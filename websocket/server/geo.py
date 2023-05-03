#!/usr/bin/env python
# coding: utf-8

# In[1]:


from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import math
from geopy.distance import geodesic
import sys;
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.select import Select
from webdriver_manager.chrome import ChromeDriverManager
import requests
import json
import asyncio
import websockets
from selenium.webdriver.common.by import By
# import openai

# openai.my_api_key = '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'
browser = webdriver.Chrome(ChromeDriverManager().install())
browser.get("https://rtr.pbs.gov.tw/pbsmgt/RoadAll.html")

#透過selenium抓東、南、西、北的路況
RoadInfo = browser.find_elements(By.NAME,'tr')
East = browser.find_elements(By.NAME,'E')
West = browser.find_elements(By.NAME,'W')
North = browser.find_elements(By.NAME,'N')
South = browser.find_elements(By.NAME,'S')
Info = []
AddressTemp = []
locationAll= []
points = []
point2 = []
RoadCondition = [] #路況說明
Index = 0


#處理抓下來的北部資料
for data in North:
    Info.append(data.text.split('\n'))
for size in range(0,len(Info)):
    if(Info[size][0] == "道路施工"): #限定 "道路施工"
        AddressTemp.append((Info[size][1]).split(" ")) #地點
        RoadCondition.append(Info[size][2]) #路況
        
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
# ----------Verify the TDX Account----------#         

# ----------地點處理轉換成經緯度，因為TDX的快速道路門牌對照API有格式要求----------# 
for address in AddressTemp:
    Index = Index + 1
    address[1] = address[1].replace("[","")
    address[1] = address[1].replace("]","")
    address[1] = address[1].replace(address[1][-8:],"")
    address[2] = address[2].replace("km","")
    direction = address[2][0:2]
    mileage = address[2][2:]
    
    try:
        if(mileage !=''):
            ##Send to TDX API process    
            mileage = float(mileage)
            mileageK = int(mileage) #整數里程
            mileageF1 = math.ceil((mileage-mileageK)*1000) #小數里程
            if(mileageF1 == 0):
                mileageF1 = "000"
                mileageF2 = "100"
            else:
                mileageF2 = int(mileageF1+100)
                mileageF1 = str(mileageF1)        
            # address[1]：快速道路 、 address[2]：地點+里程 、 mileage：里程 、 direction：方向、mileageK：整數里程、mileageF1、F2：小數里程
            url = 'https://tdx.transportdata.tw/api/basic/V3/Map/Road/Sign/RoadClass/1/RoadName/'+address[1]+'/'+str(mileageK)+'K+'+mileageF1+'/to/'+str(mileageK)+'K+'+str(mileageF2)+'?%24top=1&%24format=JSON'
            # print(url)
            try:
                d = data(app_id, app_key, auth_response)
                data_response = requests.get(url, headers=d.get_data_header())
            except:
                a = Auth(app_id, app_key)
                auth_response = requests.post(auth_url, a.get_auth_header())
                d = data(app_id, app_key, auth_response)
                data_response = requests.get(url, headers=d.get_data_header())
            if(len(json.loads(data_response.text)) != 0):
                locationAll.append(json.loads(data_response.text))
            else:
                try:
                    RoadCondition.pop(Index)
                except:
                    next          
    except:
        browser.close()


for loc in locationAll:
    tarlat = str(loc[0]["Lat"])
    tarlng = str(loc[0]["Lon"])
    # print(str(tarlat)+" "+str(tarlng))
    for i in range(0, 360, 360//80):
        lat_new, lng_new, _ = geodesic(kilometers=1).destination((tarlat, tarlng), i) #生成某點 半徑 1 公里內的圓上的點
        points.append([lat_new, lng_new])
    point2.append(points) # Use each point to make circle, and store into point2

#python 回傳 webSocket
async def sendRdCondition(rdCondition):
    async with websockets.connect('ws://192.168.100.101:5004/getRdCondition') as websocket:
        await websocket.send(rdCondition)
        websocket.close() 
        


def setLatLng(lat,lng):
    Count = 0
    point = Point([lat,lng])
    for p in point2:
        Count = Count + 1
        polygon = Polygon(p)
        print(polygon.contains(point)) # Detect whether the location is inside the point2 or not
        if(polygon.contains(point) == False): # If contain in the polygon then send the rdCondition to user
            
            asyncio.get_event_loop().run_until_complete(sendRdCondition(RoadCondition[Count-1]))
            
lat = eval(sys.argv[1])
lng = eval(sys.argv[2])
setLatLng(lat,lng)

# In[ ]:




