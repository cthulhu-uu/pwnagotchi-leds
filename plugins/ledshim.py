#!/usr/bin/env python
from threading import Event
import _thread
import logging
import colorsys
import time
import pwnagotchi.plugins as plugins
import ledshim

class Led(plugins.Plugin):
    def __init__(self):
        self._is_busy = False

    # called when the agent is sleeping for t seconds
    def on_sleep(self, agent, t):
        spacing = 360.0 / 16.0
        hue = 0

        ledshim.set_clear_on_exit()
        ledshim.set_brightness(0.8)

        while True:
            hue = int(time.time() * 100) % 360
            for x in range(ledshim.NUM_PIXELS):
                offset = x * spacing
                h = ((hue + offset) % 360) / 360.0
                r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(h, 1.0, 1.0)]
                ledshim.set_pixel(x, r, g, b)

            ledshim.show()
            time.sleep(0.0001)
    # called when the agent is waiting for t seconds
    def on_wait(self, agent, t):
        spacing = 360.0 / 16.0
        hue = 0

        ledshim.set_clear_on_exit()
        ledshim.set_brightness(0.8)

        while True:
            hue = int(time.time() * 100) % 360
            for x in range(ledshim.NUM_PIXELS):
                offset = x * spacing
                h = ((hue + offset) % 360) / 360.0
                r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(h, 1.0, 1.0)]
                ledshim.set_pixel(x, r, g, b)

            ledshim.show()
            time.sleep(0.0001)
    def on_sad(self, agent):  # https://pwnagotchi.ai/intro/#span-class-face-span-sad
    	spacing = 360.0 / 16.0
    	hue = 0

    	ledshim.set_clear_on_exit()
    	ledshim.set_brightness(0.8)

   	while True:
	    hue = int(time.time() * 100) % 360
            for x in range(ledshim.NUM_PIXELS):
            	offset = x * spacing
            	h = ((hue + offset) % 360) / 360.0
            	r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(h, 1.0, 1.0)]
            	ledshim.set_pixel(x, r, g, b)

            ledshim.show()
            time.sleep(0.0001)
