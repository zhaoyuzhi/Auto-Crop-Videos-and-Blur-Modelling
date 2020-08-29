import argparse
import os
import cv2
import numpy as np
import multiprocessing

import VideoFrameConversion as vfc

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

def process_video(opt):
    # video statics
    fps, frames, time, width, height = vfc.get_video_info(opt.videopath)
    fps = round(fps)
    width = int(width)
    height = int(height)
    print("corrected video fps =", fps)
    print("corrected video width =", width)
    print("corrected video height =", height)

    # create a video writer
    fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
    print('Saving folder:', opt.savepath)
    check_path(opt.savepath)
    savepath = os.path.join(opt.savepath, opt.videopath.split('\\')[-1])
    video = cv2.VideoWriter(savepath, fourcc, fps, (opt.resize_width, opt.resize_height))

    # read a video
    vc = cv2.VideoCapture(opt.videopath)
    # whether it is truely opened
    if vc.isOpened():
        rval, frame = vc.read()
    else:
        rval = False
    print(rval)
    frame = cv2.resize(frame, (opt.resize_width, opt.resize_height))
    video.write(frame)
    c = 1
    while rval:
        print(c, frames, rval)
        rval, frame = vc.read()
        frame = cv2.resize(frame, (opt.resize_width, opt.resize_height))
        video.write(frame)
        c = c + 1
    # release the video
    vc.release()
    video.release()
    cv2.destroyAllWindows()
    print('Released!')

def process_video_temp(opt):
    # video statics
    fps, frames, time, width, height = vfc.get_video_info(opt.videopath)
    fps = round(fps)
    width = int(width)
    height = int(height)
    print("corrected video fps =", fps)
    print("corrected video width =", width)
    print("corrected video height =", height)
    
    # create a video writer
    fourcc = cv2.VideoWriter_fourcc('F', 'F', 'V', '1')
    print('Saving folder:', opt.savepath)
    check_path(opt.savepath)
    savepath = os.path.join(opt.savepath, opt.videopath.split('\\')[-1].split('.')[0] + '.mkv')
    print('Saving path:', savepath)
    video = cv2.VideoWriter(savepath, fourcc, fps, (opt.resize_width//2, opt.resize_height//2))
    
    # read a video
    vc = cv2.VideoCapture(opt.videopath)
    # whether it is truely opened
    if vc.isOpened():
        rval, frame = vc.read()
    else:
        rval = False
    print(rval)
    frame = cv2.resize(frame, (opt.resize_width, opt.resize_height))
    video.write(frame)
    c = 1
    while rval:
        print(c, frames, rval)
        rval, frame = vc.read()
        frame = cv2.resize(frame, (opt.resize_width, opt.resize_height))[:opt.resize_height//2, :opt.resize_width//2, :]
        #show = cv2.resize(frame, (frame.shape[1] // 4, frame.shape[0] // 4))
        #cv2.imshow('read video', show)
        #cv2.waitKey(1)
        video.write(frame)
        c = c + 1
    # release the video
    vc.release()
    video.release()
    cv2.destroyAllWindows()
    print('Released!')
    
def process_videos(opt):
    videolist = get_files(opt.video_folder_path)
    for i in range(len(videolist)):
        # video statics
        fps, frames, time, width, height = vfc.get_video_info(videolist[i])
        fps = round(fps)
        width = int(width)
        height = int(height)
        print("corrected video fps =", fps)
        print("corrected video width =", width)
        print("corrected video height =", height)

        # create a video writer
        fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
        print('Saving folder:', opt.savepath)
        check_path(opt.savepath)
        savepath = os.path.join(opt.savepath, opt.videopath.split('\\')[-1])
        print('Saving path:', savepath)
        video = cv2.VideoWriter(savepath, fourcc, fps, (opt.resize_width, opt.resize_height))

        # read a video
        vc = cv2.VideoCapture(opt.videopath)
        # whether it is truely opened
        if vc.isOpened():
            rval, frame = vc.read()
        else:
            rval = False
        print(rval)
        frame = cv2.resize(frame, (opt.resize_width, opt.resize_height))
        video.write(frame)
        c = 1
        while rval:
            print(c, frames, rval)
            rval, frame = vc.read()
            frame = cv2.resize(frame, (opt.resize_width, opt.resize_height))
            video.write(frame)
            c = c + 1
        # release the video
        vc.release()
        video.release()
        cv2.destroyAllWindows()
        print('Released!')

if __name__ == "__main__":

    # Define parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('--single_or_folder', type = bool, default = True, help = 'whether to use multiprocess or not')
    parser.add_argument('--resize_width', type = int, default = 5120, help = 'resize_width')
    parser.add_argument('--resize_height', type = int, default = 2880, help = 'resize_height')
    parser.add_argument('--videopath', type = str, \
        default = 'E:\\Deblur\\data collection\\3453453.webm', \
            help = 'video path')
    parser.add_argument('--video_folder_path', type = str, \
        default = 'E:\\Deblur\\data collection\\video_original', \
            help = 'video folder path')
    parser.add_argument('--savepath', type = str, \
        default = 'E:\\Deblur\\data collection\\temp', \
            help = 'save path')
    opt = parser.parse_args()
    print(opt)
    
    process_video_temp(opt)
    '''
    if opt.single_or_folder:
        process_video(opt)
    else:
        process_videos(opt)
    '''