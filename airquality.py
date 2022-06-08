#!/usr/local/bin/python3

import urllib.request
import json
import os
import sys
import datetime
from influxdb import InfluxDBClient

url="https://api.purpleair.com/v1/sensors/%s?api_key=%s&fields=name%%2Cpm1.0_atm%%2Cpm2.5_atm%%2Cpm10.0_atm"
apiKeyPath="/run/secrets/apikey"

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
    stats = results
    print("Creating measurements for " + str(stats))
    time = datetime.datetime.utcfromtimestamp(results['data_time_stamp']/1000)
    sensor = results['sensor']
    baseMeasurement={
            "measurement" : "airquality",
            "tags" : {
                "location" : "Outside",
                "host" : sensor['name'],
                "sensor" : "PurpleAir",
            },
            "time" : time
    }
    pm10=baseMeasurement.copy()
    pm10['fields'] = {"pm10" : float(sensor['pm1.0_atm'])}
    pm25=baseMeasurement.copy()
    pm25['fields'] = {"pm25" : float(sensor['pm2.5_atm'])}
    pm100=baseMeasurement.copy()
    pm100['fields'] = {"pm100" : float(sensor['pm10.0_atm'])}

    return [pm10, pm25, pm100]


try: 
    sensorID=os.environ['SENSOR_ID']
except:
    print("ERROR: SENSOR_ID environment variable is not defined. Exiting")
    sys.exit(1)

try: 
    apiKeyFile=open(apiKeyPath, 'r')
    apiKey=apiKeyFile.readline().rstrip()
    apiKeyFile.close()
except:
    print("ERROR: API key does not exist at " + apiKeyPath + ". Exiting")
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
    fullURL = url % (sensorID, apiKey)
    with urllib.request.urlopen(fullURL) as req:
        data = json.loads(req.read().decode())
else:
    data = json.loads(testjson)

if data is None or data['sensor'] is None:
    print("No valid data returned: "+str(data))
    sys.exit(0)

print(data)

client = InfluxDBClient(host=influxURL)
client.switch_database(influxDBName)

influxData=[]
influxData = influxData + createInfluxPMMeasurements(data)

print("Fetched sensor values from PurpleAir: \n" + str(data))
print("Influx data is \n" + str(influxData))

#client.write_points(influxData)
