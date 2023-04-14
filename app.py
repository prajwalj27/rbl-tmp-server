from fastapi import FastAPI, APIRouter, File, Form, UploadFile, Request, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import dotenv_values
from pymongo import MongoClient
from typing import List
import random
import os.path
from datetime import date
import uuid
import base64

import cv2
from deepface import DeepFace
from fer import FER

from models import Song, SongUpdate, User

config = dotenv_values(".env")

print(config)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient(config["MONGODB_URI"])
    app.database = app.mongodb_client[config["DB_NAME"]]


@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()


@app.get('/', response_description="home route")
def main():
    return {'message': 'Welcome to MoodTunes - RBL Group B15'}


# GET Songs from DB

@app.get('/songs/all', response_description="Get all songs", response_model=List[Song])
def list_songs(request: Request):
    songs = list(request.app.database["songs"].find())
    shuffled_songs = random.sample(songs, len(songs))
    return songs


@app.get('/songs/happy', response_description="Get Happy Playlist", response_model=List[Song])
def list_songs(request: Request):
    songs = list(request.app.database["songs"].find({"mood": "Happy"}))
    shuffled_songs = random.sample(songs, len(songs))
    return songs


@app.get('/songs/sad', response_description="Get sad Playlist", response_model=List[Song])
def list_songs(request: Request):
    songs = list(request.app.database["songs"].find({"mood": "Happy"}))
    shuffled_songs = random.sample(songs, len(songs))
    return songs


@app.get('/songs/disgust', response_description="Get disgust Playlist", response_model=List[Song])
def list_songs(request: Request):
    songs = list(request.app.database["songs"].find({"mood": "Sad"}))
    shuffled_songs = random.sample(songs, len(songs))
    return songs


@app.get('/songs/fear', response_description="Get fear Playlist", response_model=List[Song])
def list_songs(request: Request):
    songs = list(request.app.database["songs"].find({"mood": "Calm"}))
    shuffled_songs = random.sample(songs, len(songs))
    return songs


@app.get('/songs/angry', response_description="Get angry Playlist", response_model=List[Song])
def list_songs(request: Request):
    songs = list(request.app.database["songs"].find({"mood": "Calm"}))
    shuffled_songs = random.sample(songs, len(songs))
    return songs


@app.get('/songs/surprise', response_description="Get surprise Playlist", response_model=List[Song])
def list_songs(request: Request):
    songs = list(request.app.database["songs"].find({"mood": "Energetic"}))
    shuffled_songs = random.sample(songs, len(songs))
    return songs


@app.get('/songs/neutral', response_description="Get neutral Playlist", response_model=List[Song])
def list_songs(request: Request):
    songs = list(request.app.database["songs"].find({"mood": "Energetic"}))
    shuffled_songs = random.sample(songs, len(songs))
    return songs


@app.get('/songs/{id}', response_description="Get single song by song_id", response_model=List[Song])
def find_song(id: str, request: Request):
    song = list(request.app.database["songs"].find({"song_id": int(id)}))
    # shuffled_songs = random.sample(songs, len(songs))
    return song


@app.get('/liked', response_description="Get all liked songs by the user", response_model=List[Song])
def liked_songs(request: Request):
    user = list(
        request.app.database["users"].find({"username": "prajwalj27"}))
    liked_songs = user[0]['liked_songs']

    songs = list(request.app.database["songs"].find(
        {'song_id': {'$in': liked_songs}}))
    return songs


@app.get('/liked/{id}', response_description="Get whether a song is liked by the user or not")
def is_liked(id: str, request: Request):
    user = list(
        request.app.database["users"].find({"username": "prajwalj27"}))
    liked_songs = user[0]['liked_songs']
    return int(id) in set(liked_songs)


@app.get('/liked/add/{id}', response_description="Like a song")
def set_like_song(id: str, request: Request):
    like = request.app.database["users"].update_one(
        {'username': 'prajwalj27'}, {'$push': {'liked_songs': 99}})
    # liked_songs = user[0]['liked_songs']
    return {'msg': 'song liked'}


@app.post('/upload')
async def getInformation(info: Request):
    image_data = await info.json()
    decoded_img = base64.b64decode(image_data['base64'])

    if os.path.exists('./images') == False:
        os.mkdir('./images')

    img_name = str(date.today()) + "-" + str(uuid.uuid4()) + '.jpg'

    dirImage = os.path.join(
        './images', img_name)
    with open(dirImage, 'wb') as image:
        image.write(decoded_img)
        image.close()

    input_image = './images/' + img_name
    try:
        result1 = DeepFace.analyze(input_image, actions=['emotion'])
        mood = result1[0]['dominant_emotion']
        print('deepface Model: ' + mood)

        ferDetector = FER()
        result2 = ferDetector.top_emotion(input_image)
        print(result2[0])

        return {
            "mood": mood,
        }
    except Exception as e:
        mood = str(e)
        print(str(e))
        return {
            "mood": 'Error while detecting the Mood. Please Try again!',
            
        }


# Activate venv
# source ./venv/scripts/activate

# Install all predefiened depenedencies
# pip install -r requirements.txt

# Run the server
# uvicorn app:app --host 0.0.0.0 --reload
