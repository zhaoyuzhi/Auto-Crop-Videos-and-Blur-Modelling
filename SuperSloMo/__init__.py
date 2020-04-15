import os
import torch
import numpy as np
import cv2
from PIL import Image
from torchvision import transforms
from torch.functional import F

from .model import *

torch.set_grad_enabled(False)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

trans_forward = transforms.ToTensor()
trans_backward = transforms.ToPILImage()
if device != "cpu":
    mean = [0.429, 0.431, 0.397]
    mea0 = [-m for m in mean]
    std = [1] * 3
    trans_forward = transforms.Compose([trans_forward, transforms.Normalize(mean = mean, std = std)])
    trans_backward = transforms.Compose([transforms.Normalize(mean = mea0, std = std), trans_backward])

def interpolate_batch(frames, factor, interp, flow, back_warp):
    # Stack input frames
    frame0 = torch.stack(frames[:-1])
    frame1 = torch.stack(frames[1:])
    # To device
    i0 = frame0.to(device)
    i1 = frame1.to(device)
    ix = torch.cat([i0, i1], dim=1)
    # Compute optical flows
    with torch.no_grad():
        flow_out = flow(ix)
    f01 = flow_out[:, :2, :, :]
    f10 = flow_out[:, 2:, :, :]
    # Processing
    frame_buffer = []
    for i in range(1, factor):
        t = i / factor
        temp = -t * (1 - t)
        co_eff = [temp, t * t, (1 - t) * (1 - t), temp]
        ft0 = co_eff[0] * f01 + co_eff[1] * f10
        ft1 = co_eff[2] * f01 + co_eff[3] * f10
        gi0ft0 = back_warp(i0, ft0)
        gi1ft1 = back_warp(i1, ft1)
        iy = torch.cat((i0, i1, f01, f10, ft1, ft0, gi1ft1, gi0ft0), dim=1)
        with torch.no_grad():
            io = interp(iy)
        ft0f = io[:, :2, :, :] + ft0
        ft1f = io[:, 2:4, :, :] + ft1
        vt0 = F.sigmoid(io[:, 4:5, :, :])
        vt1 = 1 - vt0
        gi0ft0f = back_warp(i0, ft0f)
        gi1ft1f = back_warp(i1, ft1f)
        co_eff = [1 - t, t]
        ft_p = (co_eff[0] * vt0 * gi0ft0f + co_eff[1] * vt1 * gi1ft1f) / (co_eff[0] * vt0 + co_eff[1] * vt1)
        frame_buffer.append(ft_p)
    return frame_buffer

def load_batch(first_frame, second_frame, w, h):
    batch = []
    for frame in (first_frame, second_frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = Image.fromarray(frame)
        frame = frame.resize((w, h), Image.ANTIALIAS)
        frame = frame.convert('RGB')
        frame = trans_forward(frame)
        batch.append(frame)
    return batch

def denorm_frame(frame, w0, h0):
    frame = frame.cpu()
    frame = trans_backward(frame)
    frame = frame.resize((w0, h0), Image.BILINEAR)
    frame = frame.convert('RGB')
    frame = np.array(frame)[:, :, ::-1].copy()
    return frame

def create_slomonet(opt):
    # Set networks
    interp = UNet(20, 5).cuda()
    flow = UNet(6, 4).cuda()
    states = torch.load(opt.checkpoint_path, map_location = 'cpu')
    interp.load_state_dict(states['state_dictAT'])
    flow.load_state_dict(states['state_dictFC'])
    for param in interp.parameters():
        param.requires_grad = False
    for param in flow.parameters():
        param.requires_grad = False
    # Set back_warp
    w, h = (opt.resize_w // 32) * 32, (opt.resize_h // 32) * 32
    with torch.set_grad_enabled(False):
        back_warp = backWarp(w, h, device).cuda()
    return interp, flow, back_warp

def save_inter_frames(first_frame, second_frame, opt, interp, flow, back_warp):
    #-----------------------------------------------------------------------------------
    # The input "first_frame" and "second_frame" should be resized cv2 image format
    # The width = opt.resize_w and height = opt.resize_h
    # The image are formed as (H, W, C)
    #first_frame = cv2.imread(first_frame)
    #second_frame = cv2.imread(second_frame)
    #first_frame = cv2.resize(first_frame, (resize_w, resize_h))
    #second_frame = cv2.resize(second_frame, (resize_w, resize_h))
    #h0 = first_frame.shape[0]
    #w0 = first_frame.shape[1]
    #-----------------------------------------------------------------------------------
    # Compute mesh w/h and interpolation factor
    # e.g. we need to interpolate frames to 2 seconds video to 4 seconds video, exposure time = 1, the factor = 4 / 2 * 1 = 2
    # e.g. we need to interpolate frames to 2 seconds video to 4 seconds video, exposure time = 8, the factor = 4 / 2 * 8 = 16
    # if factor = 16, the network will interpolate 15 frames between first_frame and second_frame
    w, h = (opt.resize_w // 32) * 32, (opt.resize_h // 32) * 32
    factor = int(opt.target_range / opt.crop_range * opt.exposure_type)
    # Processing
    batch = load_batch(first_frame, second_frame, w, h)
    intermediate_frames = interpolate_batch(batch, factor, interp, flow, back_warp)
    # Return intermediate frames
    interp_frames = []
    for fid, iframe in enumerate(intermediate_frames):
        for frm in iframe:
            f = denorm_frame(frm, opt.resize_w, opt.resize_h)
            interp_frames.append(f)
    return interp_frames

def check_path(path):
    if not os.path.exists(path):
        os.mkdir(path)

if __name__ == "__main__":

    import argparse
    # Define parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval_second', type = int, default = 10, help = 'interval of second')
    parser.add_argument('--crop_range', type = int, default = 2, help = 'the time range (second) for true video clip')
    parser.add_argument('--target_range', type = int, default = 4, help = 'the time range (second) for output video clip')
    parser.add_argument('--exposure_type', type = int, default = 8, help = 'e.g. exposure_type=8 means exposure time 1/8 seconds')
    parser.add_argument('--resize_w', type = int, default = 1920, help = 'resize_w') # 3840
    parser.add_argument('--resize_h', type = int, default = 1030, help = 'resize_h') # 2160
    parser.add_argument('--checkpoint_path', type = str, \
        default = './SuperSloMo.ckpt', \
            help = 'model weight path')
    parser.add_argument('--videopath', type = str, \
        default = './sample.mp4', \
            help = 'video path')
    # F:\\SenseTime\\Quad-Bayer to RGB Mapping\\data\\video_original\\Dubai in 4K - City of Gold-SLaYPmhse30.webm
    parser.add_argument('--video_folder_path', type = str, \
        default = 'F:\\SenseTime\\Quad-Bayer to RGB Mapping\\data\\video_original', \
            help = 'video folder path')
    parser.add_argument('--savepath', type = str, \
        default = './test_result', \
            help = 'save path')
    opt = parser.parse_args()
    print(opt)

    check_path(opt.savepath)

    interp, flow, back_warp = vslomo.create_slomonet(opt)
    first_frame = cv2.imread('./test_sample/00000.jpg')
    second_frame = cv2.imread('./test_sample/00010.jpg')
    first_frame = cv2.resize(first_frame, (opt.resize_w, opt.resize_h))
    second_frame = cv2.resize(second_frame, (opt.resize_w, opt.resize_h))
    interp_frames = save_inter_frames(first_frame, second_frame, opt, interp, flow, back_warp)
    print(len(interp_frames))

    for i, frame in enumerate(interp_frames):
        print('The %d-th frame with size:' % (i), frame.shape)
        imgname = str(i) + '.jpg'
        imgpath = os.path.join(opt.savepath, imgname)
        cv2.imwrite(imgpath, frame)
