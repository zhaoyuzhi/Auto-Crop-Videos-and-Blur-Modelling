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

    # frame number of current video
    frame_num_base = 1000.0 / fps # 原视频1帧有多少 ms长
    print('frame_num_base:', frame_num_base)
    frame_num_base = frame_num_base / opt.exposure_type # interp后的视频1帧有多少 ms长, e.g. 1000 / 30 / 16 = 2
    short_frame_num = round(opt.short_cut_ms / frame_num_base) # e.g. 10 / 2 = 5
    long1_frame_num = round(opt.long1_cut_ms / frame_num_base) # e.g. 80 / 2 = 40 帧
    long2_frame_num = round(opt.long2_cut_ms / frame_num_base) # e.g. 60 / 2 = 30 帧
    long3_frame_num = round(opt.long3_cut_ms / frame_num_base) # e.g. 40 / 2 = 20 帧
    long4_frame_num = round(opt.long4_cut_ms / frame_num_base) # e.g. 20 / 2 = 10 帧
    interval_num = round(opt.interval_cut_ms / frame_num_base) # e.g. 35 / 2 = 17 帧
    print('frame_num_base:', frame_num_base)
    print('short_frame_num:', short_frame_num)
    print('long1_frame_num:', long1_frame_num)
    print('long2_frame_num:', long2_frame_num)
    print('long3_frame_num:', long3_frame_num)
    print('long4_frame_num:', long4_frame_num)
    print('interval_num:', interval_num)

    # write folder
    print('Saving folder:', opt.savepath)
    check_path(opt.savepath)
    
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
            if c == interval - opt.long_cut_frames - opt.short_cut_frames: # 1 for short exposure, and 2 for long exposure
                long1_exposure_img = np.zeros((height, width, 3), dtype = np.float64)
                long2_exposure_img = np.zeros((height, width, 3), dtype = np.float64)
                long3_exposure_img = np.zeros((height, width, 3), dtype = np.float64)
                long4_exposure_img = np.zeros((height, width, 3), dtype = np.float64)
                short_exposure_img = np.zeros((height, width, 3), dtype = np.float64)
                imglist = []
                for j in range(opt.long_cut_frames + opt.short_cut_frames):
                    frame = cv2.resize(frame, (width, height))
                    imglist.append(frame.copy().astype(np.float64))
                    last_frame = frame
                    c = c + 1
                    cv2.waitKey(1)
                    rval, frame = vc.read()
                    if frame is None:
                        frame = last_frame
                    frame = cv2.resize(frame, (width, height))
                    # seperate images [h, w, c]
                    last_frame1 = last_frame[:height//2, :width//2, :]
                    last_frame2 = last_frame[height//2:height, :width//2, :]
                    last_frame3 = last_frame[:height//2, width//2:width, :]
                    last_frame4 = last_frame[height//2:height, width//2:width, :]
                    frame1 = frame[:height//2, :width//2, :]
                    frame2 = frame[height//2:height, :width//2, :]
                    frame3 = frame[:height//2, width//2:width, :]
                    frame4 = frame[height//2:height, width//2:width, :]
                    # interpolate respectively
                    interp_frames1 = vslomo.save_inter_frames(last_frame1, frame1, opt, interp, flow, back_warp)
                    interp_frames2 = vslomo.save_inter_frames(last_frame2, frame2, opt, interp, flow, back_warp)
                    interp_frames3 = vslomo.save_inter_frames(last_frame3, frame3, opt, interp, flow, back_warp)
                    interp_frames4 = vslomo.save_inter_frames(last_frame4, frame4, opt, interp, flow, back_warp)
                    for k in range(len(interp_frames1)):
                        patch1 = interp_frames1[k]
                        patch2 = interp_frames2[k]
                        patch3 = interp_frames3[k]
                        patch4 = interp_frames4[k]
                        temp1 = np.concatenate((patch1, patch2), axis = 0)
                        temp2 = np.concatenate((patch3, patch4), axis = 0)
                        interp_frame = np.concatenate((temp1, temp2), axis = 1)
                        imglist.append(interp_frame.astype(np.float64))
                # average
                len_imglist = len(imglist) # 4 * 16 = 64
                print('len_imglist:', len_imglist)
                a1 = 0
                a2 = 0
                a3 = 0
                a4 = 0
                for p, img in enumerate(imglist):
                    if p >= (len_imglist - long1_frame_num - interval_num - 1) and p < (len_imglist - interval_num - 1): # 6 ~ 46
                        long1_exposure_img = long1_exposure_img + img
                        a1 = a1 + 1
                long1_exposure_img = (long1_exposure_img / a1).astype(np.uint8)
                for p, img in enumerate(imglist):
                    if p >= (len_imglist - long2_frame_num - interval_num - 1) and p < (len_imglist - interval_num - 1): # 6 ~ 46
                        long2_exposure_img = long2_exposure_img + img
                        a2 = a2 + 1
                long2_exposure_img = (long2_exposure_img / a2).astype(np.uint8)
                for p, img in enumerate(imglist):
                    if p >= (len_imglist - long3_frame_num - interval_num - 1) and p < (len_imglist - interval_num - 1): # 6 ~ 46
                        long3_exposure_img = long3_exposure_img + img
                        a3 = a3 + 1
                long3_exposure_img = (long3_exposure_img / a3).astype(np.uint8)
                for p, img in enumerate(imglist):
                    if p >= (len_imglist - long4_frame_num - interval_num - 1) and p < (len_imglist - interval_num - 1): # 6 ~ 46
                        long4_exposure_img = long4_exposure_img + img
                        a4 = a4 + 1
                long4_exposure_img = (long4_exposure_img / a4).astype(np.uint8)
                short_exposure_img = (imglist[-1]).astype(np.uint8)
                # save
                imgpath = os.path.join(opt.savepath, opt.atr + '_' + str(i) + '_' + 'long8.png')
                cv2.imwrite(imgpath, long1_exposure_img)
                imgpath = os.path.join(opt.savepath, opt.atr + '_' + str(i) + '_' + 'long6.png')
                cv2.imwrite(imgpath, long2_exposure_img)
                imgpath = os.path.join(opt.savepath, opt.atr + '_' + str(i) + '_' + 'long4.png')
                cv2.imwrite(imgpath, long3_exposure_img)
                imgpath = os.path.join(opt.savepath, opt.atr + '_' + str(i) + '_' + 'long2.png')
                cv2.imwrite(imgpath, long4_exposure_img)
                imgpath = os.path.join(opt.savepath, opt.atr + '_' + str(i) + '_' + 'short.png')
                cv2.imwrite(imgpath, short_exposure_img)
                print('Long1: %d frames averaged. Long2: %d frames averaged.' % (a1, a2))
                print('This is the %d-th video %d-th interval.' % (item + 1, i + 1))
        c = c + 1
        cv2.waitKey(1)
        rval, frame = vc.read()
    # release the video
    vc.release()
    cv2.destroyAllWindows()
    print('Finished!')

def process_videos(opt):
    videolist = get_files(opt.video_folder_path)
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
        print(interval_frame_list)

        # frame number of current video
        frame_num_base = 1000.0 / fps # 原视频1帧有多少 ms长
        print('frame_num_base:', frame_num_base)
        frame_num_base = frame_num_base / opt.exposure_type # interp后的视频1帧有多少 ms长, e.g. 1000 / 30 / 16 = 2
        short_frame_num = round(opt.short_cut_ms / frame_num_base) # e.g. 10 / 2 = 5
        long1_frame_num = round(opt.long1_cut_ms / frame_num_base) # e.g. 80 / 2 = 40 帧
        long2_frame_num = round(opt.long2_cut_ms / frame_num_base) # e.g. 60 / 2 = 30 帧
        long3_frame_num = round(opt.long3_cut_ms / frame_num_base) # e.g. 40 / 2 = 20 帧
        long4_frame_num = round(opt.long4_cut_ms / frame_num_base) # e.g. 20 / 2 = 10 帧
        interval_num = round(opt.interval_cut_ms / frame_num_base) # e.g. 35 / 2 = 17 帧
        print('frame_num_base:', frame_num_base)
        print('short_frame_num:', short_frame_num)
        print('long1_frame_num:', long1_frame_num)
        print('long2_frame_num:', long2_frame_num)
        print('long3_frame_num:', long3_frame_num)
        print('long4_frame_num:', long4_frame_num)
        print('interval_num:', interval_num)

        # write folder
        print('Saving folder:', opt.savepath)
        check_path(opt.savepath)
        
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
                if c == interval - opt.long_cut_frames - opt.short_cut_frames: # 1 for short exposure, and 2 for long exposure
                    long1_exposure_img = np.zeros((height, width, 3), dtype = np.float64)
                    long2_exposure_img = np.zeros((height, width, 3), dtype = np.float64)
                    long3_exposure_img = np.zeros((height, width, 3), dtype = np.float64)
                    long4_exposure_img = np.zeros((height, width, 3), dtype = np.float64)
                    short_exposure_img = np.zeros((height, width, 3), dtype = np.float64)
                    long_last_exposure_img = np.zeros((height, width, 3), dtype = np.uint8)
                    imglist = []
                    for j in range(opt.long_cut_frames + opt.short_cut_frames):
                        frame = cv2.resize(frame, (width, height))[:height//2, :width//2, :]
                        last_frame = frame
                        imglist.append(frame.copy().astype(np.float64))
                        c = c + 1
                        cv2.waitKey(1)
                        rval, frame = vc.read()
                        if frame is None:
                            frame = last_frame
                        frame = cv2.resize(frame, (width, height))[:height//2, :width//2, :]
                        # seperate images [h, w, c]
                        interp_frames = vslomo.save_inter_frames(last_frame, frame, opt, interp, flow, back_warp)
                        for k, interp_frame in enumerate(interp_frames):
                            imglist.append(interp_frame.astype(np.float64))
                    # average
                    len_imglist = len(imglist) # 4 * 16 = 64
                    print('len_imglist:', len_imglist)
                    a1 = 0
                    a2 = 0
                    a3 = 0
                    a4 = 0
                    for p, img in enumerate(imglist):
                        if p >= (len_imglist - long1_frame_num - interval_num - 1) and p < (len_imglist - interval_num - 1): # 6 ~ 46
                            long1_exposure_img = long1_exposure_img + img
                            a1 = a1 + 1
                    long1_exposure_img = (long1_exposure_img / a1).astype(np.uint8)
                    for p, img in enumerate(imglist):
                        if p >= (len_imglist - long2_frame_num - interval_num - 1) and p < (len_imglist - interval_num - 1): # 6 ~ 46
                            long2_exposure_img = long2_exposure_img + img
                            a2 = a2 + 1
                    long2_exposure_img = (long2_exposure_img / a2).astype(np.uint8)
                    for p, img in enumerate(imglist):
                        if p >= (len_imglist - long3_frame_num - interval_num - 1) and p < (len_imglist - interval_num - 1): # 6 ~ 46
                            long3_exposure_img = long3_exposure_img + img
                            a3 = a3 + 1
                    long3_exposure_img = (long3_exposure_img / a3).astype(np.uint8)
                    for p, img in enumerate(imglist):
                        if p >= (len_imglist - long4_frame_num - interval_num - 1) and p < (len_imglist - interval_num - 1): # 6 ~ 46
                            long4_exposure_img = long4_exposure_img + img
                            a4 = a4 + 1
                            long_last_exposure_img = img.astype(np.uint8)
                    long4_exposure_img = (long4_exposure_img / a4).astype(np.uint8)
                    for p, img in enumerate(imglist):
                        if p == (len_imglist - interval_num - 1 + interval_num // 4): # 6 ~ 46
                            interval_quarter_img = img.astype(np.uint8)
                        if p == (len_imglist - interval_num - 1 + interval_num // 2): # 6 ~ 46
                            interval_half_img = img.astype(np.uint8)
                        if p == (len_imglist - interval_num - 1 + interval_num // 4 * 3): # 6 ~ 46
                            interval_3quarter_img = img.astype(np.uint8)
                    short_exposure_img = (imglist[-1]).astype(np.uint8)
                    # save
                    imgpath = os.path.join(opt.savepath, opt.atr + '_' + str(i) + '_' + 'long8.png')
                    cv2.imwrite(imgpath, long1_exposure_img)
                    imgpath = os.path.join(opt.savepath, opt.atr + '_' + str(i) + '_' + 'long6.png')
                    cv2.imwrite(imgpath, long2_exposure_img)
                    imgpath = os.path.join(opt.savepath, opt.atr + '_' + str(i) + '_' + 'long4.png')
                    cv2.imwrite(imgpath, long3_exposure_img)
                    imgpath = os.path.join(opt.savepath, opt.atr + '_' + str(i) + '_' + 'long2.png')
                    cv2.imwrite(imgpath, long4_exposure_img)
                    imgpath = os.path.join(opt.savepath, opt.atr + '_' + str(i) + '_' + 'short.png')
                    cv2.imwrite(imgpath, short_exposure_img)
                    imgpath = os.path.join(opt.savepath, opt.atr + '_' + str(i) + '_' + 'long_last.png')
                    cv2.imwrite(imgpath, long_last_exposure_img)
                    imgpath = os.path.join(opt.savepath, opt.atr + '_' + str(i) + '_' + 'interval_quarter.png')
                    cv2.imwrite(imgpath, interval_quarter_img)
                    imgpath = os.path.join(opt.savepath, opt.atr + '_' + str(i) + '_' + 'interval_half.png')
                    cv2.imwrite(imgpath, interval_half_img)
                    imgpath = os.path.join(opt.savepath, opt.atr + '_' + str(i) + '_' + 'interval_3quarter.png')
                    cv2.imwrite(imgpath, interval_3quarter_img)
                    print('long8 frame: averaged by %d frames.' % (a1))
                    print('long6 frame: averaged by %d frames.' % (a2))
                    print('long4 frame: averaged by %d frames.' % (a3))
                    print('long2 frame: averaged by %d frames.' % (a4))
                    print('1st frame: %d position.' % (len_imglist - interval_num - 1 + interval_num // 4))
                    print('2nd frame: %d position.' % (len_imglist - interval_num - 1 + interval_num // 2))
                    print('3rd frame: %d position.' % (len_imglist - interval_num - 1 + interval_num // 4 * 3))
                    print('This is the %d-th video %d-th interval.' % (item + 1, i + 1))
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
    parser.add_argument('--static_or_exposure', type = bool, default = False, \
        help = 'True for static output; False for interp output. Please use False')
    parser.add_argument('--interval_second', type = int, default = 10, help = 'interval of second')
    parser.add_argument('--crop_range', type = int, default = 1, help = 'the time range (second) for true video clip')
    parser.add_argument('--target_range', type = int, default = 1, help = 'the time range (second) for output video clip')
    parser.add_argument('--exposure_type', type = int, default = 16, help = 'e.g. exposure_type=8 means exposure time 1/8 seconds')
    parser.add_argument('--short_cut_frames', type = int, default = 2, help = 'the frames for short exposure images')
    parser.add_argument('--long_cut_frames', type = int, default = 14, help = 'the frames for long exposure images')
    parser.add_argument('--short_cut_ms', type = int, default = 20, help = 'the frames for long exposure images')
    parser.add_argument('--long1_cut_ms', type = int, default = 160, help = 'the frames for long exposure images')
    parser.add_argument('--long2_cut_ms', type = int, default = 120, help = 'the frames for long exposure images')
    parser.add_argument('--long3_cut_ms', type = int, default = 80, help = 'the frames for long exposure images')
    parser.add_argument('--long4_cut_ms', type = int, default = 40, help = 'the frames for long exposure images')
    parser.add_argument('--interval_cut_ms', type = int, default = 70, help = 'the frames for interval')
    parser.add_argument('--resize_w', type = int, default = 5120, help = 'resize_w') # 3840, 2560, 1920, 5760
    parser.add_argument('--resize_h', type = int, default = 2880, help = 'resize_h') # 2160, 1440, 1080, 3240
    parser.add_argument('--checkpoint_path', type = str, \
        default = './SuperSloMo/SuperSloMo.ckpt', \
            help = 'model weight path')
    parser.add_argument('--videopath', type = str, \
        default = 'E:\\SenseTime\\Quad-Bayer to RGB Mapping\\data\\video_original\\Moscow Russia Aerial Drone 5K Timelab.pro _ Москва Россия Аэросъемка-S_dfq9rFWAE.webm', \
            help = 'video path')
    # F:\\SenseTime\\Quad-Bayer to RGB Mapping\\data\\video_original\\Dubai in 4K - City of Gold-SLaYPmhse30.webm
    parser.add_argument('--atr', type = str, default = '1', help = 'the frames for long exposure images')
    parser.add_argument('--video_folder_path', type = str, \
        default = '/mnt/lustre/share/zhaoyuzhi/video1', \
            help = 'video folder path')
    parser.add_argument('--savepath', type = str, \
        default = '/mnt/lustre/zhaoyuzhi/long_last_frame_result1', \
        #default = 'F:\\Deblur\\Short-Long RGB to RGB Mapping\\data\\slrgb2rgb_v1', \
            help = 'save path')
    opt = parser.parse_args()
    print(opt)

    # General information of processing folder
    videolist = get_jpgs(opt.video_folder_path)
    for i in range(len(videolist)):
        print(i, videolist[i])
    videolist = get_files(opt.video_folder_path)

    # Process videos
    process_videos(opt)

    # list name:
    # video1: HAIFA _ ISRAEL - A TRAVEL TOUR - 4K UHD-8-3dvpBqnCE
    # video2: BANFF _ ALBERTA , CANADA - A TRAVEL TOUR - 4K UHD-6NYtiF0Rjf4
    # video3: HONG KONG _ SAR - CHINA - A TRAVEL TOUR - 4K UHD-FlSUQFTRfAw
    # video4: Budapest, Hungary Walking Tour Part 1 - Central Pest (4k Ultra HD 60fps)-dHbLCfbdUVo
    # video5: Budapest, Hungary Walking Tour Part 2 - Castle Hill (4k Ultra HD 60fps)-VV6TePntLLU
    # video6: New York City Walking Tour Part 1 - Midtown Manhattan (4k Ultra HD 60fps)--IpXdtWfneI
    # video7: Philadelphia Walking Tour - Old Town (4k Ultra HD 60fps)-7VVKjpFv2ks
    # video8: Vienna, Austria Walking Tour (4k Ultra HD 60fps)-rJ2IY6rp-G8
    # video9: Salzburg, Austria Walking Tour (4k ultra hd 60fps)-HhVMMfe6tuo
    # video10: Pisa, Italy Walking Tour (4k ultra hd 60fps)-k6bs2fwbUlI
    # video11: Venice, Italy - Grand Canal and Rialto Bridge Walking Tour (4K_60fps)-SamL3P-3eWE
    # video12: VANCOUVER _ BRITISH COLUMBIA , CANADA - A TRAVEL TOUR - 4K UHD-OiJsbXXq-AY
    # video13: MANHATTAN _ NEW YORK CITY - NY , UNITED STATES - A TRAVEL TOUR - 4K UHD-FjU_x1106pg
