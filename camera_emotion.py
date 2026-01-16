import cv2
from fer import FER
import random
import time
import webbrowser
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import mediapipe as mp

# ------------------------------
# Spotify Authentication
# ------------------------------
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="63ae557f57cd4e31aeb8bcc0db1673d8",
    client_secret="93cc866850954c41a38d0f5b16925a03",
    redirect_uri="http://127.0.0.1:8888/callback",
    scope="user-read-playback-state,user-modify-playback-state,user-read-currently-playing"
))

# ------------------------------
# Songs for each emotion
# ------------------------------
emotion_songs = {
    "happy": "spotify:track:YOUR_HAPPY_SONG_URI",
    "sad": "spotify:track:YOUR_SAD_SONG_URI",
    "angry": "spotify:track:YOUR_ANGRY_SONG_URI",
    "surprise": "spotify:track:YOUR_SURPRISE_SONG_URI",
    "fear": "spotify:track:YOUR_FEAR_SONG_URI",
    "disgust": "spotify:track:YOUR_DISGUST_SONG_URI",
    "neutral": "spotify:track:YOUR_NEUTRAL_SONG_URI"
}

# ------------------------------
# Mediapipe Face Mesh
# ------------------------------
mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# ------------------------------
# Detect emotion and play song
# ------------------------------
def detect_emotion_and_play_song():
    cap = cv2.VideoCapture(0)
    detector = FER(mtcnn=True)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Detect emotion
        result = detector.detect_emotions(frame)
        if result:
            emotions = result[0]["emotions"]
            dominant_emotion = max(emotions, key=emotions.get)
            print(f"Detected emotion: {dominant_emotion}")

            # Play song for this emotion
            song_uri = emotion_songs.get(dominant_emotion)
            if song_uri:
                try:
                    sp.start_playback(uris=[song_uri])
                    print(f"Playing song for {dominant_emotion}")
                except Exception as e:
                    print("Spotify playback error:", e)

        cv2.imshow("Camera", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# ------------------------------
# Run directly
# ------------------------------
if __name__ == "__main__":
    detect_emotion_and_play_song()


