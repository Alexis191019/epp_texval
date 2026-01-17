from ultralytics import YOLO
import cv2
import supervision as sv

modelo= YOLO("modelos/yolov8n.pt")

tracker = sv.ByteTrack()
box_annotator= sv.BoxAnnotator()
label_annotator= sv.LabelAnnotator()

def detectar_objetos(frame, modelo= modelo):
    resultados= modelo.predict(frame, conf=0.50)[0]
    detections = sv.Detections.from_ultralytics(resultados)
    detections = tracker.update_with_detections(detections)
    
    labels = [
        f"#{tracker_id} {class_name}"
        for class_name, tracker_id
        in zip(detections.data["class_name"], detections.tracker_id)
    ]
    
    annotated_frame = box_annotator.annotate(
        scene=frame.copy(), detections=detections)
    annotated_frame = label_annotator.annotate(
        scene=annotated_frame, detections=detections, labels=labels)
    return annotated_frame

def detect(frame, modelo= modelo):
    resultados= modelo.predict(frame, conf=0.5)[0]
    detections= resultados.plot()
    return detections

def linea_deteccion(frame, punto_inicio:tuple[int, int], punto_fin:tuple[int, int]):
    linea= cv2.line(frame, punto_inicio, punto_fin, (0, 0, 255), 2)
    return linea
