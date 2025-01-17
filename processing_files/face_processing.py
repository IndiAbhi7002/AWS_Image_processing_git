import numpy as np
import tensorflow as tf
import cv2
import os
import re
from processing_files.mqtt_database import face_database
import time

face_model_path = '/home/ubuntu/AWS_Image_processing_git/processing_files/nepal3.tflite'
face_interpreter = tf.lite.Interpreter(model_path=face_model_path)
face_interpreter.allocate_tensors()

face_input_details = face_interpreter.get_input_details()
face_output_details = face_interpreter.get_output_details()
# face_class_names = [folder for folder in os.listdir("Face_rec/datasetall/")]
face_class_names = ['KP_Sharma_Oli', 'Rajesh_Hampal', 'Unknown']

# print(f"face_class_name : {face_class_names}")

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def preprocess_image_face(face, target_size=(64, 64)):
    face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
    face = cv2.resize(face, target_size)
    face = face / 255.0  # Normalize to [0, 1]
    face = np.expand_dims(face, axis=0).astype(np.float32)  # Convert to FLOAT32
    return face

output_folder = "/home/ubuntu/AWS_Image_processing_git/Frames/analayzed_face_frames/"

os.makedirs(output_folder, exist_ok=True)

def get_frame(image, metadata):

    start_time = time.time()

    frame = np.array(image)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    gray = cv2.cvtColor(frame_rgb, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in faces:
        face = frame[y:y+h, x:x+w]
        input_data_face = preprocess_image_face(face)
        face_interpreter.set_tensor(face_input_details[0]['index'], input_data_face)
        face_interpreter.invoke()
        face_output_data = face_interpreter.get_tensor(face_output_details[0]['index'])
        face_probabilities = face_output_data[0]
        face_predicted_class = np.argmax(face_probabilities)
        face_confidence = face_probabilities[face_predicted_class]

        if face_confidence >0.88:
            if face_class_names[face_predicted_class] in face_class_names:
                cv2.rectangle(frame_rgb, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame_rgb, f'Face: {face_class_names[face_predicted_class]}', (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.putText(frame_rgb, f'Confidence: {face_confidence:.2f}', (x, y + h + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                ts_for_image = str(metadata['ts'])

                modified_ts_for_image = re.sub(r'[-:.]', '_', ts_for_image)
                
                output_path = os.path.join(output_folder, f"detected_{modified_ts_for_image}.jpg")

                cv2.imwrite(output_path, frame_rgb)
                if face_class_names[face_predicted_class] == 'Unknown':
                    # pass
                    print("Unknown Face Images found")
                else:
                    print("Known face: ",face_class_names[face_predicted_class])
                    face_database(metadata, face_class_names[face_predicted_class], face_confidence)

    end_time = time.time()
    processing_time = end_time - start_time
    print(f"Processing time for the image: {processing_time:.4f} seconds")
    # # cv2.imshow('Face Detection', cv2.resize(frame_rgb,(920,640)))
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     print("Quitting display loop...")
    #     cv2.destroyAllWindows()
    #     return  # Optionally break the loop if you wish to stop processing
