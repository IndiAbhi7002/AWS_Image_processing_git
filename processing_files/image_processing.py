import os
import tensorflow as tf
import cv2
import numpy as np
from models.object_detection.utils import label_map_util
from datetime import datetime ,timezone
import re
from processing_files.mqtt_database import cluster_database
import time
# Suppress TensorFlow logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Directory and Path Setup
current_dir = os.getcwd()

# Constants
MIN_CONF_THRESH = 0.9
RESIZE_WIDTH = 640
RESIZE_HEIGHT = 640

# Vehicle labels (Adjust according to your label_map.pbtxt file)

# Model Paths
# PATH_TO_MODEL_DIR = os.path.join(current_dir, "models", "model1")
# PATH_TO_LABELS = os.path.join(PATH_TO_MODEL_DIR, 'label_map.pbtxt')
# PATH_TO_SAVED_MODEL = os.path.join(PATH_TO_MODEL_DIR, "saved_model")

PATH_TO_MODEL_DIR ='/home/ubuntu/AWS_Image_processing_git/models/model1'
PATH_TO_LABELS = '/home/ubuntu/AWS_Image_processing_git/models/model1/label_map.pbtxt'
PATH_TO_SAVED_MODEL = "/home/ubuntu/AWS_Image_processing_git/models/model1/saved_model"

# Load Model and Labels Once
detect_fn = tf.saved_model.load(PATH_TO_SAVED_MODEL)
category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)

# Ensure the output folder exists
output_folder = "/home/ubuntu/AWS_Image_processing_git/Frames/analayzed_frames/"
os.makedirs(output_folder, exist_ok=True)

def process_image_data(frame, metadata):
    start_time = time.time()
    # Convert the frame to a NumPy array
    frame = np.array(frame)
    original_height, original_width, _ = frame.shape
    # print(f"Original Dimensions: {original_height}x{original_width}")

    # Resize frame and convert to RGB
    resized_frame = cv2.resize(frame, (RESIZE_WIDTH, RESIZE_HEIGHT))
    frame_rgb = cv2.cvtColor(resized_frame, cv2.COLOR_RGB2BGR)

    # Perform inference
    input_tensor = tf.convert_to_tensor(np.expand_dims(frame_rgb, axis=0), dtype=tf.uint8)
    detections = detect_fn(input_tensor)

    # Convert detections to numpy arrays
    num_detections = int(detections.pop('num_detections'))
    detections = {key: value[0, :num_detections].numpy() for key, value in detections.items()}
    detections['num_detections'] = num_detections
    detections['detection_classes'] = detections['detection_classes'].astype(np.int64)

    # Process detections
    for i in range(num_detections):
        class_id = int(detections['detection_classes'][i])
        score = detections['detection_scores'][i]

        if score >= MIN_CONF_THRESH:
            # Get box coordinates and label
            ymin, xmin, ymax, xmax = detections['detection_boxes'][i]
            xmin = int(xmin * RESIZE_WIDTH)
            xmax = int(xmax * RESIZE_WIDTH)
            ymin = int(ymin * RESIZE_HEIGHT)
            ymax = int(ymax * RESIZE_HEIGHT)

            label = f'{category_index[class_id]["name"]}'
            cv2.rectangle(frame_rgb, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
            cv2.putText(frame_rgb, label, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        
            ts_for_image = str(metadata['ts'])

            modified_ts_for_image = re.sub(r'[-:.]', '_', ts_for_image)
 
            output_path = os.path.join(output_folder, f"detected_{modified_ts_for_image}.jpg")

            # #Save the image
            cv2.imwrite(output_path, frame_rgb,)
            # Store detection metadata in the database
            cluster_database(metadata,label, score)

    end_time = time.time()
    processing_time = end_time - start_time
    print(f"Processing time for logo detection: {processing_time:.4f} seconds")

    # # Display the frame with detections
    # cv2.imshow('Detection', frame_rgb)
    # # Use cv2.waitKey with a small delay for continuous display
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     print("Quitting display loop...")
    #     cv2.destroyAllWindows()
    #     return  # Optionally break the loop if you wish to stop processing