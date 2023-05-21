
import urllib.request as req
import json 
from fastapi import FastAPI
from auth.TDX import get_data_response
from metadata import tags_metadata
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import math
from geopy.distance import geodesic
import openai
from dotenv import load_dotenv
import pymongo
import os
import threading
from threading import *

app = FastAPI(openapi_tags=tags_metadata)
#pymongo
myclient = pymongo.MongoClient(os.getenv('MongoDB_URI'))
mydb = myclient.TrafficHero
mycol = mydb["pbs"]
locationAll = []
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

@app.get("/reviseDB/{ID},{Content}")
async def reviseDB(ID,Content):
    if(Content != ""):
        mycol.update_one({"_id":ID},{"$set":{"rdCondition":Content}})
    for doc in mycol.find():
        print(doc)
#ChatGPT
def chatgpt(str):
    openai.api_key = app_id = os.getenv('OpenAI_Key')
    user = str + "。幫我分類出時間及事件"
    if user:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "我需要用繁體中文輸出"},
                {"role": "user", "content": user},
            ]
        )
        return (response['choices'][0]['message']['content'])
#讀取警廣API資料
def FetchData():
    url="https://data.moi.gov.tw/MoiOD/System/DownloadFile.aspx?DATA=36384FA8-FACF-432E-BB5B-5F015E7BC1BE"
    with req.urlopen(url) as res3:
        data =json.load(res3)
    #將資料庫清空    
    mycol.drop()
    evnLatLng = []
    for i in range(0,len(data)):
        if(data[i]['region'] == 'N' and data[i]['roadtype'] == '道路施工'):
            evnLatLng.append(data[i]['y1']+","+data[i]['x1'])
            mycol.insert_one({"_id":i,"type":"道路施工","place":data[i]['areaNm'],"happenDate":data[i]['modDttm'],"rdCondition":data[i]['comment'],"EventLatLng":data[i]['y1']+","+data[i]['x1']})
     #只要有重複地點就刪除
    for duplicate in GetDupicate(evnLatLng):
        mycol.delete_many({"EventLatLng":duplicate})
#取得重複的座標
def GetDupicate(L):
    return [e for e in set(L) if L.count(e) > 1]
#讀取DB內的事件座標再生成圓上的點
def GeneratePoint():
    points = []
    point2 = []
    cursor = mycol.find({})
    for doc in cursor:
        locationAll.append(doc['EventLatLng'])
    #生成某點半徑 N 公里的圓上座標
    for loc in locationAll:
        tarlat = str(loc.split(",")[0])
        tarlng = str(loc.split(",")[1])
        for i in range(0, 360, 360//80):
            lat_new, lng_new, _ = geodesic(kilometers=1).destination((tarlat, tarlng), i)  # 生成某點 半徑 1 公里內的圓上的點
            points.append([lat_new, lng_new])
        point2.append(points)  # 用每個點來製造圓並存進point2
        points.clear
    return point2
#接收使用者的Lat&Lng
@app.get("/send_lat_lng")
async def send_lat_lng(lat: float, lng: float):
    return {"Inside the pos or not":setLatLng(lat,lng)}
# 判斷使用者經緯度有無在point2裡的每個點所生成的園內
def setLatLng(lat, lng):
    Count = 0
    point = Point([lat, lng])
    msg = ""
    for p in GeneratePoint():
        Count = Count + 1
        polygon = Polygon(p)
        # Detect whether the location is inside the point2 or not
        # If contain in the polygon then send the rdCondition to user
    if (polygon.contains(point)):
        print("Located！")
        doc = mycol.find_one({"EventLatLng":str(lat)+","+str(lng)})
        msg = "地點："+doc['place'] +'\n'+ chatgpt(doc['rdCondition'])
    print(msg)
    return (msg)

#固定幾秒觸發事件
def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t
set_interval(FetchData,10)       