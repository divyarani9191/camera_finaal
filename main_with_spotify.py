import cv2
import time
import random
from fer import FER
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pymongo import MongoClient
from datetime import datetime, timezone, timedelta

# ===================== TIME (IST) =====================
IST = timezone(timedelta(hours=5, minutes=30))

# ===================== MONGODB =====================
client = MongoClient("mongodb://localhost:27017/")
db = client["EmoHeal"]
music_collection = db["face_music_history"]
print("✅ MongoDB Connected")

# ===================== SPOTIFY =====================
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id="63ae557f57cd4e31aeb8bcc0db1673d8",
        client_secret="93cc866850954c41a38d0f5b16925a03",
        redirect_uri="http://localhost:8888/callback",
        scope="user-modify-playback-state user-read-playback-state"
    )
)
print("✅ Spotify Premium Auth Successful")

# ===================== EMOTION → BOLLYWOOD =====================
EMOTION_QUERY = {
    "happy": "Hindi Bollywood happy songs",
    "sad": "Hindi Bollywood sad songs",
    "angry": "Hindi Bollywood motivational songs",
    "fear": "Hindi Bollywood calm songs",
    "surprise": "Hindi Bollywood party songs",
    "neutral": "Hindi Bollywood relaxing songs",
    "disgust": "Hindi Bollywood soothing songs"
}

# ===================== PLAY SONG =====================
def play_song(emotion):
    query = EMOTION_QUERY.get(emotion, "Hindi Bollywood songs")

    res = sp.search(q=query, type="track", limit=25, market="IN")
    tracks = res["tracks"]["items"]
    if not tracks:
        return ""

    track = random.choice(tracks)

    devices = sp.devices()["devices"]
    if not devices:
        print("⚠️ Spotify open karo (mobile/desktop)")
        return ""

    device_id = devices[0]["id"]
    sp.transfer_playback(device_id=device_id, force_play=True)
    sp.start_playback(device_id=device_id, uris=[track["uri"]])

    song = f"{track['name']} - {track['artists'][0]['name']}"
    print("🎵 Playing:", song)
    return song

def pause_song():
    try:
        sp.pause_playback()
        print("⏸ Song Paused")
    except:
        pass

# ===================== CAMERA =====================
detector = FER(mtcnn=False)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

current_emotion = "No Face Detected"
current_song = ""
selected_face_index = -1
last_faces = []
allow_detection = True

DETECT_EVERY = 10
frame_count = 0

print("🎥 EmoHeal Running")
print("👉 ENTER = detect again")
print("👉 Q = quit")

# ===================== MAIN LOOP =====================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    frame_count += 1
    faces = []

    if allow_detection and frame_count % DETECT_EVERY == 0:
        faces = detector.detect_emotions(frame)
        last_faces = faces

        if not faces:
            pause_song()
            current_emotion = "No Face Detected"
            current_song = ""
            selected_face_index = -1

        else:
            selected_face_index = max(
                range(len(faces)),
                key=lambda i: max(faces[i]["emotions"].values())
            )

            emotions = faces[selected_face_index]["emotions"]
            current_emotion = max(emotions, key=emotions.get)

            current_song = play_song(current_emotion)

            record = {
                "mood": current_emotion,
                "song": current_song,
                "timestamp": datetime.now(IST)
            }
            music_collection.insert_one(record)
            print("✅ Stored in MongoDB:", record)

            allow_detection = False

    # ===== DRAW FACES (freeze after detection) =====
    draw_faces = last_faces if not allow_detection else faces

    for i, face in enumerate(draw_faces):
        x, y, w, h = face["box"]
        color = (0, 255, 0) if i == selected_face_index else (150, 150, 150)
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

    # ===== UI =====
    cv2.rectangle(frame, (0, 0), (640, 90), (0, 0, 0), -1)
    cv2.putText(frame, f"Emotion: {current_emotion}", (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(frame, f"Song: {current_song}", (20, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

    cv2.imshow("EmoHeal - Emotion Based Player", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == 13:  # ENTER pressed
        allow_detection = True
        print("🔄 Ready for next detection")

    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()