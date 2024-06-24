from ultralytics import YOLOv10


# Load YOLOv10n model
model = YOLOv10(model="yolov10l.yaml")

if __name__ == "__main__":
    # Train the model
    model.train(data="dataset.yaml", epochs=200, batch=24)
