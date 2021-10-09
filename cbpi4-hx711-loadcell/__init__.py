
# -*- coding: utf-8 -*-
import os
from aiohttp import web
import logging
import RPi.GPIO as GPIO
from unittest.mock import MagicMock, patch
import asyncio
import random
from cbpi.api import *
from .hx711 import HX711


logger = logging.getLogger(__name__)


@parameters([Property.Select(label="dout", options=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27], description="GPIO Pin connected to the Serial Data Output Pin of the HX711"),
    Property.Select(label="pd_sck", options=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27], description="GPIO Pin connected to the Power Down & Seerial Clock Pin of the HX711"),
    Property.Select(label="gain", options = [128,64, 32],description = "Select gain for HX711"),
    Property.Number(label="offset",configurable = True, default_value = 0, description="Offset for the HX711 scale from callibration setup (Default is 0)"),
    Property.Number(label="scale",configurable = True, default_value = 0, description="Scale ratio input for the HX711 scale from callibration setup (Default is 0)"),
    Property.Select(label="Interval", options=[1,2,5,10,30,60], description="Interval in Seconds")])

class CustomSensor(CBPiSensor):
    
    def __init__(self, cbpi, id, props):
        super(CustomSensor, self).__init__(cbpi, id, props)
        self.value = 0
        self.dout = int(self.props.get("dout",0))
        self.pd_sck = int(self.props.get("pd_sck",0))
        self.gain = int(self.props.get("gain",128))
        self.interval = int(self.props.get("Interval",2))
        self.offset = int(self.props.get("offset",0))
        self.scale = int(self.props.get("scale",0))
        
        logging.info("INIT HX711:")
        logging.info("dout: {}".format(self.dout))
        logging.info("pd_sck: {}".format(self.pd_sck))
        logging.info("gain: {}".format(self.gain))
        logging.info("offset: {}".format(self.offset))
        logging.info("scale: {}".format(self.scale))


        hx = HX711(self.dout, self.pd_sck, self.gain)
        hx.set_offset(self.offset)
        hx.set_scale(self.scale)


    async def run(self):
        while self.running is True:
            try:
                self.value = hx.get_grams()
                logging.info(self.value)

                hx.power_down()
                await asyncio.sleep(.001)
                hx.power_up()
                self.push_update(self.value)
                await asyncio.sleep(self.Interval)
            except:
                pass
    
    def get_state(self):
        return dict(value=self.value)


def setup(cbpi):
    cbpi.plugin.register("HX711 Load Cell", CustomSensor)
    pass
