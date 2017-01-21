#!/usr/bin/python
#
# Copyright 2016, 2017 Deany Dean
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import subprocess
import time

#
# Piglow-sys library API.
#

def start(interval=10):
    """ Start monitoring the system """
    _monitor_tasks(interval)

def stop():
    """ Stop monitoring the system """
    global _enabled

    _enabled = False

def add_task(name, command, args=[], success_code=0):
    """ Add a system monitoring task """
    _tasks_map[name] = {
        "command": command,
        "args": args,
        "success_code": success_code,
        "status": _STATUS_NONE
    }

def get_status():
    """ Get the current status of the system """
    for data in _tasks_map.values():
        if data["status"] is _STATUS_FAILURE:
            return _STATUS_FAILURE

    return _STATUS_SUCCESS

def set_success_ui(on_success):
    """ Set the piglow UI for when the status is success """
    global _on_success

    _on_success = on_success

def set_failure_ui(on_failure):
    """ Set the piglow UI for when the status is failure """
    global _on_failure

    _on_failure = on_failure
#
# Private functions to drive the system monitor
#

_enabled = False
_tasks_map = { }
_monitor_process = None
_on_success = None
_on_failure = None

_STATUS_NONE = -1
_STATUS_SUCCESS = 0
_STATUS_FAILURE = 1

def _init_ui():
    """ Init the piglow UI """
    piglowui.start()

def _monitor_tasks(interval):
    """ Monitor the provided tasks """
    global _enabled

    _enabled = True

    while _enabled:
        for name, data in _tasks_map.iteritems():
            # Run the task
            result = _run_command(data["command"], data["args"])

            if result is data["success_code"]:
                data["status"] = _STATUS_SUCCESS
            else:
                data["status"] = _STATUS_FAILURE

        # Update UI and sleep until we want to do the next monitor
        _update_ui(get_status())
        time.sleep(interval)
        continue

def _update_ui(status):
    if status is _STATUS_SUCCESS:
        _on_success()
    else:
        _on_failure()

def _run_command(command, args):
    """ Run a command """
    return subprocess.call([command]+args)