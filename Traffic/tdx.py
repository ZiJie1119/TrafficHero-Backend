from fastapi import APIRouter
import json
import requests
from dotenv import load_dotenv
import os

# 讀取.env檔案中的變數
load_dotenv()

def get_data_response(url):
    auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
    app_id = os.getenv('TDX_app_id')
    app_key = os.getenv('TDX_app_key')
    auth = Auth(app_id, app_key)
    try:
        auth_response = requests.post(auth_url, auth.get_auth_header())
        d = Data(app_id, app_key, auth_response)
        data_response = requests.get(url, headers=d.get_data_header())
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return None
    data_all = json.loads(data_response.text)
    return data_all

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

class Data():
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
router = APIRouter(tags=["TDX"])

#TDX
@router.get("/serviceArea",summary="All the ServiceArea that has been provided on TDX")
async def serviceArea():
    url = "https://tdx.transportdata.tw/api/basic/v1/Parking/OffStreet/ParkingAvailability/Road/Freeway/ServiceArea?%24top=30&%24format=JSON"
    dataAll = get_data_response(url)
    serviceAreaSpace = []
    for service in dataAll["ParkingAvailabilities"]:
        # serviceAreaName.append(service["CarParkName"]["Zh_tw"])
        serviceAreaSpace.append(service["CarParkName"]["Zh_tw"]+"剩餘車位："+ str(service["AvailableSpaces"]))
    return {"serviceAreaSpace":serviceAreaSpace}

@router.get("/cityParking/{cityName}",summary="Taoyuan, Tainan, Kaohsiung, Keelung, YilanCounty, HualienCounty. These above are available country name")
async def cityParking(cityName):
    url = "https://tdx.transportdata.tw/api/basic/v1/Parking/OffStreet/ParkingAvailability/City/"+cityName+"?%24top=30&%24format=JSON"
    cityParkingSpace = []
    dataAll = get_data_response(url)
    for city in dataAll["ParkingAvailabilities"]:
        cityParkingSpace.append(city["CarParkName"]["Zh_tw"]+"剩餘車位："+ str(city["AvailableSpaces"]))
    return {"cityParkingSpace":cityParkingSpace}

@router.get("/sideParking/{cityName}",summary="All the sideParking that has been provided on TDX. NewTaipei, Tainan, HualienCounty")
async def sideParking(cityName):
    url = "https://tdx.transportdata.tw/api/basic/v1/Parking/OnStreet/ParkingSegmentAvailability/City/"+cityName+"?%24top=30&%24format=JSON"
    sideParkingSpace = []
    dataAll = get_data_response(url)
    for side in dataAll["CurbParkingSegmentAvailabilities"]:
        sideParkingSpace.append(side["ParkingSegmentName"]["Zh_tw"] +" 剩餘位置： " +str(side["AvailableSpaces"]))
    return {"sideParking":sideParkingSpace}