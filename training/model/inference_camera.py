import math

import cv2
from ultralytics import YOLO

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

model = YOLO("../models/best.pt")
classNames = [
    'apple', 'banana', 'bell_pepper', 'cabbage', 'carrot', 'chilli_pepper'
    'corn', 'cucumber', 'eggplant', 'garlic', 'grape', 'kiwi', 'lemon', 'lettuce', 'mango', 'onion', 'orange', 'pineapple',
    'potato', 'sweetpotato', 'tomato', 'watermelon'
]
while True:
    success, img = cap.read()
    results = model(img, stream=True)

    for r in results:
        boxes = r.boxes

        for box in boxes:
            # bounding box
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2) \

            # put box in cam
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

            # confidence
            confidence = math.ceil(box.conf[0] * 100) / 100
            print("Confidence --->", confidence)

            # class name
            cls = int(box.cls[0])
            if cls <= (len(classNames) - 1):
                print("Class name -->", classNames[cls])

            # object details
            org = [x1, y1]
            font = cv2.FONT_HERSHEY_SIMPLEX
            fontScale = 1
            color = (255, 0, 0)
            thickness = 2
            if cls <= (len(classNames) - 1):
                cv2.putText(img, classNames[cls], org, font, fontScale, color, thickness)

    cv2.imshow('Webcam', img)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
