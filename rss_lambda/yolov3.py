import os
import cv2
import numpy as np

YOLOV3_WEIGHTS_PATH = os.path.join('blobs', 'yolov3.weights')
YOLOV3_CFG_PATH = os.path.join('blobs', 'yolov3.cfg')


def is_yolov3_available():
    return os.path.exists(YOLOV3_WEIGHTS_PATH) and os.path.exists(YOLOV3_CFG_PATH)


def yolov3(image_path: str, confidence_threshold: float, desired_class_id: int) -> bool:
    # Load YOLO
    net = cv2.dnn.readNet(YOLOV3_WEIGHTS_PATH, YOLOV3_CFG_PATH)
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

    # Load image
    image = cv2.imread(image_path)

    # Create blob and do forward pass
    blob = cv2.dnn.blobFromImage(image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    # Information for each object detected
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > confidence_threshold and class_id == desired_class_id:
                return True
    return False
