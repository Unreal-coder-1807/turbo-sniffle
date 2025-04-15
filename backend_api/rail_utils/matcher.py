import sqlite3
import json
import numpy as np

def match_face(encoding, db_path, threshold=0.6):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Updated query to fetch coach information as well
    cursor.execute("SELECT name, age, gender, aadhaar, coach, face_encoding, face_image FROM passengers")
    rows = cursor.fetchall()
    conn.close()

    for name, age, gender, aadhaar, coach, enc_json, img_blob in rows:
        known_enc = np.array(json.loads(enc_json))
        dist = np.linalg.norm(known_enc - encoding)

        if dist < threshold:
            return {
                "match": True,
                "name": name,
                "age": age,
                "gender": gender,
                "aadhar": aadhaar,
                "coach": coach,
                "image": img_blob,  # raw bytes of stored image
                "distance": dist
            }

    return {"match": False}
