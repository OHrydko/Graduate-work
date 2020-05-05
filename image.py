import numpy
from cv2 import cv2

from orm.model import db, ormE, ormAllergic


def image_transformation(file):
    # open image and apply filter
    img = cv2.imdecode(numpy.frombuffer(file, numpy.uint8), cv2.IMREAD_UNCHANGED)
    img = cv2.resize(img, None, fx=1.2, fy=1.2, interpolation=cv2.INTER_CUBIC)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    kernel = numpy.ones((1, 1), numpy.uint8)
    img = cv2.dilate(img, kernel, iterations=1)
    img = cv2.erode(img, kernel, iterations=1)
    img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)

    # get coordinates
    coords = numpy.column_stack(numpy.where(img > 0))
    angle = cv2.minAreaRect(coords)[-1]
    # the `cv2.minAreaRect` function returns values in the
    # range [-90, 0); as the rectangle rotates clockwise the
    # returned angle trends to 0 -- in this special case we
    # need to add 90 degrees to the angle
    if angle < -45:
        angle = -(90 + angle)
    # otherwise, just take the inverse of the angle to make
    # it positive
    else:
        angle = -angle

    (h, w) = img.shape[:2]
    center = (w // 2, h // 2)
    m = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(img, m, (w, h),
                             flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    img = rotated

    ret, thresh_binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    value_thresh_binary = cv2.Laplacian(thresh_binary, cv2.CV_64F).var()

    blur = cv2.GaussianBlur(img, (5, 5), 0)
    # blur = gaussian_blur(img, 5)
    ret3, thresh_otsu = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    value_otsu = cv2.Laplacian(thresh_otsu, cv2.CV_64F).var()

    if value_thresh_binary > value_otsu:
        print(value_thresh_binary)
        img = thresh_binary
    else:
        print(value_otsu)
        img = thresh_otsu

    return img


def text_edit(text):
    text.replace("\r\n", "")
    text = "  ".join(text.splitlines())
    while text.find('  ') != -1:
        text = text.replace('  ', ' ')
    text = text.lower()
    return text


def get_supplement_from_text(text):
    text = text_edit(text)
    supplement_list = []
    for supplement in db.session.query(ormE):
        if supplement.name.lower() in text:
            supplement_list.append(supplement)

    return supplement_list


def get_allergic(text, mobile_number):
    text = text_edit(text)
    allergic_from_text = []
    for allergies in db.session.query(ormAllergic).filter(ormAllergic.user_mobile == mobile_number):
        if allergies.name.lower() in text:
            allergic_from_text.append(allergies.name.lower())
    return allergic_from_text


def calculate_danger(supplement_list):
    danger = 0
    for row in supplement_list:
        if row.danger == "Висока":
            danger += 10
        elif row.danger == "Середня":
            danger += 7
        elif row.danger == "Низька":
            danger += 3
        elif row.danger == "Дуже низька":
            danger += 1
    # if len(allergic_from_text) > 0:
    #     list_of_allergic = allergic_from_text.split(",")
    #     danger += len(list_of_allergic) * 10
    return danger
