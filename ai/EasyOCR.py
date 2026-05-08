from ultralytics import YOLO
import cv2
import easyocr
from SQLDatabase import *
import matplotlib.pyplot as plt
import os

# load the model
model = YOLO("models/best.pt")


def process_image(image_path):
    img = cv2.imread(image_path)
    print(image_path)
    # use the model
    results = model(img)
    result = results[0]

    # Instance text detector
    reader = easyocr.Reader(['en'])

    # detect text on image
    #text = reader.readtext(img)

    plate_class_id = 0
    Latin_Letters = "NULL"
    Latin_Numbers = "NULL"
    conf_letters = 0.0
    conf_numbers = 0.0
    avg_conf = 0.0
    cropped_plate = img
    # extract the pictures that have plate
    for box in result.boxes:
        class_id = int(box.cls[0])
        if class_id == plate_class_id:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            # cropping the image
            cropped_plate = img[y1:y2, x1:x2]
            results = reader.readtext(cropped_plate, detail=1)

            if results:
                texts = [res[1] for res in results]
                confidences = [res[2] for res in results]
                text2 = ''.join(texts).replace(" ", "")

                avg_conf = sum(confidences) / len(confidences)

            if plate_class_id == 1:
                Latin_Numbers = correct_ocr_digits_errors(text2)
                conf_numbers = avg_conf

            if plate_class_id == 2:
                Latin_Letters = correct_ocr_letters_errors(text2).upper()
                conf_letters = avg_conf

        plate_class_id+=1

    print(Latin_Numbers, "Confidence:", f"{conf_numbers * 100:.2f}%")
    print(Latin_Letters, "Confidence:", f"{conf_letters * 100:.2f}%")
    cong_avg = ((conf_numbers + conf_letters) / 2 )
    #store_in_database(Latin_Numbers,Latin_Letters,cong_avg,image_path)
    log_exit(Latin_Numbers,Latin_Letters,cong_avg,image_path)

# this for showing the image
'''
    img_rgb = cv2.cvtColor(cropped_plate, cv2.COLOR_BGR2RGB)
    plt.imshow(cropped_plate)
    plt.axis('off')
    plt.show()
'''