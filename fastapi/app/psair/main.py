 # 
 # This file is part of the PlantStudio Hub distribution (https://github.com/plant-studio/hub).
 # Copyright (c) 2015 Simon Romanski.
 # 
 # This program is free software: you can redistribute it and/or modify  
 # it under the terms of the GNU General Public License as published by  
 # the Free Software Foundation, version 3.
 #
 # This program is distributed in the hope that it will be useful, but 
 # WITHOUT ANY WARRANTY; without even the implied warranty of 
 # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
 # General Public License for more details.
 #
 # You should have received a copy of the GNU General Public License 
 # along with this program. If not, see <http://www.gnu.org/licenses/>.
 #
from typing import Optional
from fastapi import FastAPI
import RPi.GPIO as GPIO
import serial
from time2relax import CouchDB
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column,String,DateTime,Integer,create_engine
from datetime import datetime

# **************************
# THIS IS THE AIR CONTROLLER
# **************************

app = FastAPI()

#### couchDB ####
ps=CouchDB('http://couchdb:5984/plantstudio')

# InfluxDb
InfluxUrl = "http://influxdb:8086/write"
InfluxQueryString = {"db": "grow1", "precision": "ms"}

# SQLalchemy
Base = declarative_base
engine = create_engine('sqlite:///ps.db',echo=True)

#class res(Base):
#    __tablename__='reservoir'
#    id=Column(Integer)



# START SENSIBO ################
sensibo = {'url':'https://home.sensibo.com/api/v2','apiKey':'[API-KEY]','deviceId':'[DEVICE-ID]'}

# SETUP GPIO mode and initiat used pins
GPIO.setmode(GPIO.BCM)
outPins = [19,26]
GPIO.setup(outPins, GPIO.OUT)

# START CO2 SENSOR #############
ser = serial.Serial("/dev/ttyS0")
ser.write(str.encode("K 2\r\n"))
ser.flushInput()
# END CO2 SENSOR ###############

@app.get("/")
def read_root():
    return {"Hello": "There"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}