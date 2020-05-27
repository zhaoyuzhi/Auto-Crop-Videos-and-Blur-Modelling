import argparse
import os
import cv2
import numpy as np

import VideoFrameConversion as vfc
import SuperSloMo as vslomo

def get_files(path):
    # read a folder, return the complete path
    ret = []
    for root, dirs, files in os.walk(path):
        for filespath in files:
            ret.append(os.path.join(root, filespath))
    return ret

def get_jpgs(path):
    # read a folder, return the image name
    ret = []
    for root, dirs, files in os.walk(path):
        for filespath in files:
            ret.append(filespath)
    return ret

def text_save(content, filename, mode = 'a'):
    # save a list to a txt
    # Try to save a list variable in txt file.
    file = open(filename, mode)
    for i in range(len(content)):
        file.write(str(content[i]) + '\n')
    file.close()

def check_path(path):
    if not os.path.exists(path):
        os.makedirs(path)

def get_interp_video(opt):
    print(opt.videopath)
    fps, frames, time, width, height = vfc.get_video_info(opt.videopath)
    fps = opt.fps
    width = opt.resize_w
    height = opt.resize_h
    print("corrected video fps =", fps)
    print("corrected video width =", width)
    print("corrected video height =", height)

    # create a video writer
    fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
    print('Saving folder:', opt.savepath)
    check_path(opt.savepath)
    savepath = os.path.join(opt.savepath, opt.videopath.split('/')[-1] + '_processed.mp4')
    video = cv2.VideoWriter(savepath, fourcc, fps, (width, height))
    
    # read and write
    vc = cv2.VideoCapture(opt.videopath)
    # whether it is truely opened
    if vc.isOpened():
        rval, frame = vc.read()
    else:
        rval = False
    print(rval)
    # save frames
    c = 1
    while rval:
        # interpolation
        frame = cv2.resize(frame, (width, height))
        video.write(frame)
        c = c + 1
        cv2.waitKey(1)
        rval, frame = vc.read()                     # "frame" saves frame of Current time
        print('This is %d-th interval.' % (c))
    # release the video
    vc.release()
    video.release()
    cv2.destroyAllWindows()
    print('Released!')

def get_interp_videos(opt):
    videolist = get_files(opt.video_folder_path)
    print(videolist)
    for item, videopath in enumerate(videolist):
        # video statics
        #fps, frames, time, width, height = vfc.get_video_info(videopath)
        fps = opt.fps
        width = opt.resize_w
        height = opt.resize_h
        print("corrected video fps =", fps)
        print("corrected video width =", width)
        print("corrected video height =", height)

        # create a video writer
        fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
        print('Saving folder:', opt.savepath)
        check_path(opt.savepath)
        savepath = os.path.join(opt.savepath, videopath.split('/')[-1][:-5] + '.mp4')
        video = cv2.VideoWriter(savepath, fourcc, fps, (width, height))

        # read and write
        vc = cv2.VideoCapture(videopath)
        # whether it is truely opened
        if vc.isOpened():
            rval, frame = vc.read()
        else:
            rval = False
        print(rval)
        # save frames
        c = 1
        while rval:
            # interpolation
            frame = cv2.resize(frame, (width, height))
            video.write(frame)
            c = c + 1
            cv2.waitKey(1)
            rval, frame = vc.read()                     # "frame" saves frame of Current time
            print('This is %d-th video %d-th interval.' % (item + 1, c))
        # release the video
        vc.release()
        video.release()
        cv2.destroyAllWindows()
        print('Released!')

if __name__ == "__main__":

    # Define parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('--fps', type = int, default = 30, help = 'fps')
    parser.add_argument('--resize_w', type = int, default = 2560, help = 'resize_w') # 3840, 1920
    parser.add_argument('--resize_h', type = int, default = 1440, help = 'resize_h') # 2160, 1080
    parser.add_argument('--videopath', type = str, \
        default = 'E:\\Deblur\\data collection\\video_original\\Moscow Russia Aerial Drone 5K Timelab.pro _ Москва Россия Аэросъемка-S_dfq9rFWAE.webm', \
            help = 'video path')
    # F:\\SenseTime\\Quad-Bayer to RGB Mapping\\data\\video_original\\Dubai in 4K - City of Gold-SLaYPmhse30.webm
    parser.add_argument('--video_folder_path', type = str, \
        default = 'E:\\Deblur\\data collection\\video_original', \
            help = 'video folder path')
    parser.add_argument('--savepath', type = str, \
        default = 'E:\\Deblur\\data collection\\video_fps30_resized', \
            help = 'save path')
    opt = parser.parse_args()
    print(opt)
    
    # Process videos
    get_interp_videos(opt)
