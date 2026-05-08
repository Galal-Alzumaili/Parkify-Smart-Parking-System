from ultralytics import YOLO
import os
from EasyOCR import process_image
import uuid

# Save License Plate Picture
#SAVE_DIR = "captured_plates"
SAVE_DIR = "static/images"
os.makedirs(SAVE_DIR, exist_ok=True)

# Load the Yolo Model
model = YOLO("models/best.pt")

plt.ion()
fig, ax = plt.subplots()
im_display = None

cap = cv2.VideoCapture(0)
# old version
#cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# new feature to make the read only every 10 frames
frame_counter = 0
N = 10

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Camera Is not Open  ❌ ")
            continue

        # here new code for skip 10 frames
        frame_counter +=1
        if frame_counter % N != 0:
            continue

        # Detect License Plate
        results = model(frame)
        result = results[0]

        # Processing the image
        for box in result.boxes:
            class_id = int(box.cls[0])
            if class_id == 0:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cropped_plate = frame[y1:y2, x1:x2]
                # Save the image in folder
                filename = f"{uuid.uuid4().hex}.jpg"
                filepath = os.path.join(SAVE_DIR, filename)
                cv2.imwrite(filepath, cropped_plate)
                print(f"📸 Picture is saved: {filepath}")

                process_image(filepath)

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)


        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if im_display is None:
            im_display = ax.imshow(frame_rgb)
            plt.axis('off')
        else:
            im_display.set_data(frame_rgb)

        plt.pause(0.001)
finally:
    cap.release()
    plt.close()
    print("✅ Camera is closed")
