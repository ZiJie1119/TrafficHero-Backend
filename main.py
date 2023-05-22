from fastapi import FastAPI
from FastAPI.metadata import tags_metadata
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import math
from geopy.distance import geodesic
import threading
from threading import *
from Traffic import tdx, pbs

app = FastAPI()

# TDX
app.include_router(tdx.router, prefix="/tdx")

# PBS
# @app.on_event("startup")
# async def startup_event():
#     pbs.FetchData()


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
        # 判斷使用者有沒有在圓內，如果有就回傳chatgpt處理過後的路況
    if (polygon.contains(point)):
        print("Located！")
        doc = mycol.find_one({"EventLatLng":str(lat)+","+str(lng)})
        msg = "地點："+doc['place'] +'\n'+ chatgpt(doc['rdCondition'])
    print(msg)
    return (msg)

# #固定幾秒觸發事件
# def set_interval(func, sec):
#     def func_wrapper():
#         set_interval(func, sec)
#         func()
#     t = threading.Timer(sec, func_wrapper)
#     t.start()
#     return t
# set_interval(FetchData,10)