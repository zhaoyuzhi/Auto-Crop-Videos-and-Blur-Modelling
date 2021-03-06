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

def process_video(opt):
    # video statics
    fps, frames, time, width, height = vfc.get_video_info(opt.videopath)
    fps = round(fps)
    width = opt.resize_w
    height = opt.resize_h
    print("corrected video fps =", fps)
    print("corrected video width =", width)
    print("corrected video height =", height)
    interval_frame_list = get_statics(opt, time, fps)
    print(interval_frame_list)

    # write folder
    print('Saving folder:', opt.savepath)
    check_path(opt.savepath)

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
            if c == interval - opt.short_cut_frames - opt.long_cut_frames:
                long_exposure_img = np.zeros((height, width, 3), dtype = np.float64)
                short_exposure_img = np.zeros((height, width, 3), dtype = np.float64)
                for j in range(opt.long_cut_frames):
                    frame = cv2.resize(frame, (width, height))
                    long_exposure_img = long_exposure_img + frame.copy().astype(np.float64)
                    c = c + 1
                    cv2.waitKey(1)
                    rval, frame = vc.read()
                    if j == opt.long_cut_frames - 1:
                        imgname =  str(i) + '_' + 'long' + '.png'
                        imgpath = os.path.join(opt.savepath, imgname)
                        long_exposure_img = (long_exposure_img / opt.long_cut_frames).astype(np.uint8)
                        cv2.imwrite(imgpath, long_exposure_img)
                        print('This is the %d-th interval. Long exposure image is saved, average by %d times.' % (i + 1, opt.long_cut_frames))
                for k in range(opt.short_cut_frames):
                    frame = cv2.resize(frame, (width, height))
                    short_exposure_img = short_exposure_img + frame.copy().astype(np.float64)
                    last_frame = frame
                    c = c + 1
                    cv2.waitKey(1)
                    rval, frame = vc.read()
                    if k == opt.short_cut_frames - 1:
                        imgname =  str(i) + '_' + 'short' + '.png'
                        imgpath = os.path.join(opt.savepath, imgname)
                        short_exposure_img = (short_exposure_img / opt.short_cut_frames).astype(np.uint8)
                        cv2.imwrite(imgpath, short_exposure_img)
                        print('This is the %d-th interval. Short exposure image is saved, average by %d times.' % (i + 1, opt.short_cut_frames))
                        if opt.short_cut_frames > 1:
                            # if short_exposure_img is averaged by many frames, the gt image should be saved additionally
                            imgname =  str(i) + '_' + 'gt' + '.png'
                            imgpath = os.path.join(opt.savepath, imgname)
                            cv2.imwrite(imgpath, last_frame)
                            print('This is the %d-th interval. Ground truth image is saved.' % (i + 1))
        c = c + 1
        cv2.waitKey(1)
        rval, frame = vc.read()
    # release the video
    vc.release()
    cv2.destroyAllWindows()
    print('Finished!')

def process_videos(opt):
    videolist = get_files(opt.video_folder_path)#[6:]
    print(videolist)
    for item, videopath in enumerate(videolist):
        if item >= 4:
            opt.interval_second *= 2
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

        # create a video writer
        print('Saving folder:', opt.savepath)
        check_path(opt.savepath)
        
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
                if c == interval - opt.short_cut_frames - opt.long_cut_frames:
                    long_exposure_img = np.zeros((height, width, 3), dtype = np.float64)
                    short_exposure_img = np.zeros((height, width, 3), dtype = np.float64)
                    for j in range(opt.long_cut_frames):
                        frame = cv2.resize(frame, (width, height))
                        long_exposure_img = long_exposure_img + frame.copy().astype(np.float64)
                        c = c + 1
                        cv2.waitKey(1)
                        rval, frame = vc.read()
                        if j == opt.long_cut_frames - 1:
                            imgname =  str(item) + '_' + str(i) + '_' + 'long' + '.png'
                            imgpath = os.path.join(opt.savepath, imgname)
                            long_exposure_img = (long_exposure_img / opt.long_cut_frames).astype(np.uint8)
                            cv2.imwrite(imgpath, long_exposure_img)
                            print('This is the %d-th video %d-th interval. Long exposure image is saved, average by %d times.' % (item + 1, i + 1, opt.long_cut_frames))
                    for k in range(opt.short_cut_frames):
                        frame = cv2.resize(frame, (width, height))
                        short_exposure_img = short_exposure_img + frame.copy().astype(np.float64)
                        last_frame = frame
                        c = c + 1
                        cv2.waitKey(1)
                        rval, frame = vc.read()
                        if k == opt.short_cut_frames - 1:
                            imgname = str(item) + '_' + str(i) + '_' + 'short' + '.png'
                            imgpath = os.path.join(opt.savepath, imgname)
                            short_exposure_img = (short_exposure_img / opt.short_cut_frames).astype(np.uint8)
                            cv2.imwrite(imgpath, short_exposure_img)
                            print('This is the %d-th video %d-th interval. Short exposure image is saved, average by %d times.' % (item + 1, i + 1, opt.short_cut_frames))
                            if opt.short_cut_frames > 1:
                                # if short_exposure_img is averaged by many frames, the gt image should be saved additionally
                                imgname =  str(item) + '_' + str(i) + 'gt' + '.png'
                                imgpath = os.path.join(opt.savepath, imgname)
                                cv2.imwrite(imgpath, last_frame)
                                print('This is the %d-th interval. Ground truth image is saved.' % (i + 1))
            c = c + 1
            cv2.waitKey(1)
            rval, frame = vc.read()
        # release the video
        vc.release()
        cv2.destroyAllWindows()
        print('Finished!')
        
def process_videos_interp(opt):
    videolist = get_files(opt.video_folder_path)#[6:]
    print(videolist)
    for item, videopath in enumerate(videolist):
        if item >= 4:
            opt.interval_second *= 2
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

        # create Super Slomo network
        interp, flow, back_warp = vslomo.create_slomonet(opt)

        # create a video writer
        print('Saving folder:', opt.savepath)
        check_path(opt.savepath)
        
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
                if c == interval - opt.short_cut_frames - opt.long_cut_frames:
                    long_exposure_img = np.zeros((height, width, 3), dtype = np.float64)
                    short_exposure_img = np.zeros((height, width, 3), dtype = np.float64)
                    long_frames_for_average = []
                    short_frames_for_average = []
                    for j in range(opt.long_cut_frames):
                        last_frame = frame                          # "last_frame" saves frame from last loop
                        last_frame = cv2.resize(frame, (width, height))
                        c = c + 1
                        cv2.waitKey(1)
                        rval, frame = vc.read()
                        # interpolate between last frame and current frame
                        if j < opt.long_cut_frames - 1:
                            interp_frames = vslomo.save_inter_frames(last_frame, frame, opt, interp, flow, back_warp)
                            long_frames_for_average.append(last_frame)
                            for ji, interp_frame in enumerate(interp_frames):
                                long_frames_for_average.append(interp_frame)
                        # if it is the last frame, only save last frame
                        if j == opt.long_cut_frames - 1:
                            long_frames_for_average.append(last_frame)
                        # compute average
                        if j == opt.long_cut_frames - 1:
                            imgname =  str(item) + '_' + str(i) + '_' + 'long' + '.png'
                            imgpath = os.path.join(opt.savepath, imgname)
                            # compute average
                            for jj, long_interp_frame in enumerate(long_frames_for_average):
                                long_exposure_img = long_exposure_img + long_interp_frame.copy().astype(np.float64)
                            long_exposure_img = (long_exposure_img / len(long_frames_for_average)).astype(np.uint8)
                            cv2.imwrite(imgpath, long_exposure_img)
                            print('This is the %d-th video %d-th interval. Long exposure image is saved, average by %d times.' % (item + 1, i + 1, len(long_frames_for_average)))
                    for k in range(opt.short_cut_frames):
                        last_frame = frame                          # "last_frame" saves frame from last loop
                        last_frame = cv2.resize(frame, (width, height))
                        c = c + 1
                        cv2.waitKey(1)
                        rval, frame = vc.read()
                        # interpolate between last frame and current frame
                        if k < opt.short_cut_frames - 1:
                            interp_frames = vslomo.save_inter_frames(last_frame, frame, opt, interp, flow, back_warp)
                            short_frames_for_average.append(last_frame)
                            for ki, interp_frame in enumerate(interp_frames):
                                short_frames_for_average.append(interp_frame)
                        # if it is the last frame, only save last frame
                        if k == opt.short_cut_frames - 1:
                            short_frames_for_average.append(last_frame)
                        # compute average
                        if k == opt.short_cut_frames - 1:
                            imgname = str(item) + '_' + str(i) + '_' + 'short' + '.png'
                            imgpath = os.path.join(opt.savepath, imgname)
                            # compute average
                            for kj, short_interp_frame in enumerate(short_frames_for_average):
                                short_exposure_img = short_exposure_img + short_interp_frame.copy().astype(np.float64)
                            short_exposure_img = (short_exposure_img / len(short_frames_for_average)).astype(np.uint8)
                            cv2.imwrite(imgpath, short_exposure_img)
                            print('This is the %d-th video %d-th interval. Short exposure image is saved, average by %d times.' % (item + 1, i + 1, len(long_frames_for_average)))
                            if opt.short_cut_frames >= 1:
                                # if short_exposure_img is averaged by many frames, the gt image should be saved additionally
                                imgname =  str(item) + '_' + str(i) + '_' + 'gt' + '.png'
                                imgpath = os.path.join(opt.savepath, imgname)
                                cv2.imwrite(imgpath, last_frame)
                                print('This is the %d-th interval. Ground truth image is saved.' % (i + 1))
            c = c + 1
            cv2.waitKey(1)
            rval, frame = vc.read()
        # release the video
        vc.release()
        cv2.destroyAllWindows()
        print('Finished!')
        
def process_videos_only_gt(opt):
    videolist = get_files(opt.video_folder_path)
    print(videolist)
    for item, videopath in enumerate(videolist):
        #if item >= 6:
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

        # create a video writer
        print('Saving folder:', opt.savepath)
        check_path(opt.savepath)
        
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
                if c == interval - opt.short_cut_frames - opt.long_cut_frames:
                    for k in range(opt.short_cut_frames + opt.long_cut_frames):
                        # only left, right, and middle frames
                        # k = 9, 10, 11 are left, right, and middle position of short exposure
                        if k == 0 or k == 4 or k == 8 or k == 9 or k == 10 or k == 11:
                            gt_frame = cv2.resize(frame.copy(), (width, height))
                            add = opt.short_cut_frames + opt.long_cut_frames - k - 1
                            imgname = str(item) + '_' + str(i) + '_' + 'gt' + '_' + str(add) + '.png'
                            imgpath = os.path.join(opt.savepath, imgname)
                            cv2.imwrite(imgpath, gt_frame)
                            print('This is the %d-th video %d-th interval. %d-th GT image is saved at %d distance.' % (item + 1, i + 1, c + 1, add))
                        c = c + 1
                        cv2.waitKey(1)
                        rval, frame = vc.read()
            c = c + 1
            cv2.waitKey(1)
            rval, frame = vc.read()
        # release the video
        vc.release()
        cv2.destroyAllWindows()
        print('Finished!')
        
if __name__ == "__main__":

    # Define parameters
    parser = argparse.ArgumentParser()
    # task-independent
    parser.add_argument('--crop_range', type = int, default = 1, help = 'the time range (second) for true video clip')
    parser.add_argument('--target_range', type = int, default = 1, help = 'the time range (second) for output video clip')
    parser.add_argument('--exposure_type', type = int, default = 11, help = 'e.g. exposure_type=8 means exposure time 1/8 seconds')
    # task-related
    parser.add_argument('--interval_second', type = int, default = 5, help = 'interval of second')
    parser.add_argument('--short_cut_frames', type = int, default = 2, help = 'the frames for short exposure images')
    parser.add_argument('--long_cut_frames', type = int, default = 8, help = 'the frames for long exposure images')
    parser.add_argument('--resize_w', type = int, default = 2560, help = 'resize_w') # 3840, 2560, 1920
    parser.add_argument('--resize_h', type = int, default = 1440, help = 'resize_h') # 2160, 1440, 1080
    parser.add_argument('--only_gt', type = bool, default = False, help = 'if True, then only output GT images')
    parser.add_argument('--interp', type = bool, default = True, help = 'if True, interpolation + average images')
    parser.add_argument('--checkpoint_path', type = str, \
        default = './SuperSloMo/SuperSloMo.ckpt', \
            help = 'model weight path')
    parser.add_argument('--videopath', type = str, \
        default = 'F:\\SenseTime\\Quad-Bayer to RGB Mapping\\data\\video_original\\Moscow Russia Aerial Drone 5K Timelab.pro _ Москва Россия Аэросъемка-S_dfq9rFWAE.webm', \
            help = 'video path')
    # F:\\SenseTime\\Quad-Bayer to RGB Mapping\\data\\video_original\\Dubai in 4K - City of Gold-SLaYPmhse30.webm
    parser.add_argument('--video_folder_path', type = str, \
        default = 'F:\\Deblur\\data collection\\video_original', \
            help = 'video folder path')
    parser.add_argument('--savepath', type = str, \
        default = 'F:\\Deblur\\Short-Long RGB to RGB Mapping\\data\\slrgb2rgb_v3', \
        #default = 'F:\\Deblur\\Short-Long RGB to RGB Mapping\\data\\slrgb2rgb_v2', \
        #default = 'F:\\Deblur\\Short-Long RGB to RGB Mapping\\data\\slrgb2rgb_v1', \
            help = 'save path')
    opt = parser.parse_args()
    print(opt)

    # General information of processing folder
    videolist = get_jpgs(opt.video_folder_path)
    for i in range(len(videolist)):
        print(i, videolist[i])
    videolist = get_files(opt.video_folder_path)
    '''
    # Process videos
    if opt.only_gt:
        process_videos_only_gt(opt)
    else:
        if opt.interp:
            process_videos_interp(opt)
        else:
            process_videos(opt)
    '''