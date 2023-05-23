import pymongo
import os
#pymongo
myclient = pymongo.MongoClient(os.getenv('MongoDB_URI'))
mydb = myclient.TrafficHero
mycol = mydb["pbs"]