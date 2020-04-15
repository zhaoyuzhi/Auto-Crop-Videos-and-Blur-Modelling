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

def get_statics(opt, time, fps):
    interval_value = int(time / opt.interval_second)
    print('Current center interval frames equal to:', interval_value)
    interval_second_list = []
    for i in range(interval_value):
        this_interval_time = opt.interval_second * (i + 0.5)
        interval_second_list.append(this_interval_time)
    print('Time list:', interval_second_list)
    interval_frame_list = []
    for j, t in enumerate(interval_second_list):
        this_interval_frame = int(t * fps)
        interval_frame_list.append(this_interval_frame)
    print('Frame list:', interval_frame_list)
    return interval_frame_list

def get_interp_video(opt):
    # video statics
    fps, frames, time, width, height = vfc.get_video_info(opt.videopath)
    fps = round(fps)
    width = opt.resize_w
    height = opt.resize_h
    print("corrected video fps =", fps)
    print("corrected video width =", width)
    print("corrected video height =", height)
    interval_frame_list = get_statics(opt, time, fps)

    # time range
    frame_half_crop_range = int(opt.crop_range * fps / opt.exposure_type / 2)
    frame_crop_range = int(opt.crop_range * fps / opt.exposure_type)
    frame_target_range = opt.target_range * fps                 # 4 * fps, not relavant to "exposure_type"
    factor = int(opt.target_range / opt.crop_range * opt.exposure_type)
    discripancy = frame_target_range - frame_crop_range * factor
    print('In each clip, %d frames should be added' % (discripancy))

    # create a video writer
    fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
    print('Saving folder:', opt.savepath)
    check_path(opt.savepath)
    savepath = os.path.join(opt.savepath, 'temp_interp_exposure_type_' + str(opt.exposure_type) + '.mp4')
    video = cv2.VideoWriter(savepath, fourcc, fps, (width, height))

    # create Super Slomo network
    interp, flow, back_warp = vslomo.create_slomonet(opt)
    
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
        for i, interval in enumerate(interval_frame_list):
            if c == (interval - frame_half_crop_range):
                # interpolation part
                for j in range(frame_crop_range):
                    # interpolation
                    last_frame = frame                          # "last_frame" saves frame from last loop
                    last_frame = cv2.resize(last_frame, (width, height))
                    c = c + 1
                    cv2.waitKey(1)
                    rval, frame = vc.read()                     # "frame" saves frame of Current time
                    frame = cv2.resize(frame, (width, height))
                    interp_frames = vslomo.save_inter_frames(last_frame, frame, opt, interp, flow, back_warp)
                    # write frames
                    video.write(last_frame)
                    print('This is the %d-th interval. Original frame %d is saved' % (i + 1, c - 1))
                    for k, interp_frame in enumerate(interp_frames):
                        video.write(interp_frame)
                    print('This is the %d-th interval. Interpolated frames are saved %d times' % (i + 1, k + 1))
                # supplementary part
                if discripancy > 0:
                    for dis in range(discripancy):
                        video.write(interp_frame)
                    print('This is the %d-th interval. Finally %d frames are added' % (i + 1, dis + 1))
        c = c + 1
        cv2.waitKey(1)
        rval, frame = vc.read()
    # release the video
    vc.release()
    video.release()
    cv2.destroyAllWindows()
    print('Released!')

def get_moving_video(opt):
    # video statics
    fps, frames, time, width, height = vfc.get_video_info(opt.videopath)
    fps = round(fps)
    width = opt.resize_w
    height = opt.resize_h
    print("corrected video fps =", fps)
    print("corrected video width =", width)
    print("corrected video height =", height)
    interval_frame_list = get_statics(opt, time, fps)

    # time range
    frame_half_crop_range = int(opt.crop_range * fps / opt.exposure_type / 2)
    frame_crop_range = int(opt.crop_range * fps / opt.exposure_type)
    frame_target_range = opt.target_range * fps                 # 4 * fps, not relavant to "exposure_type"
    num_interp_frames = int(opt.target_range / opt.crop_range * opt.exposure_type) - 1
    last_repeat = int(num_interp_frames / 2) + 1
    current_repeat = int(num_interp_frames / 2)

    # create a video writer
    fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
    print('Saving folder:', opt.savepath)
    check_path(opt.savepath)
    savepath = os.path.join(opt.savepath, 'temp_moving_exposure_type' + str(opt.exposure_type) + '.mp4')
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
        for i, interval in enumerate(interval_frame_list):
            if c == (interval - frame_half_crop_range):
                # interpolation part
                for j in range(frame_crop_range):
                    # interpolation
                    last_frame = frame                          # "last_frame" saves frame from last loop
                    last_frame = cv2.resize(last_frame, (width, height))
                    c = c + 1
                    cv2.waitKey(1)
                    rval, frame = vc.read()                     # "frame" saves frame of Current time
                    frame = cv2.resize(frame, (width, height))
                    # write frames
                    video.write(last_frame)
                    print('This is the %d-th interval. Original frame %d is saved' % (i + 1, c - 1))
                    for m in range(last_repeat):
                        video.write(last_frame)
                    if current_repeat > 0:
                        for n in range(current_repeat):
                            video.write(frame)
                    print('This is the %d-th interval. Interpolated frames are saved %d times' % (i + 1, num_interp_frames))
        c = c + 1
        cv2.waitKey(1)
        rval, frame = vc.read()
    # release the video
    vc.release()
    video.release()
    cv2.destroyAllWindows()
    print('Released!')

def get_static_video(opt):
    # video statics
    fps, frames, time, width, height = vfc.get_video_info(opt.videopath)
    fps = round(fps)
    width = opt.resize_w
    height = opt.resize_h
    print("corrected video fps =", fps)
    print("corrected video width =", width)
    print("corrected video height =", height)
    interval_frame_list = get_statics(opt, time, fps)

    # time range
    #frame_half_crop_range = int(opt.crop_range * fps / 2)
    frame_target_range = opt.target_range * fps

    # create a video writer
    fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
    print('Saving folder:', opt.savepath)
    check_path(opt.savepath)
    savepath = os.path.join(opt.savepath, 'temp_static.mp4')
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
        for i, interval in enumerate(interval_frame_list):
            if c == interval:
                for j in range(frame_target_range):
                    frame = cv2.resize(frame, (width, height))
                    video.write(frame)
                    if j == frame_target_range - 1:
                        print('This is the %d-th interval. Original frame %d is saved, repeat time %d' % (i + 1, c, j + 1))
        c = c + 1
        cv2.waitKey(1)
        rval, frame = vc.read()
    # release the video
    vc.release()
    video.release()
    cv2.destroyAllWindows()
    print('Released!')

def get_interp_videos(opt):
    videolist = get_files(opt.video_folder_path)[opt.addition:]
    print(videolist)
    for item, videopath in enumerate(videolist):
        # video statics
        fps, frames, time, width, height = vfc.get_video_info(videopath)
        fps = round(fps)
        width = opt.resize_w
        height = opt.resize_h
        print("corrected video fps =", fps)
        print("corrected video width =", width)
        print("corrected video height =", height)
        interval_frame_list = get_statics(opt, time, fps)

        # time range
        frame_half_crop_range = int(opt.crop_range * fps / opt.exposure_type / 2)
        frame_crop_range = int(opt.crop_range * fps / opt.exposure_type)
        frame_target_range = opt.target_range * fps                 # 4 * fps, not relavant to "exposure_type"
        factor = int(opt.target_range / opt.crop_range * opt.exposure_type)
        discripancy = frame_target_range - frame_crop_range * factor
        print('In each clip, %d frames should be added' % (discripancy))

        # create a video writer
        fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
        print('Saving folder:', opt.savepath)
        check_path(opt.savepath)
        savepath = os.path.join(opt.savepath, 'interp_' + str(item + opt.addition) + '_exposure_type_' + str(opt.exposure_type) + '.mp4')
        video = cv2.VideoWriter(savepath, fourcc, fps, (width, height))

        # create Super Slomo network
        interp, flow, back_warp = vslomo.create_slomonet(opt)
        
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
            for i, interval in enumerate(interval_frame_list):
                if c == (interval - frame_half_crop_range):
                    # interpolation part
                    for j in range(frame_crop_range):
                        # interpolation
                        last_frame = frame                          # "last_frame" saves frame from last loop
                        last_frame = cv2.resize(last_frame, (width, height))
                        c = c + 1
                        cv2.waitKey(1)
                        rval, frame = vc.read()                     # "frame" saves frame of Current time
                        if frame is None:
                            frame = last_frame
                        frame = cv2.resize(frame, (width, height))
                        interp_frames = vslomo.save_inter_frames(last_frame, frame, opt, interp, flow, back_warp)
                        # write frames
                        video.write(last_frame)
                        print('This is the %d-th video %d-th interval. Original frame %d is saved' % (item + opt.addition + 1, i + 1, c - 1))
                        for k, interp_frame in enumerate(interp_frames):
                            video.write(interp_frame)
                        print('This is the %d-th video %d-th interval. Interpolated frames are saved %d times' % (item + opt.addition + 1, i + 1, k + 1))
                    # supplementary part
                    if discripancy > 0:
                        for dis in range(discripancy):
                            video.write(interp_frame)
                        print('This is the %d-th video %d-th interval. Finally %d frames are added' % (item + opt.addition + 1, i + 1, dis + 1))
            c = c + 1
            cv2.waitKey(1)
            rval, frame = vc.read()
        # release the video
        vc.release()
        video.release()
        cv2.destroyAllWindows()
        print('Released!')

def get_static_videos(opt):
    videolist = get_files(opt.video_folder_path)
    print(videolist)
    for item, videopath in enumerate(videolist):
        # video statics
        print('Now it is the %d-th video with name %s' % (item, videopath))
        fps, frames, time, width, height = vfc.get_video_info(videopath)
        fps = round(fps)
        width = opt.resize_w
        height = opt.resize_h
        print("corrected video fps =", fps)
        print("corrected video width =", width)
        print("corrected video height =", height)
        interval_frame_list = get_statics(opt, time, fps)

        # time range
        #frame_half_crop_range = int(opt.crop_range * fps / 2)
        frame_target_range = opt.target_range * fps

        # create a video writer
        fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
        print('Saving folder:', opt.savepath)
        check_path(opt.savepath)
        savepath = os.path.join(opt.savepath, 'static_' + str(item) + '.mp4')
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
            for i, interval in enumerate(interval_frame_list):
                if c == interval:
                    for j in range(frame_target_range):
                        frame = cv2.resize(frame, (width, height))
                        video.write(frame)
                        if j == frame_target_range - 1:
                            print('This is the %d-th video %d-th interval. Original frame %d is saved, repeat time %d' % (item + 1, i + 1, c, j + 1))
            c = c + 1
            cv2.waitKey(1)
            rval, frame = vc.read()
        # release the video
        vc.release()
        video.release()
        cv2.destroyAllWindows()
        print('Released!')
        
if __name__ == "__main__":

    # Define parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('--static_or_exposure', type = bool, default = False, help = 'True for static output; False for interp output')
    parser.add_argument('--interval_second', type = int, default = 10, help = 'interval of second')
    parser.add_argument('--crop_range', type = int, default = 2, help = 'the time range (second) for true video clip')
    parser.add_argument('--target_range', type = int, default = 4, help = 'the time range (second) for output video clip')
    parser.add_argument('--exposure_type', type = int, default = 1, help = 'e.g. exposure_type=8 means exposure time 1/8 seconds')
    parser.add_argument('--resize_w', type = int, default = 3840, help = 'resize_w') # 3840, 1920
    parser.add_argument('--resize_h', type = int, default = 2160, help = 'resize_h') # 2160, 1080
    parser.add_argument('--addition', type = int, default = 6, help = 'addition')
    parser.add_argument('--checkpoint_path', type = str, \
        default = './SuperSloMo/SuperSloMo.ckpt', \
            help = 'model weight path')
    parser.add_argument('--videopath', type = str, \
        default = 'F:\\SenseTime\\Quad-Bayer to RGB Mapping\\data\\video_original\\Moscow Russia Aerial Drone 5K Timelab.pro _ Москва Россия Аэросъемка-S_dfq9rFWAE.webm', \
            help = 'video path')
    # F:\\SenseTime\\Quad-Bayer to RGB Mapping\\data\\video_original\\Dubai in 4K - City of Gold-SLaYPmhse30.webm
    parser.add_argument('--video_folder_path', type = str, \
        default = 'F:\\SenseTime\\Quad-Bayer to RGB Mapping\\data\\video_original', \
            help = 'video folder path')
    parser.add_argument('--savepath', type = str, \
        default = 'F:\\SenseTime\\Quad-Bayer to RGB Mapping\\data\\video_processed_v2', \
            help = 'save path')
    opt = parser.parse_args()
    print(opt)

    # General information of processing folder
    videolist = get_jpgs(opt.video_folder_path)
    for i in range(len(videolist)):
        print(i, videolist[i])
    videolist = get_files(opt.video_folder_path)

    # Process videos
    '''
    if opt.static_or_exposure:
        get_static_videos(opt)
    else:
    '''
    get_interp_videos(opt)
