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

import os
import subprocess
import time

#
# System monitoring library API.
#

def start(interval=10):
    """ Start monitoring the system """
    _start_monitoring(interval)

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

def add_scripts_dir(name, path):
    """ Add a scripts directory to the monitor """
    _scripts_dirs[name] = {
        "path": path,
        "status": _STATUS_NONE
    }

def get_status():
    """ Get the current status of the system """
    for data in _tasks_map.values():
        if data["status"] is _STATUS_FAILURE:
            return _STATUS_FAILURE

    for data in _scripts_dirs.values():
        if data["status"] is _STATUS_FAILURE:
            return _STATUS_FAILURE

    return _STATUS_SUCCESS

def set_activity_ui(on_activity):
    """ Set the UI for when actively monitoring """
    global _on_activity 
    
    _on_activity = on_activity

def set_success_ui(on_success):
    """ Set the UI for when the status is success """
    global _on_success

    _on_success = on_success

def set_failure_ui(on_failure):
    """ Set the UI for when the status is failure """
    global _on_failure

    _on_failure = on_failure

def enable_report(report_filename):
    global _report_filename

    _report_filename = report_filename

#
# Private functions to drive the system monitor
#

_enabled = False
_tasks_map = { }
_scripts_dirs = { }
_monitor_process = None
_report_filename = None

_STATUS_NONE = -1
_STATUS_SUCCESS = 0
_STATUS_FAILURE = 1

def _no_action():
    pass

_on_activity = _no_action
_on_success = _no_action
_on_failure = _no_action

def _start_monitoring(interval):
    """ Monitor the provided tasks """
    global _enabled

    _enabled = True

    while _enabled:
        # Run all the tasks and scripts to check the system
        _on_activity()

        report_file = None
        if _report_filename:
            report_file = open(_report_filename, "w")

        _run_tasks(report_file)
        _run_scripts_dirs(report_file)

        if report_file:
            report_file.close()

        # Update UI and sleep until we want to do the next monitor
        _update_ui(get_status())
        time.sleep(interval)
        continue

def _run_tasks(report_file):
    """ Run each task """
    for name, data in _tasks_map.iteritems():
        # Run the task
        result = _run_command(data["command"], data["args"], report_file)

        if result is data["success_code"]:
            data["status"] = _STATUS_SUCCESS
        else:
            data["status"] = _STATUS_FAILURE

def _run_scripts_dirs(report_file):
    """ For each scripts dir, run each script """
    for name, data in _scripts_dirs.iteritems():
        dir_contents = os.listdir(data["path"])

        status = _STATUS_SUCCESS
        for script in dir_contents:
            # TODO Check file props
            result = _run_command(os.path.join(data["path"], script), [], 
                report_file)

            if result is _STATUS_FAILURE:
                status = _STATUS_FAILURE

        data["status"] = status

def _update_ui(status):
    if status is _STATUS_SUCCESS:
        _on_success()
    else:
        _on_failure()

def _run_command(command, args=[], output=None):
    """ Run a command """
    return subprocess.call([command]+args, stdout=output, stderr=output)
