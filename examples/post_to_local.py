#!/usr/bin/env python3
'''
Get data from sensors and write it to InfluxDB

Requires:
    influxdb - pip install influxdb


** Docker InfluxDB & Grafana guide **

Download container
$ docker pull samuelebistoletti/docker-statsd-influxdb-grafana

Create and start new container
$ docker run -d --name docker-statsd-influxdb-grafana -p 3003:3003 -p 3004:8083 -p 8086:8086 -p 22022:22 -p 8125:8125/udp samuelebistoletti/docker-statsd-influxdb-grafana:latest

Or start existing container
$ docker start docker-statsd-influxdb-grafana

InfluxDB: http://localhost:3004/

First create new database: CREATE DATABASE ruuvi
Query to return all tag data: SELECT * FROM ruuvi_measurements
Remove all data: DROP SERIES FROM ruuvi_measurements

Grafana: http://localhost:3003/ (root/root)

Add datasource (type: InfluxDB url: http://localhost:8086, database: ruuvi)
Add new graph to dashboard
'''

from influxdb import InfluxDBClient
from ruuvitag_sensor.ruuvi import RuuviTagSensor


def convert_to_influx(mac, payload):
    '''
    Convert data into RuuviCollector naming schme and scale

    returns:
        Object to be written to InfluxDB
    '''
    dataFormat = payload["data_format"] if ('data_format' in payload) else None
    fields = {}
    fields["temperature"]               = payload["temperature"] if ('temperature' in payload) else None
    fields["humidity"]                  = payload["humidity"] if ('humidity' in payload) else None
    fields["pressure"]                  = payload["pressure"] if ('pressure' in payload) else None
    fields["accelerationX"]             = payload["acceleration_x"]/1000.0 if ('acceleration_x' in payload) else None
    fields["accelerationY"]             = payload["acceleration_y"]/1000.0 if ('acceleration_y' in payload) else None
    fields["accelerationZ"]             = payload["acceleration_z"]/1000.0 if ('acceleration_z' in payload) else None
    fields["batteryVoltage"]            = payload["battery"]/1000.0 if ('battery' in payload) else None
    fields["p_rssi"]                    = payload["p_rssi"]/1000.0 if ('p_rssi' in payload) else None
    fields["v_cap"]        = payload["v_cap"]/1000.0 if ('v_cap' in payload) else None
    fields["txPower"]                   = payload["tx_power"] if ('tx_power' in payload) else None
    fields["movementCounter"]           = payload["movement_counter"] if ('movement_counter' in payload) else None
    fields["measurementSequenceNumber"] = payload["measurement_sequence_number"] if ('measurement_sequence_number' in payload) else None
    fields["tagID"]                     = payload["tagID"] if ('tagID' in payload) else None
    fields["rssi"]                      = payload["rssi"] if ('rssi' in payload) else None
    return {
        "measurement": "ruuvi_measurements",
        "tags": {
            "mac": mac.replace(':',''),
            "dataFormat": dataFormat
        },
        "fields": fields
    }


client = InfluxDBClient(host="localhost", port=8086, database="ruuvi")

def handle_data(data):
    json_body = [convert_to_influx(data[0], data[1])] 
    client.write_points(json_body)


RuuviTagSensor.get_datas(handle_data)