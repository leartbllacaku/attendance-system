from flask import Flask, render_template, request, redirect, url_for, flash
import os
import database
import process_video

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


app.secret_key = 'MZNM7gQZXRnoyE2kAyrzNjpfi1OXpTQp'  # Replace with a random string

# Initialize DB if not exists
database.init_db()
known_encodings, known_names = process_video.load_known_faces() 

@app.route('/', methods=['GET', 'POST'])
def index():

    classes = database.get_classes()

    if request.method == 'POST':
        video = request.files['video']
        class_name = request.form.get('class_name')
        
        if video:
            path = os.path.join(app.config['UPLOAD_FOLDER'], video.filename)
            video.save(path)
            
            # If no class selected, try to extract from filename
            if not class_name:
                # Look for class codes in the filename
                filename = video.filename.upper()
                for code in database.CLASSES.keys():
                    if code in filename:
                        class_name = code
                        break

            # Process video 
            faces_detected = process_video.process_video(path, known_encodings, known_names)
            
            # Record class attendance in database
            if faces_detected:
                for name in set(process_video.recognized_names):
                    database.record_attendance(name, class_name)
                flash(f'Video processing complete! Faces detected and recorded for {class_name if class_name else "Unknown"} class.', 'success')
            else:
                flash('No faces were detected in the video. Please try again.', 'warning')

            return redirect(url_for('logs', class_name=class_name))
            
    return render_template('index.html', classes=classes)

@app.route('/logs')
def logs():
    class_name = request.args.get('class_name')
    attendance = database.fetch_attendance(class_name)
    classes = database.get_classes()
    
    return render_template('logs.html', attendance=attendance, classes=classes, selected_class=class_name)

if __name__ == '__main__':
    app.run(debug=True, port=5001)  
