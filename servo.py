import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

GPIO.setup(7, GPIO.OUT)

start = 2.5
p.start(start)

try:
#	while True:
		#GPIO.output(7,1)
		#time.sleep(0.0015)
		#GPIO.output(7,0)
		#time.sleep(2)
	for i in range(100):
		pos = start + (i / 100.0)
		print pos
		p.ChangeDutyCycle(pos)
		time.sleep(0.01)


except KeyboardInterrupt:
	GRIO.cleanup()
