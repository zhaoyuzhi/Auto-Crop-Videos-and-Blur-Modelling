# Auto-Crop Videos and Blur Modelling

Automatic crop videos and produce static, interpolation, and averaged frames or new videos for making blur dataset.

The interpolation is based on CVPR 2018 paper [SuperSloMo](https://people.cs.umass.edu/~hzjiang/projects/superslomo/).

## 1 Description of the scripts

- [SuperSloMo](https://github.com/avinashpaliwal/Super-SloMo): A packed lib for frame interpolation in this project

- VideoFrameConversion: A packed lib including printing video information, video-frame transformation

- video_clipper.py: Crop video into multiple small clips and concatnate all clips into a new video. There are 3 versions: static video, moving video and interp video

- video2rgb.py: Crop video into many single frames. There are 3 versions: only GT, averaged frame and interp frame

- disparity_2frames.py: Compute disparity of 2 frames

- video_get_statics.py: Display all information of videos in a folder

## 2 Description of three versions in video_clipper

Suppose the continuous frames f<sub>1</sub>, f<sub>2</sub>, f<sub>3</sub>, ..., f<sub>n</sub> are for constructing new video, and each clip includes t seconds

- Static video: Save f<sub>n</sub> for n*t times

- Moving video: Save each frame f<sub>k</sub> for t times

- Interp video: Interpolate 1-8 frames to each two original frames f<sub>k</sub> and f<sub>k+1</sub>, then save them

## 3 Description of three versions in video2rgb

It decomposes original video into many individual frames. The output includes short-exposure (obtained by smaller numbers of frames), long-exposure (obtained by larger numbers of frames), and ground truth (obtained by single frame).

- Only GT: Only save ground truth frames at different sample point

- Averaged frame: Save short/long-exposure frames by averaging neighbouring frames

- Interp frame: Save short/long-exposure frames by interpolating and averaging neighbouring frames

## 4 Description of three versions in other video2rgb files

- video2rgb_burst.py: generate dense burst long exposure images 生成连续的长曝帧

- video2rgb_mobile_application.py: generate long exposure frame and short exposure frame, and there is an interval between the two frames 生成长曝帧，经过一段间隔后，生成短曝帧

## 5 Description of three versions in video fps change

- video_change_fps.py: generate same video with specific fps 生成可以指定fps的相同video

- video_slomo.py: generate interpolated video with specific fps and interp ratio 生成经过SuperSloMo插帧后的video，可以指定fps和插帧比例

## 6 Log files for type1-type9 video generation and ckpt model for SuperSloMo

[Onedrive Link](https://portland-my.sharepoint.com/:f:/g/personal/yzzhao2-c_ad_cityu_edu_hk/EpEte0zzHt5IqQr01LINntEBrv2waXRwwBEjDtWns-gyeA?e=U9xw4t)
