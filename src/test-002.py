import piglowui
from time import sleep

# Start the updater
piglowui.start()

for i in range(0, 10):
    piglowui.cycle([3, 9, 15], 2, 128)
    piglowui.cycle([3, 9, 15], 2, 128)
    piglowui.pulse_color("green", 200, 128)
    piglowui.set_color("green", 128)
    sleep(5)

# Stop
piglowui.stop()

