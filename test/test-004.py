import sysmon

import os

def success():
    print "SUCCESS"

def failure():
    print "FAILURE"

sysmon.set_success_ui(success)
sysmon.set_failure_ui(failure)

sysmon.add_task("process list success", "ps", [], 0)
sysmon.add_task("process list fail", "ps", [], 1)

sysmon.add_scripts_dir("test scripts", os.path.abspath("test.d"))

# Start the updater
sysmon.start(1)


