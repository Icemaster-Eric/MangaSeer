from ultralytics import YOLOv10

# currently just a training script pls don't run randomly :)
# Load YOLOv10n model
model = YOLOv10("yolov10l.pt")

if __name__ == "__main__":
    # Train the model
    model.train(data="dataset.yaml", epochs=60, batch=24)
