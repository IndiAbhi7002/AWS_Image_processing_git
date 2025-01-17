import pymongo
import base64
from PIL import Image
from io import BytesIO
import time
from processing_files.image_processing import process_image_data
from processing_files.face_processing import get_frame
# Connect to MongoDB using the provided connection string
client = pymongo.MongoClient('mongodb+srv://ankurauti:ankurauti02@cluster0.7ikri.mongodb.net/logo_base?retryWrites=true&w=majority&appName=Cluster0')
# client = pymongo.MongoClient('mongodb://localhost:27017/')

# Select the 'logo_base' database
db = client['logo_base']

# Select the 'events' collection
events_table_logo_base = db['events']

# Function to decode and display base64 image
def display_image_from_base64(base64_str):
    # Decode base64 string
    img_data = base64.b64decode(base64_str)
    # Convert the byte data to an image
    image = Image.open(BytesIO(img_data))
    return image
# Keep track of the last processed document's _id to avoid fetching the same data again
last_processed_id = None

# Continuous fetch in while loop
while True:
    # Fetch the next document based on the last processed _id (if any)
    query = {}
    if last_processed_id:
        query = {'_id': {'$gt': last_processed_id}}  # Only fetch documents with _id greater than the last processed one

    fetch_start_time = time.time()


    # Fetch documents from the 'events' collection, sorted by timestamp, device_id, and _id
    documents = events_table_logo_base.find(query).sort([('TS', 1), ('DEVICE_ID', 1), ('_id', 1)])
    fetch_end_time = time.time()  # End timing the database fetch operation
    print(f"Time taken to fetch data from database: {fetch_end_time - fetch_start_time:.4f} seconds")

    # Check if any documents were returned
    if events_table_logo_base.count_documents(query) == 0:
        print("No new data found, waiting for new entries...")
        time.sleep(5)  # Wait for 5 seconds before checking again
        continue

    # Iterate over the fetched documents
    for doc in documents:

        device_id = doc.get('DEVICE_ID')
        event_name = doc.get('Event_Name')
        ts = doc.get('TS')
        # Type= doc.get("Type")
        image_base64 = doc.get('Details', {}).get('image')
        # print(f"ts : {ts} : tytpe {type(ts)}")
        if image_base64:
            decode_start_time = time.time()

            # Create a dictionary with metadata
            metadata = {
                # 'timestamp': timestamp,
                'device_id': device_id,
                'event_name': event_name,
                'ts': ts,
                # 'Type': Type
            }

            # Decode and display the image
            image = display_image_from_base64(image_base64)
            decode_end_time = time.time()

            print(f"Time taken to decode the image: {decode_end_time - decode_start_time:.4f} seconds")
            # Pass the image and metadata to the process function
            process_image_data(image, metadata)

            # get_frame(image,metadata)
            
            # Update the last processed _id
            last_processed_id = doc['_id']

    # Optional: Pause the loop for a short time before fetching again
    # time.sleep(1)  # Wait for 1 second before checking for new data
