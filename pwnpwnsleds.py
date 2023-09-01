#!/usr/bin/env python

import pwnagotchi.plugins as plugins
import logging
import ledshim
import colorsys
import datetime
import time
import yaml
import math

from abc import ABC, abstractmethod
from random import randint, randrange, uniform as randfloat

DEBUG_FILE = '/home/pi/some_file'

            
class Effect(ABC):
    """interface + holder for effects"""
    EFFECTS = {}

    @staticmethod
    @abstractmethod
    def run(duration, speed, r, g, b, l):
        pass

    @classmethod
    def get(cls, effect_name):
        # better to do it as a singlton, but ..
        if not cls.EFFECTS:
            EFFECTS = {
                Cls.__name__.lower(): Cls for Cls in cls.__subclasses__()
            }
        return EFFECTS[effect_name.lower().replace(' ', '')]

    @classmethod
    def play(cls, effect_name, *args):
        return cls.get(effect_name).run(*args)

class Solid(Effect):
    """solid block of color"""
    def run(duration, speed, r, g, b, l):
        ledshim.set_all(255, 255, 0, .8)
        ledshim.show()
        time.sleep(duration)
        ledshim.clear()


class ShootingStars(Effect):
    """adopted from https://github.com/RatJuggler/led-shim-demo"""
    def run(duration, speed, r, g, b, l):

        class DisplayBuffer():
            def __init__(self, bgr, bgg, bgb, bgl, size=ledshim.NUM_PIXELS):
                self.size = size
                self.bg_rgb = [bgr, bgg, bgb]
                self.bg_l = bgl
                self.clear_buffer()

            def clear_buffer(self):
                self.buffer = [0 for i in range(self.size)]

            def set(self, i, value):
                self.buffer[i] = value

            def setmax(self, i, value):
                self.set(i, max(self.get(i), value))

            def get(self, i):
                return self.buffer[i]

            def write(self):
                for i in range(self.size):
                    cs = [r,g,b]
                    cns = []
                    for ci in range(len(cs)):
                        c = cs[ci]
                        bc = self.bg_rgb[ci]
                        cns.append(int(max(0, min(bc + c*self.get(i), 255))))
                    nr, ng, nb = cns
                    ledshim.set_pixel(i, nr, ng, nb, self.bg_l)

        class Star():
            def __init__(self, display_buffer):
                self.t = 0
                self.buffer = display_buffer
                self.alive = True
                self.x = -1
                self.dx = randrange(1, 3)
                self.trail = randrange(3, 8)
                self.intensity_step = 255 // self.trail

            def update(self):
                self.t += 1
                if int(self.x - self.trail) > self.buffer.size:
                    self.alive = False
                if self.t % self.dx == 0:
                    self.x += 1

            def draw(self):
                intensity = 255
                for i in range(self.trail):
                    x = int(self.x - i)
                    x = self.buffer.size - x
                    if 0 <= x < self.buffer.size:
                        self.buffer.setmax(x, intensity/255)
                    intensity -= self.intensity_step

        fps = 1/50
        n_frames = math.ceil(duration/fps)
        bgc = [0,0,40,l]

        buffer = DisplayBuffer(*bgc)
        
        stars = []
        for i in range(n_frames):
            # update/draw stars to buffer
            for star in stars:
                star.update()
                star.draw()

            # cull dead stars
            stars = [star for star in stars if star.alive]

            # add more stars
            if len(stars) == 0 or randint(0, 100) > 90:
                stars.append(Star(buffer))

            # write stars to screen
            if i%2==0:
                buffer.write()
                ledshim.show()
            
            buffer.clear_buffer()
            time.sleep(fps)
        ledshim.clear()


class Fireworks(Effect):
    def run(duration, speed, r, g, b, l):
        w = ledshim.NUM_PIXELS

        t = 0
        st = 0
        sparks = []

        fps = 1/50
        n_frames = math.ceil(duration/fps)

        speed = min(10, speed)

        class Spark():
            def __init__(self, w, x, dx, r, g, b):
                self.w = w
                self.x = x
                self.dx = dx
                self.odx = dx
                self.c = [r, g, b]
                self.t = 0
                self.alive = True

            def update(self):
                self.t += 1
                self.x += self.dx
                self.l = min(1, abs(self.dx/(self.odx*.3)))

                if abs(self.dx) < .01 or self.w <= int(self.x) < 0:
                    self.alive = False

                self.dx *= .8

            def draw(self):
                if 0 <= int(self.x) < self.w:
                    r, g, b = self.c
                    ledshim.set_pixel(int(self.x), r, g, b, self.l * l)

        def explosion(sparks):
            pad = w//5
            x = randint(pad, w-pad)
            c = [int(c * 255)
                 for c in colorsys.hsv_to_rgb(randint(0, 360)/360, 1.0, 1.0)]
            dx = randfloat(.4, 3.7) * (speed / 3)
            sparks.append(Spark(w, x,  dx, *c))
            sparks.append(Spark(w, x, -dx, *c))

        for f in range(n_frames):
            ledshim.clear()
            t += 1

            if len(sparks) == 0:
                st += 1

            if st > 10 or randrange(100) > 92 - speed:
                explosion(sparks)
                st = 0

            for spark in sparks:
                spark.update()
                spark.draw()

            sparks = [spark for spark in sparks if spark.alive]

            ledshim.show()
            time.sleep(fps)


class Rainbow(Effect):
    """taken from led shim examples https://github.com/pimoroni/led-shim"""
    def run(duration, speed, r, g, b, l):
        ledshim.clear()
        ledshim.set_brightness(l)

        spacing = 360.0 / 16.0

        duration = 100
        for i in range(duration):
            hue = int(time.time() * 100) % 360
            for x in range(ledshim.NUM_PIXELS):
                offset = x * spacing
                h = ((hue + offset) % 360) / 360.0
                r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(h, 1.0, 1.0)]
                ledshim.set_pixel(x, r, g, b)
            
            ledshim.show()
            time.sleep(.001)

class Confetti(Effect):
    """modified from rainbow effect"""
    def run(duration, speed, r, g, b, l):
        ledshim.clear()
        ledshim.set_brightness(.8)

        spacing = 360.0 / 16.0
        # rainbow once
        duration = 100
        for i in range(duration):
            hue = int(time.time() * 100) % 180
            for x in range(ledshim.NUM_PIXELS):
                offset = x * spacing
                h = ((hue + offset) % 30.0) / 30.0
                r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(h, 1.0, 1.0)]
                ledshim.set_pixel(x, r, g, b)
            
            ledshim.show()
            time.sleep(.001)
        ledshim.clear()
        ledshim.show()

class LEDreaccs(plugins.Plugin):
    __author__ = 'honey_buns'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'This plugin provides Pimoroni LED shim reactions to Pwnagotchi moods and events. The LED notifications are independent of screen updates to allow for use regardless if a screen is attached to your Pwnagotchi.'

    def __init__(self):
        logging.info('[LEDreaccs] init')
        with open('/home/pi/hmm', 'w') as f:
            f.write('test')
        logging.info('[LEDreaccs] written')

        logging.info('[LEDreaccs] testing effects')
        try:
            self.test()
        except TypeError as e:
            logging.info(f'[LEDreaccs] test failed: {e}')
        else:
            logging.info('[LEDreaccs] tests passed')
        self.is_running = False

    
    def test(self):
        for Cls in Effect.__subclasses__():
            Cls()  # instantiate it to see if it follows interface definition

    
    def on_event(self, event_name):
        logging.info(f'[LEDreaccs] {event_name} start')
        with open(DEBUG_FILE, 'w') as d:
            d.write(
                f'{datetime.datetime.now().isoformat()}: your own pwnpwns was {event_name.upper()[3:]} \n')

        effect_name = self.options['effects'][event_name]
        modifiers = {}

        if isinstance(effect_name, dict):
            modifiers = effect_name
            effect_name = effect_name['effect']
        
        seconds_waited = 0
        while self.is_running:
            time.sleep(1)
            seconds_waited += 1

        try: 
            self.is_running = True
            logging.info(f'[LEDreaccs] waited {seconds_waited} seconds for {event_name}')
            Effect.play(effect_name, 3, 5, 180, 150, 200, 1)
            ledshim.clear()
            ledshim.show()
        finally:
            self.is_running = False

        logging.info(f'[LEDreaccs] {event_name} end')

    def on_webhook(self, path, request):
        """plugin webpage with list/dropdown of effects and their descriptions
        can select effect, adjust sliders, and demo the effect live on the pwnagotchi by pressing a button
        """
        pass

    def on_loaded(self):
        pass

    def on_peer_detected(self, agent, peer):
        self.on_event('on_peer_detected')

    def on_ready(self, agent):
        self.on_event('on_ready')

    def on_internet_available(self, agent):
        self.on_event('on_internet_available')
        
    def on_wait(self, agent, t):
        self.on_event('on_wait')
    
    def on_sleep(self, agent, t):
        self.on_event('on_sleep')

    def on_bored(self):
        self.on_event('on_bored')

    def on_excited(self, agent):
        self.on_event('on_excited')

    def on_lonely(self, agent):
        self.on_event('on_lonely')

    def on_rebooting(self, agent):
        self.on_event('on_rebooting')
    
    def on_epoch(self, agent, epoch, epoch_data):
        self.on_event('on_epoch')
    
    def on_sad(self):
        self.on_event('on_sad')
    
    def on_handshake(self, agent, filename, access_point, client_station):
        self.on_event('on_handshake')
