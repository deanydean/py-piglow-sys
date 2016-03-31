#!/usr/bin/python
#
# Copyright 2016 Deany Dean
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

import piglow
from multiprocessing import Process, Queue
from Queue import Full, Empty
from time import sleep

#
# Piglow UI utils for piglow-sys library.
#

def start(clear=True):
    """ Start PiGlow UI updates """
    if _enabled:
        return

    if clear:
        _change_task("_clear_all")

    _change_task("_enable")
    _start_updater()

def stop(clear=True):
    """ Stop any PiGlow UI updates """
    if clear:
        _change_task("_clear_all") 
    
    _change_task("_disable")

def clear_all():
    """ Clear all LEDs """
    _change_task("_clear_all")

def pulse_color(color, speed=10, low=64, high=255):
    """ Pulse each LED of the defined color at the defined speed. """
    _change_task("_pulse_color", [color, speed, low, high], True)

def set_color(color, value):
    """ Set the value of the defined color """
    _change_task("_set_color", [color, value])

def cycle(leds, speed=10, low=0, high=255):
    """ Cycle each LED from low to high in order """
    _change_task("_cycle", [leds, speed, low, high], True)

def dim(led, speed=2, high=255, low=0):
    """ Dims the LED from high to low at the given speed """
    _change_task("_dim", [led, speed, high, low], True)

def set(leds, value):
    """ Sets the value of each led """
    _change_task("_set", [leds, value])

def pulse(led, speed=2, low=0, high=255):
    """ Pulse the LED from low to high at the given speed """
    _change_task("_pulse", [led, speed, low, high], True)

#
# Private functions to drive the UI (ie, PiGlow updates)
#

_enabled = False
_task_queue = Queue()
_updater_process = None

_NOTASK_SLEEP_INTERVAL = 1

def _enable():
    """ Enable the PiGlow UI updates """
    global _enabled

    _enabled = True

def _disable():
    """ Disable the PiGlow UI updates """
    global _enabled

    _enabled = False

def _change_task(task, args=[], repeat=False, interval=0):
    """ Change the current task """
    try:
        _task_queue.put([task, args, repeat, interval])
    except Full:
        print "Task ", task, " failed. Task queue full"
        return
 
def _handle_tasks(tasks):
    """ Perform the UI update for the current task """
    global _enabled

    task = None
    _enabled = True

    while _enabled:
        try:
            task = tasks.get(False)
        except Empty:
            # Do nothing, this is a valid state
            pass

        # If we have no task, just sleep for an interval and read again
        if task is None:
            sleep(_NOTASK_SLEEP_INTERVAL)
            continue

        # Get and exec the task method
        task_method = globals()[task[0]]
        if task_method is None:
            sleep(task[3])
            continue
        else:
            task_method(*task[1])

        if not task[2]:
            task = None
    
def _start_updater():
    """ Start an updater process if there isn't already one """
    global _updater_process

    # If already enabled, just return
    if _enabled:
        return

    _updater_process = Process(target=_handle_tasks, args=(_task_queue,))
    _updater_process.start()
    

#
# API drawing task functions
#

def _clear_all():
    """ Clear all LEDs """
    for l in range(0, 18):
        piglow.set(l, 0)
    piglow.show()

def _set_color(color, value):
    """ Set the value of the defined color """
    color_setter = getattr(piglow, color)
    color_setter(value)
    piglow.show()

def _pulse_color(color, speed, low, high):
    """ Pulse each LED of the defined color at the given speed """
    color_setter = getattr(piglow, color)
    pulse_range = range(low, high)
    wait_for = 1/speed

    for c in pulse_range:
        color_setter(c)
        piglow.show()
        sleep(wait_for)

    for c in reversed(pulse_range):
        color_setter(c)
        piglow.show()
        sleep(wait_for)

def _pulse(led, speed, low, high):
    """ Pulse the LED from low to high """
    pulse_range = range(low, high)
    wait_for = 1/speed

    for c in pulse_range:
        piglow.set(led, c)
        piglow.show()
        sleep(wait_for)

    for c in reversed(pulse_range):
        piglow.set(led, c)
        piglow.show()
        sleep(wait_for)

def _set(leds, value):
    """ Sets the value of each led """
    for led in leds:
        piglow.set(led, value)
    piglow.show()

def _dim(led, speed, high, low):
    """ Dims the led from high to low at the given speed """
    dim_range = range(low, high)
    wait_for = 1/speed

    for c in reversed(dim_range):
        piglow.set(led, c)
        piglow.show()
        sleep(wait_for)

def _cycle(leds, speed, low, high):
    """ Cycle each LED from low to high in order """
    pulse_range = range(low, high)
    wait_for = 1/speed

    # Set each LED to the LOW state
    _set(leds, low)

    for i in range(0, len(leds)):
        for c in pulse_range:
            # Increase the LED to HIGH
            piglow.set(leds[i], c)
            piglow.show()
            sleep(wait_for)

            # Decrease the previous LED back to LOW at same rate
            if i > 0:
                piglow.set(leds[i-1], high-(c-low))
                piglow.show()
                sleep(wait_for)

    # Decrease the final LED back to LOW state
    _dim(leds[-1], speed, high, low)

    # Set each LED to the LOW state
    _set(leds, low)
