import requests
from pprint import pprint
import json
import asyncio
import time
from fastapi import FastAPI
from auth.TDX import get_data_response
from metadata import tags_metadata
import subprocess
import time
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import math
from geopy.distance import geodesic
import sys
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.select import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests
import json
import asyncio
import websockets
from selenium.webdriver.common.by import By
import openai
from dotenv import load_dotenv
import pymongo
import os
import sys
import threading
from threading import *

app = FastAPI(openapi_tags=tags_metadata)
pointAll = []
#TDX
@app.get("/serviceArea",tags=["serviceArea"])
async def serviceArea():
    url = "https://tdx.transportdata.tw/api/basic/v1/Parking/OffStreet/ParkingAvailability/Road/Freeway/ServiceArea?%24top=30&%24format=JSON"
    dataAll = get_data_response(url)
    serviceAreaSpace = []
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

# #Websocket
@app.get("/websocket")
async def websocket():
    command = ['node','index.js']
    process = subprocess.Popen(command)
    print(process.stdout)



def chatgpt(str):
    openai.api_key = app_id = os.getenv('OpenAI_Key')
    user = str + "。幫我分類出地點、時間及事件"
    if user:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "我需要用繁體中文輸出"},
                {"role": "user", "content": user},
            ]
        )
        return (response['choices'][0]['message']['content'])
def Crawling():
    #pymongo
    myclient = pymongo.MongoClient(os.getenv('MongoDB_URI'))
    mydb = myclient.TrafficHero
    mycol = mydb["pbs"]

    # 讀取.env檔案中的變數
    load_dotenv()

    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service)
    browser.get("https://rtr.pbs.gov.tw/pbsmgt/RoadAll.html")

    # 透過selenium抓東、南、西、北的路況
    RoadInfo = browser.find_elements(By.NAME, 'tr')
    East = browser.find_elements(By.NAME, 'E')
    West = browser.find_elements(By.NAME, 'W')
    North = browser.find_elements(By.NAME, 'N')
    South = browser.find_elements(By.NAME, 'S')
    Info = []
    AddressTemp = []
    locationAll = []
    points = []
    point2 = []
    RoadCondition = []  # 路況說明
    Index = 0
    RdCount = []


    # 處理抓下來的北部資料
    for data in North:
        Info.append(data.text.split('\n'))

    #將資料庫清空    
    mycol.drop()

    for size in range(0, len(Info)):
        if (Info[size][0] == "道路施工"):  # 限定 "道路施工"
            mycol.insert_one({"type":"道路施工","place":[],"rdCondition":Info[size][2],"EventLat&Lng":[]})
            AddressTemp.append((Info[size][1]).split(" "))  # 地點
            RoadCondition.append(Info[size][2])  # 路況
            RdCount.append(size)
    # ----------地點處理轉換成經緯度，因為TDX的快速道路門牌對照API有格式要求----------#
    for address in AddressTemp:
        Index = Index + 1
        try:
            mycol.update_one({"rdCondition":RoadCondition[Index-1]},{"$set":{"place":"".join(address)}})
        except:
            next
        address[1] = address[1].replace("[", "")
        address[1] = address[1].replace("]", "")
        address[1] = address[1].replace(address[1][-8:], "")
        address[2] = address[2].replace("km", "")
        direction = address[2][0:2]
        mileage = address[2][2:]
        try:
            if (mileage != ''):
                # Send to TDX API process
                mileage = float(mileage)
                mileageK = int(mileage)  # 整數里程
                mileageF1 = math.ceil((mileage-mileageK)*1000)  # 小數里程
                if (mileageF1 == 0):
                    mileageF1 = "000"
                    mileageF2 = "100"
                else:
                    mileageF2 = int(mileageF1+100)
                    mileageF1 = str(mileageF1)
                # address[1]：快速道路 、 address[2]：地點+里程 、 mileage：里程 、 direction：方向、mileageK：整數里程、mileageF1、F2：小數里程
                url = 'https://tdx.transportdata.tw/api/basic/V3/Map/Road/Sign/RoadClass/1/RoadName/' +address[1]+'/'+str(mileageK)+'K+'+mileageF1+'/to/'+str(mileageK)+'K+'+str(mileageF2)+'?%24top=1&%24format=JSON'
                if (len(get_data_response(url)) != 0):
                    loc = get_data_response(url)
                    locationAll.append(loc)
                    #插入事件地點
                    mycol.update_one({"rdCondition":RoadCondition[Index-1]},{"$set":{"EventLat&Lng":str(loc[0]["Lat"])+","+str(loc[0]["Lon"])}}) 
                else:
                    try:
                        RoadCondition.pop(Index)
                    except:
                        next
        except:
            browser.close()
            
    #生成某點半徑 N 公里的圓上座標
    for loc in locationAll:
        tarlat = str(loc[0]["Lat"])
        tarlng = str(loc[0]["Lon"])
        for i in range(0, 360, 360//80):
            lat_new, lng_new, _ = geodesic(kilometers=1).destination(
                (tarlat, tarlng), i)  # 生成某點 半徑 1 公里內的圓上的點
            points.append([lat_new, lng_new])
        point2.append(points)  # 用每個點來製造圓並存進point2
    pointAll = point2

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

#Websocket
@app.get("/send_lat_lng")
async def send_lat_lng(lat: str, lng: str):
    return setLatLng(lat,lng)
# 判斷使用者經緯度有無在point2裡的每個點所生成的園內
def setLatLng(lat, lng):
    Count = 0
    point = Point([lat, lng])
    for p in pointAll:
        Count = Count + 1
        polygon = Polygon(p)
        # Detect whether the location is inside the point2 or not
        print(polygon.contains(point))
        # If contain in the polygon then send the rdCondition to user
        if (polygon.contains(point) == False):
            print("False")

set_interval(Crawling,60)
# set_interval(Crawling,240)        