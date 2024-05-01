import cv2
import numpy as np
import pytesseract
from PIL import Image

#Clase funciona de forma independiente

class LectorPlacas:
    def __init__(self):
        pass
        self.plate_counts = {}

    def preprocess_plate(self, plate):
        plate_hsv = cv2.cvtColor(plate, cv2.COLOR_BGR2HSV)
        lower_white = np.array([0, 0, 135])
        upper_white = np.array([180, 30, 255])
        mask_white = cv2.inRange(plate_hsv, lower_white, upper_white)
        return plate_hsv, mask_white

    def process_frame(self, frame):
        frame_with_roi = frame.copy()
        height, width, _ = frame.shape
        roi_x1 = int(width / 3)
        roi_x2 = int(width * 2 / 3)
        roi_y1 = int(height / 3)
        roi_y2 = int(height * 2 / 3)
        cv2.rectangle(frame_with_roi, (roi_x1, roi_y1), (roi_x2, roi_y2), (0, 255, 0), 2)
        roi = frame_with_roi[roi_y1:roi_y2, roi_x1:roi_x2]
        plate_bgr, plate_bin = self.preprocess_plate(roi)

        # Aquí se muestra la placa binarizada
        cv2.imshow("Binarized Plate", plate_bin)

        plate_text = self.extract_text_from_plate(plate_bin)
        contours, _ = cv2.findContours(plate_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            area = cv2.contourArea(contour)
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w) / h
            if 300 < area < 2000 and 2 <= aspect_ratio <= 3:
                x += roi_x1
                y += roi_y1
                cv2.rectangle(frame_with_roi, (x, y), (x + w, y + h), (0, 255, 0), 2)
        if plate_text is not None:
            self.draw_plate_text(frame_with_roi, plate_text)
            print("TEXTO: " + plate_text)
        return frame_with_roi

    def select_roi(self, frame):
        height, width, _ = frame.shape
        x1 = int(width / 3)
        x2 = int(width * 2 / 3)
        y1 = int(height / 3)
        y2 = int(height * 2 / 3)
        return frame[y1:y2, x1:x2]


    # def extract_text_from_plate(self, plate):
    #     if plate.shape[0] >= 36 and plate.shape[1] >= 82:
    #         pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    #         config = "--psm 3"
    #         text = pytesseract.image_to_string(Image.fromarray(plate), config=config)
    #         text_filtered = ''.join(c for c in text if c.isalnum() or c == '-')
    #         if len(text_filtered) >= 9:
    #             return text_filtered[:9]
    #     return None

    def extract_text_from_plate(self, plate):
        if plate.shape[0] >= 36 and plate.shape[1] >= 82:
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            config = "--psm 3"
            text = pytesseract.image_to_string(Image.fromarray(plate), config=config)
            text_filtered = ''.join(c for c in text if c.isalnum() or c == '-')
            if len(text_filtered) >= 9:
                text_filtered = text_filtered[:9]
                if text_filtered in self.plate_counts:
                    self.plate_counts[text_filtered] += 1
                    if self.plate_counts[text_filtered] == 4:
                        print("La placa {} se ha detectado 4 veces.".format(text_filtered))
                        # Aquí podrías agregar código para una notificación más elaborada
                else:
                    self.plate_counts[text_filtered] = 1

                return text_filtered

        return None


    def draw_plate_text(self, frame, text):
        cv2.rectangle(frame, (870, 750), (1070, 850), (0, 0, 0), cv2.FILLED)
        cv2.putText(frame, text, (900, 810), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    def process_video(self, video_path):
        cap = cv2.VideoCapture(video_path)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame_with_plate = self.process_frame(frame)
            cv2.imshow("Vehicle Detection", frame_with_plate)
            if cv2.waitKey(1) == 27:
                break
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    lector_placas = LectorPlacas()
    lector_placas.process_video("Placas8.mp4")