import cv2
import os

def check_path(path):
    #lastlen = len(path.split('/')[-1])
    #path = path[:(-lastlen)]
    if not os.path.exists(path):
        os.makedirs(path)

def decode_fourcc(cc):
    return "".join([chr((int(cc) >> 8 * i) & 0xFF) for i in range(4)])

def get_video_info(readpath):
    # read one video
    vc = cv2.VideoCapture(readpath)
    # print details of video
    fps = vc.get(cv2.CAP_PROP_FPS)
    frames = vc.get(cv2.CAP_PROP_FRAME_COUNT)
    time = frames / fps
    width = vc.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = vc.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fourcc = vc.get(cv2.CAP_PROP_FOURCC)
    fourcc = decode_fourcc(fourcc)
    print("video name =", readpath)
    print("video fps =", fps)
    print("video whole time length =", time, 'seconds')
    print("video frames =", frames)
    print("video width =", width)
    print("video height =", height)
    print("video fourcc =", fourcc)
    return fps, frames, time, width, height

# Warning: mind this method takes up your memory
def get_all_frames(readpath):
    # read one video
    vc = cv2.VideoCapture(readpath)
    # print details of video
    fps = vc.get(cv2.CAP_PROP_FPS)
    frames = vc.get(cv2.CAP_PROP_FRAME_COUNT)
    print("video fps =", fps)
    print("video frames =", frames)
    # save to image list
    imglist = []
    for i in range(int(frames)):
        rval, frame = vc.read()
        imglist.append(frame)
    return imglist

# save frames at each interval frame
def video2frame_by_frame(readpath, savepath, interval = 24):
    # read one video
    vc = cv2.VideoCapture(readpath)
    # whether it is truely opened
    if vc.isOpened():
        rval, frame = vc.read()
    else:
        rval = False
    print(rval)
    interval = round(interval)
    print(interval)
    check_path(savepath)
    # save each frame; default interval = 24 (normally 24 frames in a second for videos)
    c = 1
    while rval:
        if (c % interval == 0):
            #sp = os.path.join(savepath, readpath.split('/')[-1][:-4], str(c) + '.jpg')
            sp = os.path.join(savepath, str(c) + '.jpg')
            cv2.imwrite(sp, frame)
            print('Frame %d is saved' % c)
        c = c + 1
        cv2.waitKey(1)
        rval, frame = vc.read()
    # release the video
    vc.release()

# save frames at each interval second
def video2frame_by_second(readpath, savepath, second = 10):
    # read one video
    vc = cv2.VideoCapture(readpath)
    # whether it is truely opened
    if vc.isOpened():
        rval, frame = vc.read()
    else:
        rval = False
    print(rval)
    interval = second * vc.get(cv2.CAP_PROP_FPS)
    interval = round(interval)
    print(interval)
    check_path(savepath)
    # save each frame; default interval = 24 (normally 24 frames in a second for videos)
    c = 1
    while rval:
        if (c % interval == 0):
            sp = os.path.join(savepath, str(c) + '.jpg')
            cv2.imwrite(sp, frame)
            print('Frame %d is saved' % c)
        c = c + 1
        print(c)
        cv2.waitKey(1)
        rval, frame = vc.read()
    # release the video
    vc.release()

if __name__ == '__main__':

    readpath = './AircraftTakingOff1.avi'
    savepath = '/media/6864FEA364FE72E4/video_frame_conversion'

    # interval = 1: extract each frame; interval = 24: extract frame every second
    video2frame_by_frame(readpath, savepath, interval = 1)
    
