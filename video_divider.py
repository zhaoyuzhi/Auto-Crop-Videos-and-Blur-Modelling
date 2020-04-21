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

    # time range
    if time % opt.small_video_second > 0:
        small_video_num = time // opt.small_video_second + 1
    else:
        small_video_num = time // opt.small_video_second
    small_video_num = int(small_video_num)
    print('There are %d small videos output' % (small_video_num))
    small_video_frame_num = opt.small_video_second * fps
    print('Each small video contains %d frames' % (small_video_frame_num))

    # name of small videos
    namelist = []
    for i in range(small_video_num):
        name = opt.videopath.split('\\')[-1][:-4] + '_small_' + str(i) + '.mp4'
        namelist.append(name)
    print(namelist)

    # clip small videos
    vc = cv2.VideoCapture(opt.videopath)
    for v in range(small_video_num):
        # create a video writer
        fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
        print('Saving folder:', opt.savepath)
        check_path(opt.savepath)
        savepath = os.path.join(opt.savepath, namelist[v])
        video = cv2.VideoWriter(savepath, fourcc, fps, (width, height))
        for f in range(small_video_frame_num):
            print('This is the %d-th small video, %d-th frame' % (v, f))
            rval, frame = vc.read()
            if rval == False:
                video.release()
            video.write(frame)
        video.release()
    
    # release the video
    vc.release()
    cv2.destroyAllWindows()
    print('Released!')

def process_video_by_path(opt, videopath):
    # video statics
    fps, frames, time, width, height = vfc.get_video_info(videopath)
    fps = round(fps)
    width = int(width)
    height = int(height)
    print("corrected video fps =", fps)
    print("corrected video width =", width)
    print("corrected video height =", height)

    # time range
    if time % opt.small_video_second > 0:
        small_video_num = time // opt.small_video_second + 1
    else:
        small_video_num = time // opt.small_video_second
    small_video_num = int(small_video_num)
    print('There are %d small videos output' % (small_video_num))
    small_video_frame_num = opt.small_video_second * fps
    print('Each small video contains %d frames' % (small_video_frame_num))

    # name of small videos
    namelist = []
    for i in range(small_video_num):
        name = videopath.split('\\')[-1][:-4] + '_small_' + str(i) + '.mp4'
        namelist.append(name)
    print(namelist)

    # clip small videos
    vc = cv2.VideoCapture(videopath)
    for v in range(small_video_num):
        # create a video writer
        fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
        print('Saving folder:', opt.savepath)
        check_path(opt.savepath)
        savepath = os.path.join(opt.savepath, namelist[v])
        video = cv2.VideoWriter(savepath, fourcc, fps, (width, height))
        for f in range(small_video_frame_num):
            if f % (small_video_frame_num // 10) == 0:
                print('This is the %d-th small video, %d-th frame' % (v, f))
            rval, frame = vc.read()
            if rval == False:
                video.release()
            video.write(frame)
        video.release()
    
    # release the video
    vc.release()
    cv2.destroyAllWindows()
    print('Released!')

if __name__ == "__main__":

    # Define parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('--multiprocess', type = bool, default = True, help = 'whether to use multiprocess or not')
    parser.add_argument('--small_video_second', type = int, default = 120, help = 'interval of second')
    parser.add_argument('--processes_num', type = int, default = 4, help = 'number of CPU used for processing')
    parser.add_argument('--videopath', type = str, \
        default = 'F:\\Deblur\\data collection\\video_processed_v2\\clip1\\interp_1_exposure_type_1.mp4', \
            help = 'video path')
    parser.add_argument('--video_folder_path', type = str, \
        default = 'F:\\Deblur\\data collection\\video_processed_v2\\clip5', \
            help = 'video folder path')
    parser.add_argument('--savepath', type = str, \
        default = 'F:\\Deblur\\data collection\\clip5_small_videos', \
        #default = 'F:\\Deblur\\Short-Long RGB to RGB Mapping\\data\\slrgb2rgb_v1', \
            help = 'save path')
    opt = parser.parse_args()
    print(opt)

    # Process videos
    if opt.multiprocess:

        # build video list
        videolist = get_jpgs(opt.video_folder_path)
        for i in range(len(videolist)):
            print(i, videolist[i])
        videolist = get_files(opt.video_folder_path)

        # multiprocessing
        pool = multiprocessing.Pool(processes = opt.processes_num) # create multiprocessing operator
        for i in range(len(videolist)):
            pool.apply_async(process_video_by_path, (opt, videolist[i], ))
        pool.close() # close multiprocessing operator, which represents no processes can be added
        pool.join() # wait for all processed done, which should be run after close method
        print("Sub-processes all done")

    else:
        process_video(opt)
