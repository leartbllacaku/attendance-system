import sqlite3
import os
from datetime import datetime

# Database file
DB_FILE = 'attendance.db'


CLASSES = {
    'COMP101': 'Introduction to Computer Science',
    'MATH201': 'Linear Algebra',
    'PHYS150': 'Data Structures and Algorithms',
    'CHEM120': 'General Chemistry'
}

def init_db():
    """Initialize the database if it doesn't exist"""
    if os.path.exists(DB_FILE):
        return  # Database already exists
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create attendance table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        class_name TEXT NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()

def get_classes():
    """Return the list of classes"""
    return [(code, name) for code, name in CLASSES.items()]

def record_attendance(name, class_name = None):
    """Record attendance for a person"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Get current date and time
    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    time_str = now.strftime('%H:%M:%S')

    # If no class name provided, use "Unknown"
    if not class_name or class_name not in CLASSES:
        class_name = "Unknown"
    
    # Insert attendance record
    cursor.execute(
        'INSERT INTO attendance (name, class_name, date, time) VALUES (?, ?, ?, ?)',
        (name, class_name, date_str, time_str)
    )
    
    conn.commit()
    conn.close()

def fetch_attendance(class_name=None):
    """Fetch all attendance records"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    if class_name and class_name in CLASSES:
        cursor.execute('''
            SELECT name, class_name, date, time FROM attendance 
            WHERE class_name = ?
            ORDER BY date DESC, time DESC
        ''', (class_name,))
    else:
        cursor.execute('''
            SELECT name, class_name, date, time FROM attendance 
            ORDER BY date DESC, time DESC
        ''')
    
    attendance = cursor.fetchall()
    
    conn.close()
    return attendance