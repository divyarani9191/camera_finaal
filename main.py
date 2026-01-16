from fer import FER
import cv2

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Improve FPS
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

detector = FER(mtcnn=False)   # FAST MODE

print("EmoHeal Running... Press Q to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)

    # Resize for speed
    small_frame = cv2.resize(frame, (450, 350))

    emotions = detector.detect_emotions(small_frame)

    if emotions:
        emotion, score = detector.top_emotion(small_frame)
        if emotion:
            cv2.putText(frame, f"Emotion: {emotion}",
                        (40, 50), cv2.FONT_HERSHEY_SIMPLEX,
                        1.1, (255, 255, 255), 2)

    cv2.imshow("EmoHeal - Live Mood Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()


