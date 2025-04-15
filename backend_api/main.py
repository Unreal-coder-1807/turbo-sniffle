from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from models import PassengerInfo
from rail_utils.face_encoder import encode_face
from rail_utils.db_manager import save_passenger

app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/book")
async def book_ticket(
    name: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    train_id: str = Form(...),
    travel_date: str = Form(...),
    image: UploadFile = File(...)
):
    image_bytes = await image.read()
    encoding = encode_face(image_bytes)

    if encoding is None:
        return {"status": "fail", "reason": "No face detected"}

    save_passenger(name, age, gender, train_id, travel_date, encoding)
    return {"status": "success", "message": "Ticket booked successfully"}

@app.get("/")
def home():
    return {"message": "Backend is alive!"}
