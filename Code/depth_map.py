# MIT License
#
# Copyright (c) 2016 Burkle, Lin, Prasad, Ranmuthu, Speiser
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from common import *
from cv2 import cv
import cv2
from glob import glob
from datetime import datetime
import os
from SimpleCV.ImageClass import Image, ColorSpace
from SimpleCV.Camera import StereoImage
from time import time, sleep

output_dir = 'depth_map_images'

def create_depth_map(depth_map_config, raw_image_queue, depth_map_queue,
                     stop_signal_queue, debug):
    if debug and not os.path.exists(output_dir):
        print 'creating directory {}'.format(output_dir)
        os.makedirs(output_dir)

    disparity = depth_map_config.get('disparity', 40)
    
    while should_run(stop_signal_queue):
        print 'starting depth map loop'
        img1, img2, timestamp = get_raw_images(raw_image_queue)
        if img1 is None or img2 is None:
            # This should only happen at startup because the cameras are not a
            # bottleneck. Wait a little while so we're not spamming too much.
            sleep(0.5)
            continue
        
        start = time()
        stereo_img = StereoImage(img1,img2)
        depth_map = stereo_img.findDisparityMap(disparity, method = 'BM')
        print 'depth_map: generating depth map took {}'.format(time() - start)

        depth_map_queue.put((depth_map, timestamp));
        if debug:
            output_filename = '{}/depth_{}.png'.format(output_dir, timestamp)
            depth_map.save(output_filename)

    print 'depth_map: ending depth map loop'

def get_raw_images(raw_image_queue):
    size = raw_image_queue.qsize()
    print 'depth_map: raw image queue size = {}'.format(size)
    if size < 2:
        # No new pictures yet
        return None, None, None

    # Throw out old images from queue
    old_image_count = size - (2 if size % 2 == 0 else 3)
    for i in range(old_image_count):
        raw_image_queue.get()

    img1, timestamp1 = raw_image_queue.get()
    img2, timestamp2 = raw_image_queue.get()
    assert timestamp1 == timestamp2, 'Timestamps of raw images do not match'
    img1 =Image(img1.transpose(1,0,2)[:,:,::-1])
    img2 =Image(img2.transpose(1,0,2)[:,:,::-1])

    return img1, img2, timestamp1
