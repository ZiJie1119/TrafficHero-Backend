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
from selenium.webdriver.common.by import By

# In[4]:

# The polygon was made of 65 point
# each point has its own lng,lat
# every triple of lng；120.5327、120.5318、120.5308 will differ 0.0010
# next triple of lng : 120.5299、120.5290、120.5281  will differ 0.0009


# point1 = Point([114.34605717658997,30.475584995561178])
# point2 = Point([120.53663880498414,23.690548816857273])
# polygon = Polygon(polygon_data)
# print(polygon.contains(point1))
browser = webdriver.Chrome(ChromeDriverManager().install())
browser.get("https://rtr.pbs.gov.tw/pbsmgt/RoadAll.html")
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
    
for data in North:
    Info.append(data.text.split('\n'))

for size in range(0,len(Info)):
    if(Info[size][0] == "道路施工"):
        AddressTemp.append((Info[size][1]).split(" "))
        
        
            
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


for address in AddressTemp:
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
    #https://api.opencube.tw/location/address?keyword=北部 [台61線((西濱快速))] 北上32.7km&key=AIzaSyC3JojC31oVXNGbGFDGa_7Q0pPwqvfIzlY
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
    except:
        browser.close()
# browser.close()

for loc in locationAll:
    tarlat = str(loc[0]["Lat"])
    tarlng = str(loc[0]["Lon"])
    for i in range(0, 360, 360//80):
        lat_new, lng_new, _ = geodesic(kilometers=1).destination((tarlat, tarlng), i)
        points.append([lat_new, lng_new])
    point2.append(points)

def setLatLng(lat,lng):
    point = Point([lat,lng])
    for p in point2:
        polygon = Polygon(p)
        print(polygon.contains(point))
    
lat = eval(sys.argv[1])
lng = eval(sys.argv[2])
setLatLng(lat,lng)

# In[ ]:




