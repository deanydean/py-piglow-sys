import piglowui
from time import sleep

# Start the updater
piglowui.start()

piglowui.pulse_color("blue", 200)
sleep(5)

piglowui.pulse_color("green", 10)
sleep(5)

piglowui.set_color("red", 64)
sleep(2)

piglowui.stop()
sleep(5)
