
import paho.mqtt.client as mqtt
import pymongo
import json
from datetime import datetime
import logging
import time
# MongoDB setup
client = pymongo.MongoClient('mongodb+srv://ankurauti:ankurauti02@cluster0.7ikri.mongodb.net/indi_test?retryWrites=true&w=majority&appName=Cluster0')
db = client['indi_test']
event_table = db['events']

# MQTT setup with certificates
MQTT_BROKER = "a3uoz4wfsx2nz3-ats.iot.ap-south-1.amazonaws.com"  # Change this to your broker's hostname
MQTT_PORT = 8883  # Default secure port for MQTT
MQTT_TOPIC = "apm/server"

CA_CERT_PATH = '/home/ubuntu/AWS_Image_processing_git/processing_files/root-CA.crt'  # Replace with the path to your CA certificate
CLIENT_CERT_PATH = "/home/ubuntu/AWS_Image_processing_git/processing_files/test.cert.pem.crt"  # Replace with the path to your client certificate (optional)
CLIENT_KEY_PATH = '/home/ubuntu/AWS_Image_processing_git/processing_files/test.private.pem.key'  # Replace with the path to your client private key (optional)

# Create an MQTT client instance
mqtt_client = mqtt.Client()

# Set the MQTT username and password if required by the broker
# mqtt_client.username_pw_set(username="your_username", password="your_password")

# Setup TLS/SSL connection with certificates
mqtt_client.tls_set(ca_certs=CA_CERT_PATH, certfile=CLIENT_CERT_PATH, keyfile=CLIENT_KEY_PATH)

# Callback when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code: {rc}")

# mqtt_client.loop_start()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to AWS IoT")
    else:
        logging.error(f"Connection failed with code {rc}")

def on_publish(client, userdata, mid):
    logging.info(f"Message {mid} published.")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        logging.warning(f"Unexpected disconnection. Result code: {rc}")

# Set the callback for connection
mqtt_client.on_connect = on_connect
mqtt_client.on_connect = on_connect
mqtt_client.on_publish = on_publish
mqtt_client.on_disconnect = on_disconnect

# Connect to the broker
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Function to send data through MQTT and insert it into MongoDB
def cluster_database(metadata, label, score):
    score = round(float(score), 2)  # Round score to 2 decimal places
    # print("metadata_ts :  ",metadata['ts']*1000)
    payload = {
        "TS": metadata['ts'],
        "Type": 29,
        "DEVICE_ID": metadata['device_id'],
        "Details": {
            "Channel_name": label,
            "score": score
        }
    }
        
    # Publish to MQTT
    payload_json = json.dumps(payload)  # Convert the payload to JSON string
    mqtt_client.publish(MQTT_TOPIC, payload_json)
    print(f"Sent payload log detection to MQTT: {payload_json}")

def face_database(metadata, label, score):
    score = round(float(score), 2)  # Round score to 2 decimal places
    # print("metadata_ts :  ",metadata['ts']*1000)
    payload = {
        "TS": metadata['ts'],
        "Type": 29,
        "DEVICE_ID": metadata['device_id'],
        "Details": {
            "Face_name": label,
            "score": score
        }
    }

    # Publish to MQTT
    payload_json = json.dumps(payload)  # Convert the payload to JSON string
    mqtt_client.publish(MQTT_TOPIC, payload_json)
    print(f"Sent payload face detection to MQTT: {payload_json}")
