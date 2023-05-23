from MongoDB.MongoDB import mycol
import os
import urllib.request as req
import json
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from geopy.distance import geodesic


#讀取警廣API資料
def FetchData():
    url="https://data.moi.gov.tw/MoiOD/System/DownloadFile.aspx?DATA=36384FA8-FACF-432E-BB5B-5F015E7BC1BE"
    with req.urlopen(url) as res3:
        data =json.load(res3)
    #將資料庫清空    
    mycol.drop()
    #將事件插入資料庫
    evnLatLng = []
    for i in range(0,len(data)):
        if(data[i]['region'] == 'N' and data[i]['roadtype'] == '道路施工'):
            evnLatLng.append(data[i]['y1']+","+data[i]['x1'])
            mycol.insert_one({"_id":i,"type":"道路施工","place":data[i]['areaNm'],"UID":data[i]['UID'],"rdCondition":data[i]['comment'],"EventLatLng":data[i]['y1']+","+data[i]['x1']})
    # #只要有重複地點就刪除，只保留一個
    evnLatLng = []
    for item in mycol.find():
        if item['EventLatLng'] not in evnLatLng:  
            evnLatLng.append(item['EventLatLng'])  
        else:
            mycol.delete_one(item)
#取得重複的座標
def GetDupicate(L):
    return [e for e in set(L) if L.count(e) > 1]
#讀取DB內的事件座標再生成圓上的點
def GeneratePoint():
    points = [] 
    point2 = {}
    locationAll = []
    cursor = mycol.find({})
    for doc in cursor:
        locationAll.append(doc['EventLatLng'])
    #生成某點半徑 N 公里的圓上座標
    for loc in locationAll:
        tarlat = str(loc.split(",")[0]) #事件Lat
        tarlng = str(loc.split(",")[1]) #事件Lng
        for angle in range(0, 360, 60):
            # 生成某點 半徑 1 公里內的圓上的點
            points.append(geodesic(kilometers=0.5).destination((tarlat, tarlng),bearing = angle)) 
        for i in range(0,len(points)):
            point2[tarlat,tarlng] =  Polygon(points)
        points = []
    return point2