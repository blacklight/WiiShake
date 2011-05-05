#!/usr/bin/python

#
# A simple module that connects to a Wiimote device and recognize when you "shake" it, performing some actions when the event occurs
# You need the Python porting of the cwiid library in order to use this class (http://abstrakraft.org/cwiid/)
#
# Sample implementation:
#
# import wiishake
#
# def myAction() :
#	print ("The Wiimote was shaken")
#
# def main() :
#	wiishake = wiishake.WiiShake (onActionStart = myAction)
#	wiishake.start()
#	wiishake.join()
#
# Author: Fabio "BlackLight" Manganiello <blacklight@autistici.org>, http://0x00.ath.cx
# Released under GNU GPL licence v.3
#

from cwiid import *
from threading import Thread

import math
import time

class WiiShake (Thread):
	"""
	@author: Fabio "BlackLight" Manganiello <blacklight@autistici.org>, http://0x00.ath.cx

	Thread that manages the recognition of a "shaking" of a Wiimote controller
	You need the Python porting of the cwiid library in order to use this class (http://abstrakraft.org/cwiid/)
	Sample implementation:

	def myAction() :
		print ("The Wiimote was shaken")

	def main() :
		wiishake = WiiShake (onActionStart = myAction)
		wiishake.start()
		wiishake.join()
	"""

	def __init__ (self, initRumble = True, onActionStart = None, onActionEnd = None, deviationThreshold = 15) :
		"""
		Constructor for the thread. It takes as arguments:
		- initRumble, set as True if you want your Wiimote to rumble when the connection is performed (default: True)
		- onActionStart, function to be executed when the Wiimote is shaken (default: no action)
		- onActionEnd, function to be executed when the shake action on the Wiimote is ended (default: no action)
		- deviationThreshold, numerical value that expresses the threshold in the standard devation buffer to recognize a "shake" gesture (default: 15)
		"""
		Thread.__init__ (self)
		self.startAction = onActionStart
		self.endAction = onActionEnd
		self.deviationThreshold = deviationThreshold

		print ("Press 1+2 for putting your Wiimote in discoverable mode")
		self.wii = Wiimote()

		if initRumble :
			self.wii.rumble = 1
			time.sleep (1)
			self.wii.rumble = 0

		self.wii.enable (FLAG_MOTIONPLUS)
		self.wii.rpt_mode = RPT_ACC

	def run (self) :
		""" Execute the thread itself """
		buf = []
		bufSize = 10
		bufFull = False

		latest_stddev = []
		latest_stddev_full = False
		latest_stddev_size = 5
		inAction = False

		while True :
			# The current accelerometer value is computed as module of the XYZ sensors values
			value = 0;
			
			for i in self.wii.state['acc'] :
				value += i*i
			value = math.sqrt(value)

			# Manage the set of the accelerometer values as a circular buffer
			if not bufFull :
				buf.append (value)

				if len (buf) == bufSize :
					bufFull = True
			else :
				# Shift back all the values
				for i in range (1, len (buf)) :
					buf[i-1] = buf[i]

				# Append the new value
				buf[bufSize-1] = value

			# Get the average value
			avg = 0

			for i in buf :
				avg += i
			avg /= len (buf)

			# Get the standard deviation
			stddev = 0

			for i in buf :
				stddev += (i-avg)*(i-avg)
			stddev = math.sqrt (stddev / len (buf))

			# Save the acquired standard deviation
			if not latest_stddev_full :
				latest_stddev.append (stddev)

				if len (latest_stddev) == latest_stddev_size :
					latest_stddev_full = True
			else :
				# Shift back all the values
				for i in range (1, len (latest_stddev)) :
					latest_stddev[i-1] = latest_stddev[i]

				# Append the new value
				latest_stddev[latest_stddev_size - 1] = stddev

			if stddev >= self.deviationThreshold and len (buf) >= bufSize :
				if not inAction :
					inAction = True

					if self.startAction != None :
						self.startAction()
			else :
				if inAction :
					inAction = False

					if self.endAction != None :
						self.endAction()

			time.sleep (0.05)

#
# Sample implementation
#

def myAction() :
	print ("Action started")

def main() :
	wiishake = WiiShake (onActionStart = myAction)
	wiishake.start()
	wiishake.join()

if __name__ == "__main__" :
	main()

