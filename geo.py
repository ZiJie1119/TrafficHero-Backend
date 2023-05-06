#!/usr/bin/env python
# coding: utf-8




from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import math
from geopy.distance import geodesic
import sys
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.select import Select
from webdriver_manager.chrome import ChromeDriverManager
import requests
import json
import asyncio
import websockets
from selenium.webdriver.common.by import By
import openai
from dotenv import load_dotenv
import os
import sys
sys.path.append("../../")
from auth.TDX import Auth,Data,get_data_response

# 讀取.env檔案中的變數
load_dotenv()

browser = webdriver.Chrome(ChromeDriverManager().install())
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


# 處理抓下來的北部資料
for data in North:
    Info.append(data.text.split('\n'))
for size in range(0, len(Info)):
    if (Info[size][0] == "道路施工"):  # 限定 "道路施工"
        AddressTemp.append((Info[size][1]).split(" "))  # 地點
        RoadCondition.append(Info[size][2])  # 路況

# ----------地點處理轉換成經緯度，因為TDX的快速道路門牌對照API有格式要求----------#
for address in AddressTemp:
    Index = Index + 1
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
            # print(url)
            if (len(get_data_response(url)) != 0):
                locationAll.append(get_data_response(url))
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


# 判斷使用者經緯度有無在point2裡的每個點所生成的園內
def setLatLng(lat, lng):
    Count = 0
    point = Point([lat, lng])
    for p in point2:
        Count = Count + 1
        polygon = Polygon(p)
        # Detect whether the location is inside the point2 or not
        print(polygon.contains(point))
        # If contain in the polygon then send the rdCondition to user
        if (polygon.contains(point) == False):
            asyncio.get_event_loop().run_until_complete(
                sendRdCondition(RoadCondition[Count-1]))
            
# python 回傳至 webSocket
async def sendRdCondition(rdCondition):
    async with websockets.connect('ws://192.168.100.101:5004/getRdCondition') as websocket:
        #print(chatgpt(rdCondition))
        await websocket.send(rdCondition)

# ChatGPT
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


lat = eval(sys.argv[1])
lng = eval(sys.argv[2])
setLatLng(lat, lng)