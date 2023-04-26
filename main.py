import requests
from pprint import pprint
import json
from fastapi import FastAPI
from auth import get_data_response

tags_metadata = [
    {
        "name": "serviceArea",
        "description": "All the ServiceArea that has been provided on TDX"
    },
    {
        "name": "cityParking",
        "description": "Taoyuan, Tainan, Kaohsiung, Keelung, YilanCounty, HualienCounty. These above are available country name"
    },
    {
        "name": "sideParking",
        "description": "All the sideParking that has been provided on TDX. NewTaipei, Tainan, HualienCounty"
    }, 
]
app = FastAPI(openapi_tags=tags_metadata)

app_id = 'b10923015-1aa2500a-b917-4539'
app_key = '009cb4d7-a507-47f1-bab6-7da5182e6e95'

@app.get("/serviceArea",tags=["serviceArea"])
async def serviceArea():
    url = "https://tdx.transportdata.tw/api/basic/v1/Parking/OffStreet/ParkingAvailability/Road/Freeway/ServiceArea?%24top=30&%24format=JSON"
    serviceAreaName = []
    serviceAreaSpace = []
    dataAll = get_data_response(app_id, app_key, url)
    for service in dataAll["ParkingAvailabilities"]:
        # serviceAreaName.append(service["CarParkName"]["Zh_tw"])
        serviceAreaSpace.append(service["CarParkName"]["Zh_tw"]+"剩餘車位："+ str(service["AvailableSpaces"]))
    return {"serviceAreaSpace":serviceAreaSpace}

@app.get("/cityParking/{cityName}",tags = ["cityParking"])
async def cityParking(cityName):
    url = "https://tdx.transportdata.tw/api/basic/v1/Parking/OffStreet/ParkingAvailability/City/"+cityName+"?%24top=30&%24format=JSON"
    cityParkingSpace = []
    dataAll = get_data_response(app_id, app_key, url)
    for city in dataAll["ParkingAvailabilities"]:
        cityParkingSpace.append(city["CarParkName"]["Zh_tw"]+"剩餘車位："+ str(city["AvailableSpaces"]))
    return {"cityParkingSpace":cityParkingSpace}

@app.get("/sideParking/{cityName}",tags = ["sideParking"])
async def sideParking(cityName):
    url = "https://tdx.transportdata.tw/api/basic/v1/Parking/OnStreet/ParkingSegmentAvailability/City/"+cityName+"?%24top=30&%24format=JSON"
    sideParkingSpace = []
    dataAll = get_data_response(app_id, app_key, url)
    for side in dataAll["CurbParkingSegmentAvailabilities"]:
        sideParkingSpace.append(side["ParkingSegmentName"]["Zh_tw"] +" 剩餘位置： " +str(side["AvailableSpaces"]))
    return {"sideParking":sideParkingSpace}