import face_recognition
import cv2
import os
import database
import numpy as np
from datetime import datetime

def load_known_faces():
    """Load known faces from the students_images folder (now organized into subfolders)"""
    known_encodings = []
    known_names = []
    
    students_images_dir = 'students_images' 
    
    for student_folder in os.listdir(students_images_dir):
        student_folder_path = os.path.join(students_images_dir, student_folder)
        
        if os.path.isdir(student_folder_path):
            for image_name in os.listdir(student_folder_path):
                image_path = os.path.join(student_folder_path, image_name)
                image = cv2.imread(image_path)
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                
                small_frame = cv2.resize(rgb_image, (0, 0), fx=0.5, fy=0.5)
                face_locations = face_recognition.face_locations(small_frame)
                face_encodings = face_recognition.face_encodings(small_frame, face_locations)
                
                for face_encoding in face_encodings:
                    known_encodings.append(face_encoding)
                    known_names.append(student_folder)
    
    return known_encodings, known_names

known_encodings, known_names = load_known_faces()

recognized_names = []

def process_video(video_path, known_encodings, known_names):
    global recognized_names
    recognized_names = []  # Clear the list

    """Main function to process a video with face recognition"""    
    if not known_encodings:
        print("No reference faces found! Add images to the students_images directory.")
        return False
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return False
    
    frame_count = 0
    face_detected = False
    recognized_people = set()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Process every 60th frame to reduce CPU usage
        if frame_count % 30 == 0:
            small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)            

            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            
            face_locations = [(top*2, right*2, bottom*2, left*2) for (top, right, bottom, left) in face_locations]

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                face_detected = True
                name = "Unknown"
                
                if known_encodings:
                    matches = face_recognition.compare_faces(known_encodings, face_encoding)
                    
                    face_distances = face_recognition.face_distance(known_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    
                    if matches[best_match_index]:
                        name = known_names[best_match_index]

                if name not in recognized_people:
                    database.record_attendance(name)
                    recognized_people.add(name)
                    recognized_names.append(name) 
                    print(f"Face detected and recognized: {name}")

                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # Save detected face (optional)
                # faces_dir = os.path.join('static', 'detected_faces')
                # os.makedirs(faces_dir, exist_ok=True)
                # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")  # include microseconds
                # h, w = frame.shape[:2]
                # top = max(0, top)
                # bottom = min(h, bottom)
                # left = max(0, left)
                # right = min(w, right)

                # face_img = frame[top:bottom, left:right]                
                # face_file = os.path.join(faces_dir, f"{name}_{timestamp}.jpg")
                # cv2.imwrite(face_file, face_img)

        frame_count += 1

    cap.release()
    return face_detected
