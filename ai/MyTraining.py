from ultralytics import YOLO

# load the model
model = YOLO("yolov8n.yaml")

# use the model
results = model.train(data="config.yaml", epochs=150) # train the model