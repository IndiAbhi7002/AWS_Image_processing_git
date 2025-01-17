import pymongo
import requests
from datetime import datetime
client = pymongo.MongoClient('mongodb+srv://ankurauti:ankurauti02@cluster0.7ikri.mongodb.net/indi_test?retryWrites=true&w=majority&appName=Cluster0')
# client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['indi_test']        
event_table = db['events']

def cluster_database(metadata,label, score):
    score = round(float(score), 2)  # Round score to 2 decimal places
    payload = {
        "timestamp": datetime.now(),
        "TS": metadata['ts'],
        # "TS": ts_for_db_converted,
        # "Type": metadata['Type'],
        "Type": 29,
        "DEVICE_ID": metadata['device_id'],
        # "timestamp": str(metadata['timestamp']),
        "Details": {
            "Channel_name": label,
            "score": score
        }
    }
    
    existing_record = event_table.find_one({
        "TS": payload["TS"],
        "Type": payload["Type"],
        "DEVICE_ID": payload["DEVICE_ID"],
    
    })
    
    if existing_record:

        print("Record already exists in the database. Skipping insertion.")
    else:
        # Insert the payload into the database
        event_table.insert_one(payload)
        print(f"Inserted payload: {payload}")


# def cluster_database(metadata,label,score):
#     score = round(float(score), 2)  # Round score to 2 decimal places
#     # payload = {"TS":str(metadata['ts']),"Type":29,"DEVICE_ID":metadata['device_id'],"Details":{"Channel_name":label,'score':score}}
#     payload = {"TS":metadata['ts'],"Type":29,"DEVICE_ID":metadata['device_id'],"Details":{"Channel_name":label,'score':score}}
#     print(f"payload:{payload}")
#     event_table.insert_one(payload)  