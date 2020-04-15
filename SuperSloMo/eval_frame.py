"""
Interpolate frames from two frames using SuperSloMo version
"""
import argparse
from time import time
import os
import click
import cv2
import torch
from PIL import Image
import numpy as np
import model
from torchvision import transforms
from torch.functional import F


torch.set_grad_enabled(False)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

trans_forward = transforms.ToTensor()
trans_backward = transforms.ToPILImage()
if device != "cpu":
    mean = [0.429, 0.431, 0.397]
    mea0 = [-m for m in mean]
    std = [1] * 3
    trans_forward = transforms.Compose([trans_forward, transforms.Normalize(mean=mean, std=std)])
    trans_backward = transforms.Compose([transforms.Normalize(mean=mea0, std=std), trans_backward])

flow = model.UNet(6, 4).to(device)
interp = model.UNet(20, 5).to(device)
back_warp = None


def setup_back_warp(w, h):
    global back_warp
    with torch.set_grad_enabled(False):
        back_warp = model.backWarp(w, h, device).to(device)


def load_models(checkpoint):
    states = torch.load(checkpoint, map_location='cpu')
    interp.load_state_dict(states['state_dictAT'])
    flow.load_state_dict(states['state_dictFC'])


def interpolate_batch(frames, factor):

    frame0 = torch.stack(frames[:-1])
    frame1 = torch.stack(frames[1:])

    i0 = frame0.to(device)
    i1 = frame1.to(device)
    ix = torch.cat([i0, i1], dim=1)

    flow_out = flow(ix)
    f01 = flow_out[:, :2, :, :]
    f10 = flow_out[:, 2:, :, :]

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
        io = interp(iy)

        ft0f = io[:, :2, :, :] + ft0
        ft1f = io[:, 2:4, :, :] + ft1
        vt0 = F.sigmoid(io[:, 4:5, :, :])
        vt1 = 1 - vt0

        gi0ft0f = back_warp(i0, ft0f)
        gi1ft1f = back_warp(i1, ft1f)

        co_eff = [1 - t, t]

        ft_p = (co_eff[0] * vt0 * gi0ft0f + co_eff[1] * vt1 * gi1ft1f) / \
               (co_eff[0] * vt0 + co_eff[1] * vt1)

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
    return np.array(frame)[:, :, ::-1].copy()


def save_inter_frames(first_frame, second_frame, factor, dest):

    first_frame = cv2.imread(first_frame)
    second_frame = cv2.imread(second_frame)

    h0 = first_frame.shape[0]
    w0 = first_frame.shape[1]
    
    w, h = (w0 // 32) * 32, (h0 // 32) * 32
    setup_back_warp(w, h)

    batch = load_batch(first_frame, second_frame, w, h)
    intermediate_frames = interpolate_batch(batch, factor)

    #intermediate_frames = list(zip(*intermediate_frames))
    for fid, iframe in enumerate(intermediate_frames):
        print(iframe.shape)
        for frm in iframe:
            f = denorm_frame(frm, w0, h0)
            cv2.imwrite('%d.jpg' % fid, f)

def check_path(path):
    if not os.path.exists(path):
        os.mkdir(path)
    
'''
@click.command('Evaluate Model by converting a low-FPS video to high-fps')
@click.argument('input')
@click.option('--checkpoint', help='Path to model checkpoint')
@click.option('--output', help='Path to output file to save')
@click.option('--first_frame', default=2, help='path')
@click.option('--second_frame', default=30, help='path')
@click.option('--scale', default=4, help='Scale Factor of FPS')
'''
def main_frame(checkpoint, first_frame, second_frame, scale, output):
    load_models(checkpoint)
    save_inter_frames(first_frame, second_frame, scale, output)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint', type = str, default = './SuperSloMo.ckpt', help = 'root for model')
    parser.add_argument('--first_frame', type = str, default = './test_sample/00000.jpg', help = 'first frame')
    parser.add_argument('--second_frame', type = str, default = './test_sample/00001.jpg', help = 'second frame')
    parser.add_argument('--scale', type = int, default = 4, help = 'interpolate num')
    parser.add_argument('--output', type = str, default = '', help = 'output dir')
    opt = parser.parse_args()
    
    main_frame(checkpoint = opt.checkpoint, \
    first_frame = opt.first_frame, \
    second_frame = opt.second_frame, \
    scale = opt.scale, output = opt.output)
