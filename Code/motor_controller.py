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
import time
import signal
import Adafruit_PCA9685
import sys
import numpy as np
from PIL import Image
from time import time, sleep

LUT_NEW_INDEX = { 0:0, 1:4, 2:8, 3:12, 4:1, 5:5, 6:9, 7:13, 8:2, 9:6, 10:10,
                  11:14, 12:3, 13:7, 14:11, 15:15 }

vibration_output_filename = 'vibrations.txt'

def vibrate_motors(motor_config, depth_map_queue, stop_signal_queue):
    percentile_threshold = motor_config.get('percentile_threshold', 80)
    threshold_levels = motor_config.get('threshold_levels', [100,100,150,175,200])
    power_pwm = motor_config.get('power_pwm', [0, 250, 500, 750, 1000])
    num_rows = motor_config.get('num_rows', 4)
    num_cols = motor_config.get('num_cols', 4)

    # Initialise the PCA9685 using the default address (0x40).
    pwm = Adafruit_PCA9685.PCA9685()
    
    while should_run(stop_signal_queue):
        depth_map, timestamp = get_depth_map_array(depth_map_queue)
        if depth_map is None:
            sleep(0.5)
            continue

        start = time()
        alertness_list = get_alertness(depth_map, percentile_threshold,
                                       threshold_levels, num_rows, num_cols)
        print 'motor_controller: altertness levels are {}'.format(alertness_list)

        vibrate_selected_motors(pwm, alertness_list, power_pwm)

    turn_all_off(pwm, num_rows * num_cols)
    print 'motor_controller: received stop signal. Ending vibrations.'

def get_depth_map_array(depth_map_queue):
    size = depth_map_queue.qsize()
    print 'motor_controller: depth map queue size = {}'.format(size)
    if size < 1:
        # No new pictures yet
        return None, None

    # Throw out old images from queue
    old_image_count = size - 1
    for i in range(old_image_count):
        depth_map_queue.get()

    # depth_map_array = np.asarray(depth_map_queue.get())
    depth_map_array, timestamp = depth_map_queue.get()
    depth_map_array = depth_map_array.getNumpy()
    return depth_map_array, timestamp

#turn all motors off
def turn_all_off(pwm, num_channels):
    for motor in range(num_channels):
        pwm.set_pwm(motor, 0, 0)

def vibrate_selected_motors(pwm, alertness_levels, motor_pwm):
    for i in range(len(alertness_levels)):
        alertness = alertness_levels[i]
        pwm.set_pwm(i, 0, motor_pwm[alertness])

def get_alertness(image, percentile_threshold, threshold_levels,
                       num_rows, num_cols):

    block_dimension = (image.shape[0]/num_rows, image.shape[1]/num_cols)
    alertness_level = np.zeros(num_rows*num_cols)
    alertness = [0] * (num_rows * num_cols)
    percentile_cutoffs = np.zeros(num_rows*num_cols)
    for j in range(num_cols):
        for i in range(num_rows):
            index = i*num_rows + j
            block = image[
                i*block_dimension[0] : i*block_dimension[0] + block_dimension[0],
                j*block_dimension[1] : j*block_dimension[1] + block_dimension[1],
                0
            ]
            
            # do some processing on the block
            # get the cutoff pixel value
            block_thresh = np.percentile(block, percentile_threshold)
            percentile_cutoffs[index] = block_thresh

            # depending on its threshold, we set the alertness level
            index = LUT_NEW_INDEX[index]
            if block_thresh > threshold_levels[3]:
                #alertness_level[index] = 4
                alertness[index] = 4
            elif block_thresh > threshold_levels[2]:
                #alertness_level[index] = 3
                alertness[index] = 3
            elif block_thresh > threshold_levels[1]:
                #alertness_level[index] = 2
                alertness[index] = 2
            elif block_thresh > threshold_levels[0]:
                #alertness_level[index] = 1
                alertness[index] = 1

    return alertness
