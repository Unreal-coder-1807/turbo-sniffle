import sqlite3
import json
import numpy as np
from PIL import Image
from io import BytesIO

def insert_passenger(db_path, name, age, gender, aadhaar, coach, encoding, image=None):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Ensure table exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS passengers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            gender TEXT,
            aadhaar TEXT,
            coach TEXT,
            face_encoding TEXT,
            face_image BLOB
        );
    """)

    # Convert encoding to JSON string for storage
    encoding_json = json.dumps(encoding.tolist())

    # Convert image to bytes if provided
    face_blob = None
    if image is not None:
        img_pil = Image.fromarray(image)
        buffer = BytesIO()
        img_pil.save(buffer, format='JPEG')
        face_blob = buffer.getvalue()

    cursor.execute("""
        INSERT INTO passengers (name, age, gender, aadhaar, coach, face_encoding, face_image)
        VALUES (?, ?, ?, ?, ?, ?, ?);
    """, (name, age, gender, aadhaar, coach, encoding_json, face_blob))

    conn.commit()
    conn.close()