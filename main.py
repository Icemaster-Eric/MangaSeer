from ultralytics import YOLOv10

# Load YOLOv10n model
model = YOLOv10("yolov10l.pt")

if __name__ == "__main__":
    # Train the model
    model.train(data="dataset.yaml", epochs=30, batch=16, imgsz=(871, 1238))
