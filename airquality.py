#!/usr/local/bin/python3

import urllib.request
import json
import os
import sys
import datetime
from influxdb import InfluxDBClient

url="https://www.purpleair.com/json?show="

testjson=None

def averageRoundPM(sensors, valueName):
    avg=0
    measurements=0
    for sensor in sensors:
        if sensor is not None and sensor.get(valueName) is not None:
            avg = avg + float(sensor[valueName])
            measurements = measurements + 1
    if measurements > 0:
        avg = round((avg / measurements) * 100) / 100
    return avg 


def createInfluxPMMeasurements(results):
    stats = json.loads(results['Stats'])
    print("Creating measurements for " + str(stats))
    time = datetime.datetime.utcfromtimestamp(stats['lastModified']/1000)
    baseMeasurement={
            "measurement" : "airquality",
            "tags" : {
                "location" : "Outside",
                "host" : results['Label'],
                "sensor" : "PurpleAir",
            },
            "time" : time
    }
    pm10=baseMeasurement.copy()
    pm10['fields'] = {"pm10" : float(results['pm1_0_atm_1'])}
    pm25=baseMeasurement.copy()
    pm25['fields'] = {"pm25" : float(results['pm2_5_atm_1'])}
    pm100=baseMeasurement.copy()
    pm100['fields'] = {"pm100" : float(results['pm10_0_atm_1'])}

    return [pm10, pm25, pm100]


try: 
    sensorID=os.environ['SENSOR_ID']
except:
    print("ERROR: SENSOR_ID environment variable is not defined. Exiting")
    sys.exit(1)

try: 
    influxURL=os.environ['INFLUX_URL']
except:
    print("ERROR: INFLUX_URL environment variable is not defined. Exiting")
    sys.exit(1)

try: 
    influxDBName=os.environ['INFLUX_DB']
except:
    print("ERROR: INFLUX_DBL environment variable is not defined. Exiting")
    sys.exit(1)

data = None
if testjson is None:
    with urllib.request.urlopen(url+str(sensorID)) as req:
        data = json.loads(req.read().decode())
else:
    data = json.loads(testjson)

if data is None or data['results'] is None:
    print("No valid data returned: "+str(data))
    sys.exit(0)


client = InfluxDBClient(host=influxURL)
client.switch_database(influxDBName)

results=data['results']

influxData=[]
for result in results:
    influxData = influxData + createInfluxPMMeasurements(result)

print("Fetched sensor values from PurpleAir: \n" + str(data))
print("Influx data is \n" + str(influxData))

client.write_points(influxData)
