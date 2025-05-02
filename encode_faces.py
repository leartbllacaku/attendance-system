import face_recognition
import os
import pickle
import database

dataset_path = 'student_images'
encodings = []
names = []

print("[INFO] Encoding faces...")

for filename in os.listdir(dataset_path):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        name = os.path.splitext(filename)[0]
        image_path = os.path.join(dataset_path, filename)
        image = face_recognition.load_image_file(image_path)
        boxes = face_recognition.face_locations(image)
        encoding = face_recognition.face_encodings(image, boxes)[0]
        encodings.append(encoding)
        names.append(name)

        database.add_student(name)

# Save encodings
data = {"encodings": encodings, "names": names}
with open("encodings.pickle", "wb") as f:
    f.write(pickle.dumps(data))

print("[INFO] Encoding complete!")
