from datetime import datetime

import numpy
from PIL import Image
from cv2 import cv2
from flask import Flask, request, jsonify
from pytesseract import pytesseract

from orm.model import db, ormHistory, ormUser, ormE, ormAllergic, ormProductHasSupplement

app = Flask(__name__)
app.secret_key = 'key'
env = "dev"

if env == "dev":
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:meizu123@localhost/ohrydko'
else:
    app.debug = False
    app.config[
        'SQLALCHEMY_DATABASE_URI'] = 'postgres://pzkhopobswyvsu:ec792630a99f73019ca28361fac9374f9b65cdaa29b4649c2' \
                                     'f76295bc9f189ef@ec2-34-225-82-212.compute-1.amazonaws.com:5432/d3mvjnn9i3nout'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
db.app = app
db.create_all()


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        mobile_number = request.form['mobile_phone']
        name = request.form['name']

        img = image_transformation(file.read())

        text = pytesseract.image_to_string(Image.fromarray(img), lang='ukr')
        text.replace("\r\n", "")
        text = "  ".join(text.splitlines())
        while text.find('  ') != -1:
            text = text.replace('  ', ' ')
        text = text.lower()
        supplement_list = []
        for supplement in db.session.query(ormE):
            if supplement.name.lower() in text:
                supplement_list.append(supplement)
                db.session.add(ormProductHasSupplement(name, supplement.number_supplement))

        allergic_from_text = ''
        for allergic in db.session.query(ormAllergic):
            if allergic.name.lower() in text:
                allergic_from_text = allergic.name.lower() + ","
        db.session.add(ormHistory(name, mobile_number, file.read(), allergic_from_text))
        db.session.commit()

        return jsonify(status="200", success="true", result=text,
                       supplement=[supp.serialize() for supp in supplement_list], allergic=allergic_from_text)
    return jsonify(status="200", success="false", text="server error")


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
    # check bluring for threst binary and otsu method
    ret, thresh_binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    value_thresh_binary = cv2.Laplacian(thresh_binary, cv2.CV_64F).var()

    blur = cv2.GaussianBlur(img, (5, 5), 0)
    ret3, thresh_otsu = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    value_otsu = cv2.Laplacian(thresh_otsu, cv2.CV_64F).var()

    if value_thresh_binary > value_otsu:
        print(value_thresh_binary)
        img = thresh_binary
    else:
        print(value_otsu)
        img = thresh_otsu

    return img


@app.route('/registration', methods=['POST'])
def registration():
    if request.method == 'POST':
        try:
            mobile = request.form['mobile']
            name = request.form['name']
            last_name = request.form['last_name']
            birthday = request.form['birthday']
            datetime_object = datetime.strptime(birthday, '%d-%m-%Y')
            user_name = request.form['user_name']
            password = request.form['password']
            for user in db.session.query(ormUser).filter(ormUser.mobile_number == mobile):
                if user.mobile_number == mobile:
                    return jsonify(status="200", success="false", text="user already exists")

            db.session.add(
                ormUser(name=name, mobile=mobile, last_name=last_name, birthday=datetime_object,
                        user_name=user_name,
                        password=password))
            db.session.commit()
            return jsonify(status="200", success="true", mobile_number=mobile)
        except:
            return jsonify(status="500", success="false", text="invalid params")

    return jsonify(status="200", success="false", text="server error")


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        mobile = request.form['mobile']
        password = request.form['password']
        print(mobile)
        try:
            for user in db.session.query(ormUser).filter(ormUser.mobile_number == mobile):
                if user.mobile_number == mobile:
                    if user.password == password:
                        return jsonify(status="200", success="true", mobile_number=mobile)
                    else:
                        return jsonify(status="200", success="false", text="incorrect password")

        except:
            return jsonify(status="500", success="false", text="server error")

    return jsonify(status="200", success="false", text="user does't exists")


@app.route('/supplement', methods=['GET'])
def get_supplement():
    if request.method == "GET":
        e = []
        try:
            for supplement in db.session.query(ormE):
                e.append(supplement)
        except:
            return jsonify(status="200", success="false", text="server error")
        return jsonify(status="200", success="true", supplement=[supp.serialize() for supp in e])
    return jsonify(status="200", success="false", text="server error")


if __name__ == '__main__':
    app.run()
