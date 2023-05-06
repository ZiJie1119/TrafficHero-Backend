import requests
from pprint import pprint
import json
import asyncio
import time
from fastapi import FastAPI
from auth.TDX import get_data_response
from metadata import tags_metadata
import subprocess


app = FastAPI(openapi_tags=tags_metadata)

#Websocket
@app.get("/send_lat_lng")
async def send_lat_lng(loc1: float, loc2: float):
    return sendLatLng(loc1, loc2)

def sendLatLng(loc1, loc2):
    command = ['python', 'geo.py', str(loc1), str(loc2)]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    if result.stdout:
        response = {'result': result.stdout.decode(errors='ignore').strip()}
    else:
        response = {'error': 'You don\'t offer args'}

    if result.stderr:
        error = result.stderr.decode(errors='ignore').strip()
        if error:
            print('stderr:', error)
            response['error'] = error
    return response

#TDX
@app.get("/serviceArea",tags=["serviceArea"])
async def serviceArea():
    url = "https://tdx.transportdata.tw/api/basic/v1/Parking/OffStreet/ParkingAvailability/Road/Freeway/ServiceArea?%24top=30&%24format=JSON"
    serviceAreaName = []
    serviceAreaSpace = []
    dataAll = get_data_response(url)
    for service in dataAll["ParkingAvailabilities"]:
        # serviceAreaName.append(service["CarParkName"]["Zh_tw"])
        serviceAreaSpace.append(service["CarParkName"]["Zh_tw"]+"剩餘車位："+ str(service["AvailableSpaces"]))
    return {"serviceAreaSpace":serviceAreaSpace}

@app.get("/cityParking/{cityName}",tags = ["cityParking"])
async def cityParking(cityName):
    url = "https://tdx.transportdata.tw/api/basic/v1/Parking/OffStreet/ParkingAvailability/City/"+cityName+"?%24top=30&%24format=JSON"
    cityParkingSpace = []
    dataAll = get_data_response(url)
    for city in dataAll["ParkingAvailabilities"]:
        cityParkingSpace.append(city["CarParkName"]["Zh_tw"]+"剩餘車位："+ str(city["AvailableSpaces"]))
    return {"cityParkingSpace":cityParkingSpace}

@app.get("/sideParking/{cityName}",tags = ["sideParking"])
async def sideParking(cityName):
    url = "https://tdx.transportdata.tw/api/basic/v1/Parking/OnStreet/ParkingSegmentAvailability/City/"+cityName+"?%24top=30&%24format=JSON"
    sideParkingSpace = []
    dataAll = get_data_response(url)
    for side in dataAll["CurbParkingSegmentAvailabilities"]:
        sideParkingSpace.append(side["ParkingSegmentName"]["Zh_tw"] +" 剩餘位置： " +str(side["AvailableSpaces"]))
    return {"sideParking":sideParkingSpace}

#Websocket-test
@app.get("/websocket")
async def websocket():
    command = ['node','index.js']
    process = subprocess.Popen(command)
    print(process.stdout)