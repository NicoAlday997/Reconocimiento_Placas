import time

import cv2
import numpy as np
import pytesseract
from PIL import Image


def preprocess_plate(plate):
    # Convertir la placa a formato HSV
    plate_hsv = cv2.cvtColor(plate, cv2.COLOR_BGR2HSV)

    # Definir el rango de valores HSV para el color blanco
    #lower_white = np.array([0, 0, 200])  # Valores mínimos de matiz, saturación y valor para blanco
    lower_white = np.array([0, 0, 145])
    upper_white = np.array([180, 30, 255])  # Valores máximos de matiz, saturación y valor para blanco

    # Binarizar la imagen basándose en el rango de valores de color blanco
    mask_white = cv2.inRange(plate_hsv, lower_white, upper_white)

    return plate_hsv, mask_white


def extract_plate_text(plate_bgr, plate_bin):
    Mva = np.zeros(plate_bgr.shape[:2], dtype=np.uint8)
    mBp = plate_bgr[:, :, 0]
    mGp = plate_bgr[:, :, 1]
    mRp = plate_bgr[:, :, 2]
    for col in range(plate_bgr.shape[0]):
        for fil in range(plate_bgr.shape[1]):
            Max = max(mRp[col, fil], mGp[col, fil], mBp[col, fil])
            Mva[col, fil] = 255 - Max
    _, binary_plate = cv2.threshold(Mva, 150, 255, cv2.THRESH_BINARY)
    return binary_plate


def process_video(video_path):
    cap = cv2.VideoCapture(video_path)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame_with_plate = process_frame(frame)
        cv2.imshow("Vehicle Detection", frame_with_plate)
        if cv2.waitKey(1) == 27:
            break
    cap.release()
    cv2.destroyAllWindows()


def process_frame(frame):
    # Clonar el fotograma original para evitar modificar el original
    frame_with_roi = frame.copy()

    # Obtener las dimensiones del fotograma
    height, width, _ = frame.shape

    # Definir las coordenadas del área de interés (ROI) en el centro del fotograma
    roi_x1 = int(width / 3)
    roi_x2 = int(width * 2 / 3)
    roi_y1 = int(height / 3)
    roi_y2 = int(height * 2 / 3)

    # Dibujar el área de interés en el fotograma clonado
    cv2.rectangle(frame_with_roi, (roi_x1, roi_y1), (roi_x2, roi_y2), (0, 255, 0), 2)

    # Procesar el área de interés
    roi = frame_with_roi[roi_y1:roi_y2, roi_x1:roi_x2]  # Usar el fotograma con el área de interés dibujada
    plate_bgr, plate_bin = preprocess_plate(roi)
    #cv2.imshow("Binarized Plate", plate_bin)
    #cv2.waitKey(0)


    #cv2.destroyAllWindows()


    plate_text = extract_text_from_plate(plate_bin)

    # Extraer los contornos de la imagen binarizada
    contours, _ = cv2.findContours(plate_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Dibujar los rectángulos alrededor de los contornos que cumplen ciertas condiciones
    for contour in contours:
        # Calcular el área del contorno
        area = cv2.contourArea(contour)
        # Verificar si el área del contorno es mayor que un umbral mínimo
        if (area > 300 and area < 2000):  # Ajustar este valor según sea necesario
            x, y, w, h = cv2.boundingRect(contour)
            # Ajustar las coordenadas del rectángulo a la posición relativa al fotograma completo
            x += roi_x1
            y += roi_y1
            cv2.rectangle(frame_with_roi, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Si se detecta texto en la placa

    if plate_text is not None:
        draw_plate_text(frame_with_roi, plate_text)
        print("TEXTO: " + plate_text)

    # print("NO hay texto")


    return frame_with_roi


def select_roi(frame):
    height, width, _ = frame.shape
    x1 = int(width / 3)
    x2 = int(width * 2 / 3)
    y1 = int(height / 3)
    y2 = int(height * 2 / 3)
    return frame[y1:y2, x1:x2]


def extract_text_from_plate(plate):
    if plate.shape[0] >= 36 and plate.shape[1] >= 82:
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        config = "--psm 3"  # Modo de segmentación de bloques
        text = pytesseract.image_to_string(Image.fromarray(plate), config=config)

        # Filtrar caracteres no alfanuméricos
        text = ''.join(filter(str.isalnum, text))

        if len(text) >= 6:
            return text[:6]
    return None



def draw_plate_text(frame, text):
    cv2.rectangle(frame, (870, 750), (1070, 850), (0, 0, 0), cv2.FILLED)
    cv2.putText(frame, text, (900, 810), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)


if __name__ == "__main__":
    process_video("Placas8.mp4")
