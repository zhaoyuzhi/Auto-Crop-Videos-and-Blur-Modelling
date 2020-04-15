import argparse
import os
import cv2
import numpy as np

import VideoFrameConversion as vfc
import SuperSloMo as vslomo

img1 = cv2.imread('F:\\Deblur\\Short-Long RGB to RGB Mapping\\data\\slrgb2rgb_v1\\multiple_gt\\0_0_gt.png')
img2 = cv2.imread('F:\\Deblur\\Short-Long RGB to RGB Mapping\\data\\slrgb2rgb_v1\\val\\0_0_gt.png')
k = img1 - img2
print(k)