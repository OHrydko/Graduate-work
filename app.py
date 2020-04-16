from datetime import datetime

import numpy
from PIL import Image
from cv2 import cv2
from flask import Flask, request, jsonify
from pytesseract import pytesseract

from orm.model import db, ormPhoto, ormUser

app = Flask(__name__)
app.secret_key = 'key'
env = "prod"

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


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        user = request.form['mobile_phone']

        img = image_transformation(file.read())

        text = pytesseract.image_to_string(Image.fromarray(img), lang='ukr')
        db.session.add(ormPhoto(user, file.read()))
        db.session.commit()

        return jsonify(status="200", success="true", result=text)
    return jsonify(status="200", success="false", text="server error")


def image_transformation(file):
    img = cv2.imdecode(numpy.frombuffer(file, numpy.uint8), cv2.IMREAD_UNCHANGED)
    img = cv2.resize(img, None, fx=1.2, fy=1.2, interpolation=cv2.INTER_CUBIC)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    kernel = numpy.ones((1, 1), numpy.uint8)
    img = cv2.dilate(img, kernel, iterations=1)
    img = cv2.erode(img, kernel, iterations=1)
    img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)

    ret, example_img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    value_thresh_binary = cv2.Laplacian(example_img, cv2.CV_64F).var()

    blur = cv2.GaussianBlur(img, (5, 5), 0)
    ret3, img_ex = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    value_otsu = cv2.Laplacian(img_ex, cv2.CV_64F).var()

    if value_thresh_binary > value_otsu:
        print(value_thresh_binary)
        return example_img
    print(value_otsu)
    return img_ex


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
            db.session.add(
                ormUser(name=name, mobile=mobile, last_name=last_name, birthday=datetime_object, user_name=user_name,
                        password=password))
            db.session.commit()
            return jsonify(status="200", success="true")
        except:
            return jsonify(status="500", success="false", text="don't insert, crash")

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
            return jsonify(status="500", success="false", text="don't insert, crash")

    return jsonify(status="200", success="false", text="user does't exists")


if __name__ == '__main__':
    app.run()
