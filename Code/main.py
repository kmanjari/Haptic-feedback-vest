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

from camera_controller import *
from depth_map import *
import json
from motor_controller import *
from multiprocessing import Process, Queue
from time import time, sleep

CONFIG_FILENAME = 'config.json'

def main():
    with open(CONFIG_FILENAME) as config_file:
        config = json.load(config_file)
    camera_config = config.get('cameras', {})
    depth_map_config = config.get('depth_map', {})
    motor_config = config.get('motors', {})
    debug = config.get('debug', False)

    stop_signal = Queue()
    raw_images = Queue()
    depth_maps = Queue()

    camera_process = Process(
        target=capture_images,
        args=(camera_config, raw_images, stop_signal, debug))
    camera_process.start()

    depth_map_process = Process(
        target=create_depth_map,
        args=(depth_map_config, raw_images, depth_maps, stop_signal, debug))
    depth_map_process.start()

    haptic_process = Process(
        target=vibrate_motors,
        args=(motor_config, depth_maps, stop_signal))
    haptic_process.start()

    # Uncomment these lines to stop early for testing
    # sleep(30)
    # print '******************************'
    # stop_signal.put(True)
    # stop_signal.put(True)
    # stop_signal.put(True)

if __name__ == '__main__':
    main()
