import pymongo
import os
import urllib.request as req
import json

#pymongo
myclient = pymongo.MongoClient(os.getenv('MongoDB_URI'))
mydb = myclient.TrafficHero
mycol = mydb["pbs"]
locationAll = []

#讀取警廣API資料
def FetchData():
    url="https://od.moi.gov.tw/MOI/v1/pbs"
    with req.urlopen(url) as res3:
        data =json.load(res3)
    #將資料庫清空    
    mycol.drop()
    #將事件插入資料庫
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
    point2 = [] # 用每個點來製造圓並存進point2
    cursor = mycol.find({})
    for doc in cursor:
        locationAll.append(doc['EventLatLng'])
    #生成某點半徑 N 公里的圓上座標
    for loc in locationAll:
        tarlat = str(loc.split(",")[0]) #事件Lat
        tarlng = str(loc.split(",")[1]) #事件Lng
        for i in range(0, 360, 360//80):
            lat_new, lng_new, _ = geodesic(kilometers=1).destination((tarlat, tarlng), i)  # 生成某點 半徑 1 公里內的圓上的點
            points.append([lat_new, lng_new])
        point2.append(points)  
        points.clear
    return point2