# import subprocess
# import time

# # Define the full path to the Python executable in your virtual environment
# python_path = "python"

# try:
#     # Run the face detection script
#     face_process = subprocess.Popen(
#         [python_path, "access_database_face.py"],
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE
#     )
#     print("Face detection script started...")

#     # Wait for 10 seconds before starting the logo detection script
#     time.sleep(10)

#     # Run the logo detection script
#     logo_process = subprocess.Popen(
#         [python_path, "access_database_logo.py"],
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE
#     )
#     print("Logo detection script started...")

#     # Wait for both scripts to complete
#     face_stdout, face_stderr = face_process.communicate()
#     logo_stdout, logo_stderr = logo_process.communicate()

#     # Print outputs and errors for debugging
#     print("Face Detection Output:")
#     print(face_stdout.decode())
#     print("Face Detection Errors:")
#     print(face_stderr.decode())

#     print("Logo Detection Output:")
#     print(logo_stdout.decode())
#     print("Logo Detection Errors:")
#     print(logo_stderr.decode())

# except Exception as e:
#     print(f"An error occurred: {e}")

# print("Both face and logo detection scripts have completed.")



import subprocess
import time

# Run the face detection script
face_process = subprocess.Popen(["python", "face_detection.py"])

# Wait for 10 seconds before starting the logo detection script
time.sleep(10)

# Run the logo detection script
logo_process = subprocess.Popen(["python", "logo_detection.py"])
# Wait for both scripts to complete
face_process.wait()
logo_process.wait()

print("Both face and logo detection scripts have completed.")
