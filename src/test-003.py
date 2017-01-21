import sysmon

def success():
    print "SUCCESS"

def failure():
    print "FAILURE"

sysmon.set_success_ui(success)
sysmon.set_failure_ui(failure)

sysmon.add_task("process list success", "ps", [], 0)
sysmon.add_task("process list fail", "ps", [], 1)

# Start the updater
sysmon.start(1)


