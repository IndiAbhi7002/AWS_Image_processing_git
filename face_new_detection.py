import pymongo
import base64
from PIL import Image
from io import BytesIO
import time
from processing_files.face_processing import get_frame

# Connect to MongoDB
client = pymongo.MongoClient('mongodb+srv://ankurauti:ankurauti02@cluster0.7ikri.mongodb.net/logo_base?retryWrites=true&w=majority&appName=Cluster0')
db = client['logo_base']
events_table_logo_base = db['events']

# Function to decode and display base64 image
def display_image_from_base64(base64_str):
    img_data = base64.b64decode(base64_str)
    return Image.open(BytesIO(img_data))

# Keep track of the last processed document's _id
last_processed_id = None

# Batch size for efficient data fetching
batch_size = 100

while True:
    # Build the query
    query = {'_id': {'$gt': last_processed_id}} if last_processed_id else {}

    try:
        # Fetch documents in batches without sorting
        documents = events_table_logo_base.find(
            query,
            {'TS': 1, 'DEVICE_ID': 1, '_id': 1, 'Details.image': 1, 'Event_Name': 1}
        ).limit(batch_size)

        # Check if no new data is found
        has_data = False
        for doc in documents:
            has_data = True
            device_id = doc.get('DEVICE_ID')
            event_name = doc.get('Event_Name')
            ts = doc.get('TS')
            image_base64 = doc.get('Details', {}).get('image')

            if image_base64:
                decode_start_time = time.time()
                metadata = {
                    'device_id': device_id,
                    'event_name': event_name,
                    'ts': ts,
                }
                image = display_image_from_base64(image_base64)
                decode_end_time = time.time()
                print(f"Time taken to decode the image: {decode_end_time - decode_start_time:.4f} seconds")
                get_frame(image, metadata)

            # Update the last processed ID
            last_processed_id = doc['_id']

        if not has_data:
            print("No new data found, waiting for new entries...")
            time.sleep(5)

    except pymongo.errors.PyMongoError as e:
        print(f"Database error: {e}")

    # Optional: Pause briefly between iterations
    time.sleep(1)
