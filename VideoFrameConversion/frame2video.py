import os
import cv2
import time

image_format = ['.jpg', '.JPEG', '.png', '.bmp']

def check_path(path):
    #lastlen = len(path.split('/')[-1])
    #path = path[:(-lastlen)]
    if not os.path.exists(path):
        os.makedirs(path)

def get_files(path):
    # Read a folder, return the complete path
    ret = []
    for root, dirs, files in os.walk(path):
        for filespath in files:
            p = os.path.join(root, filespath)
            if p[-4:] in image_format:
                ret.append(p)
    return ret

def frame2video(readpath, savepath, fps = 24, size = (854, 480)):
    # get the whole list
    imglist = get_files(readpath)

    # fps: write N images in one second

    # size: the size of a video
    # 144p: 256 * 144
    # 256p: 456 * 256
    # 480p: 854 * 480

    # video encode type
    # cv2.VideoWriter_fourcc('D','I','V','X') 文件名为.mp4
    # cv2.VideoWriter_fourcc('X','V','I','D') MPEG-4 编码类型，文件名后缀为.avi
    # cv2.VideoWriter_fourcc('I','4','2','0') YUV 编码类型，文件名后缀为.avi
    # cv2.VideoWriter_fourcc('P','I','M','I') MPEG-1编码类型，文件名后缀为.avi
    # cv2.VideoWriter_fourcc('T','H','E','O') Ogg Vorbis 编码类型，文件名为.ogv
    # cv2.VideoWriter_fourcc('F','L','V','1') Flask 视频，文件名为.flv
    if savepath[-4:] == '.mp4':
        fourcc = cv2.VideoWriter_fourcc('D','I','V','X')
    if savepath[-4:] == '.avi':
        fourcc = cv2.VideoWriter_fourcc('I','4','2','0')
    if savepath[-4:] == '.ogv':
        fourcc = cv2.VideoWriter_fourcc('T','H','E','O')
    if savepath[-4:] == '.flv':
        fourcc = cv2.VideoWriter_fourcc('F','L','V','1')

    # create a video writer
    video = cv2.VideoWriter(savepath, fourcc, fps, size)

    # write images
    for item in imglist:
        img = cv2.imread(item)
        img = cv2.resize(img, size)
        video.write(img)
    video.release()

def video2video_by_interval(readpath, savepath, interval):
    # read one video    
    vc = cv2.VideoCapture(readpath)
    # print details of video
    fps = vc.get(cv2.CAP_PROP_FPS)
    frames = vc.get(cv2.CAP_PROP_FRAME_COUNT)
    time = frames / fps
    width = vc.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = vc.get(cv2.CAP_PROP_FRAME_HEIGHT)

    # create a video writer
    #fourcc = cv2.VideoWriter_fourcc('D','I','V','X')            # mp4
    fourcc = cv2.VideoWriter_fourcc('m','p','4','v')            # mp4
    check_path(savepath)
    savepath = os.path.join(savepath, 'temp.mp4')
    video = cv2.VideoWriter(savepath, fourcc, fps, (width, height))

    # read and write
    # whether it is truely opened
    if vc.isOpened():
        rval, frame = vc.read()
    else:
        rval = False
    print(rval)
    interval = round(interval)
    print(interval)
    # save each frame; default interval = 24 (normally 24 frames in a second for videos)
    c = 1
    while rval:
        if (c % interval == 0):
            video.write(frame)
            print('Frame %d is saved' % c)
        c = c + 1
        cv2.waitKey(1)
        rval, frame = vc.read()
    # release the video
    vc.release()
    video.release()

def video2video_by_period(readpath, savepath, start, end):
    # read one video    
    vc = cv2.VideoCapture(readpath)
    # print details of video
    fps = vc.get(cv2.CAP_PROP_FPS)
    frames = vc.get(cv2.CAP_PROP_FRAME_COUNT)
    time = frames / fps
    width = vc.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = vc.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print("video name =", readpath)
    print("video fps =", fps)
    print("video whole time length =", time, 'seconds')
    print("video frames =", frames)
    print("video width =", width)
    print("video height =", height)
    fps = round(fps)
    width = round(width)
    height = round(height)
    print("corrected video fps =", fps)
    print("corrected video width =", width)
    print("corrected video height =", height)

    # create a video writer
    #fourcc = cv2.VideoWriter_fourcc('D','I','V','X')            # mp4
    fourcc = cv2.VideoWriter_fourcc('m','p','4','v')            # mp4
    check_path(savepath)
    savepath = os.path.join(savepath, 'temp.mp4')
    video = cv2.VideoWriter(savepath, fourcc, fps, (width, height))

    # read and write
    # whether it is truely opened
    if vc.isOpened():
        rval, frame = vc.read()
    else:
        rval = False
    print(rval)
    # save each frame; default interval = 24 (normally 24 frames in a second for videos)
    c = 1
    while rval:
        if (c >= start) and (c <= end):
            video.write(frame)
            print('Frame %d is saved' % c)
        c = c + 1
        cv2.waitKey(1)
        rval, frame = vc.read()
        if c > end:
            break
    # release the video
    vc.release()
    video.release()

if __name__ == '__main__':

    readpath = 'D:\\dataset\\perframe\\DAVIS\\bike-packing'
    savepath = './result.avi'
    fps = 12
    size = (854, 480)

    frame2video(readpath, savepath, fps, size)
