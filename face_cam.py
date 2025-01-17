import numpy as np
import tensorflow as tf
import cv2
import os
from processing_files.mqtt_database import face_database
import time

cap = cv2.VideoCapture("VIdeo_data/nepal_prime.mp4")
DEVICE_ID = "4000123"
TYPE = 29
face_model_path = 'processing_files/nepal2.tflite'
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

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
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
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, f'Face: {face_class_names[face_predicted_class]}', (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, f'Confidence: {face_confidence:.2f}', (x, y + h + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            epoch_time = int(time.time())

            payload = {
                        "TS": epoch_time,
                        "Type": TYPE,
                        "DEVICE_ID":DEVICE_ID ,
                        "Details": {
                            "Face_name": label,
                            "score": score
                        }
                    }

            score = round(float(face_confidence), 2)
         

    cv2.imshow('Face Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
