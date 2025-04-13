import os
import pymongo

client = pymongo.MongoClient(os.environ['CHANGE_STREAM_DB'])
#client.changestream.collection.insert_one({"_id":1, "hallo":"schnitzel"})
client.changestream.collection.update_one({"_id":1}, {"$set": {"elon": "mars"}})
#client.changestream.collection.replace_one({"_id":1}, {"bye": "world"})
#client.changestream.collection.delete_one({"_id":1})