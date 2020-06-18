import argparse
import cv2
import os

def get_frames(videoname, savepath, interval):
    # Basical definition
    video = cv2.VideoCapture(videoname)
    count = 0

    # Whether the video file is open
    if video.isOpened():
        rval, frame = video.read()
    else:
        rval = False

    # Loop the video frames
    while rval:
        rval, frame = video.read()
        if (count % interval) == 0:
            cv2.imwrite(os.path.join(savepath, str(count) + '.png'), frame)
        count = count + 1
        cv2.waitKey(1)
    video.release()

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    # pre-train, saving, and loading parameters
    parser.add_argument('--videoname', type = str, default = 'SpiritedAway.mkv', help = 'saving mode, and by_epoch saving is recommended')
    parser.add_argument('--savepath', type = str, default = 'C:\\Users\\ZHAO Yuzhi\\Desktop\\dataset\\Manga\\SpiritedAway', help = 'interval between model checkpoints (by epochs)')
    parser.add_argument('--interval', type = int, default = 1, help = 'interval between each frame')
    opt = parser.parse_args()

    get_frames(opt.videoname, opt.savepath, opt.interval)
    
