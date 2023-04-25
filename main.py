import requests
from pprint import pprint
import json
from fastapi import FastAPI

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

# ----------Verify the TDX Account----------#
app_id = 'b10923015-1aa2500a-b917-4539'
app_key = '009cb4d7-a507-47f1-bab6-7da5182e6e95'
auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
class Auth():
    def __init__(self, app_id, app_key):
        self.app_id = app_id
        self.app_key = app_key

    def get_auth_header(self):
        content_type = 'application/x-www-form-urlencoded'
        grant_type = 'client_credentials'

        return {
            'content-type': content_type,
            'grant_type': grant_type,
            'client_id': self.app_id,
            'client_secret': self.app_key
        }
class data():
    def __init__(self, app_id, app_key, auth_response):
        self.app_id = app_id
        self.app_key = app_key
        self.auth_response = auth_response
    def get_data_header(self):
        auth_JSON = json.loads(self.auth_response.text)
        access_token = auth_JSON.get('access_token')
        return {
            'authorization': 'Bearer '+access_token
    }

def response(url):
    data_response = ""
    try:
        d = data(app_id, app_key, auth_response)
        data_response = requests.get(url, headers=d.get_data_header())
    except:
        a = Auth(app_id, app_key)
        auth_response = requests.post(auth_url, a.get_auth_header())
        d = data(app_id, app_key, auth_response)
        data_response = requests.get(url, headers=d.get_data_header())
    dataAll = json.loads(data_response.text)
    return dataAll
# ----------Verify the TDX Account----------#

@app.get("/serviceArea",tags=["serviceArea"])
async def serviceArea():
    url = "https://tdx.transportdata.tw/api/basic/v1/Parking/OffStreet/ParkingAvailability/Road/Freeway/ServiceArea?%24top=30&%24format=JSON"
    serviceAreaName = []
    serviceAreaSpace = []
    dataAll = response(url)
    for service in dataAll["ParkingAvailabilities"]:
        # serviceAreaName.append(service["CarParkName"]["Zh_tw"])
        serviceAreaSpace.append(service["CarParkName"]["Zh_tw"]+"剩餘車位："+ str(service["AvailableSpaces"]))
    return {"serviceAreaSpace":serviceAreaSpace}

@app.get("/cityParking/{cityName}",tags = ["cityParking"])
async def cityParking(cityName):
    url = "https://tdx.transportdata.tw/api/basic/v1/Parking/OffStreet/ParkingAvailability/City/"+cityName+"?%24top=30&%24format=JSON"
    cityParkingSpace = []
    dataAll = response(url)
    for city in dataAll["ParkingAvailabilities"]:
        cityParkingSpace.append(city["CarParkName"]["Zh_tw"]+"剩餘車位："+ str(city["AvailableSpaces"]))
    return {"cityParkingSpace":cityParkingSpace}

@app.get("/sideParking/{cityName}",tags = ["sideParking"])
async def sideParking(cityName):
    url = "https://tdx.transportdata.tw/api/basic/v1/Parking/OnStreet/ParkingSegmentAvailability/City/"+cityName+"?%24top=30&%24format=JSON"
    sideParkingSpace = []
    dataAll = response(url)
    for side in dataAll["CurbParkingSegmentAvailabilities"]:
        sideParkingSpace.append(side["ParkingSegmentName"]["Zh_tw"] +" 剩餘位置： " +str(side["AvailableSpaces"]))
    return {"sideParking":sideParkingSpace}