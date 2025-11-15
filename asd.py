from ultralytics import YOLO
import numpy as np

model = YOLO("models/best.pt")

img = np.zeros((640, 640, 3), dtype=np.uint8)
res = model.predict(img, imgsz=640, verbose=True)[0]

print("\n---- RES.BOXES ----")
print(res.boxes)

print("\n---- JSON ----")
print(res.to_json())
