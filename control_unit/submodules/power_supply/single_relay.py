import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

class SingleRelay():
	def __init__(self, p=14):
		self.outpin = p				# remember BCM pin!
		GPIO.setup(p, GPIO.OUT)
		
	def ON(self):
		GPIO.output(self.outpin, True)
		
	def OFF(self):
		GPIO.output(self.outpin, False)
