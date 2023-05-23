from fastapi import FastAPI
from FastAPI.metadata import tags_metadata
from OpenAI.ChatGPT import chatgpt
from shapely.geometry import Point
import math
import threading
from threading import *
from MongoDB.MongoDB import mycol
from Traffic.pbs import GeneratePoint
from Traffic import tdx
app = FastAPI()

# TDX
app.include_router(tdx.router, prefix="/tdx")

# PBS
# @app.on_event("startup")
# async def startup_event():
#     pbs.FetchData()
def get_key(dict,value):
    return [k for k,v in dict.items() if v == value]
#接收使用者的Lat&Lng
@app.get("/send_lat_lng")
async def send_lat_lng(lat: str, lng: str):
    return {"Inside the pos or not":setLatLng(lat,lng)}

# 判斷使用者經緯度有無在point2裡的每個點所生成的園內
def setLatLng(lat, lng):
    point = Point([lat, lng])
    msg = "" 
    # Detect whether the location is inside the point2 or not
    # 判斷使用者有沒有在圓內，如果有就回傳chatgpt處理過後的路況   
    for pos in GeneratePoint().values():
        print(pos)
        if (pos.contains(point)):
            print("Located！")
            doc = mycol.find_one({"EventLatLng":get_key(GeneratePoint(),pos)[0][0]+","+get_key(GeneratePoint(),pos)[0][1]})
            break
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