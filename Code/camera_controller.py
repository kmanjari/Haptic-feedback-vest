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

import cv2
from time import time, sleep
from datetime import datetime
import Queue
import os
from common import *

output_dir = 'raw_images'

def capture_images(camera_config, raw_image_queue, stop_signal_queue, debug):
    if debug and not os.path.exists(output_dir):
        print 'creating directory {}'.format(output_dir)
        os.makedirs(output_dir)

    delay = camera_config.get('camera_delay', 0)

    # Initialize cameras
    cam1 = cv2.VideoCapture(0)
    cam2 = cv2.VideoCapture(1)
    cam1.set(cv2.cv.CV_CAP_PROP_FPS, 10);
    cam2.set(cv2.cv.CV_CAP_PROP_FPS, 10);

    print 'camera_controller: camera 1 has resolution {}x{}'\
        .format(cam1.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH),
                cam1.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))
    print 'camera_controller: camera 2 has resolution {}x{}'\
        .format(cam2.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH),
                cam2.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))

    while should_run(stop_signal_queue):
        start = time()
        ret1, frame1 = cam1.read()
        ret2, frame2 = cam2.read()
        print 'camera_controller:  capturing two images took {}s'\
            .format(time() - start)

        timestr = datetime.now().strftime('%Y.%m.%d.%H.%M.%S.%f')
        raw_image_queue.put((frame2, timestr))
        raw_image_queue.put((frame1, timestr))
        if debug:
            cv2.imwrite('{}/raw_{}_1.png'.format(output_dir, timestr), frame1)
            cv2.imwrite('{}/raw_{}_2.png'.format(output_dir, timestr), frame2)

        sleep(delay)

    # Cleanup
    print 'camera_controller: Ending camera loop'
    cam1.release()
    cam2.release()
    print 'after camera releases'
    cv2.destroyAllWindows()
    print 'camera_controller: Done closing everything'
