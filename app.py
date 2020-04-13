from datetime import datetime

from PIL import Image
from flask import Flask, request, jsonify
from pytesseract import pytesseract

from orm.model import db, ormPhoto, ormUser

app = Flask(__name__)
app.secret_key = 'key'
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:meizu123@localhost/ohrydko'

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
        text = pytesseract.image_to_string(Image.open(file), lang='ukr')

        db.session.add(ormPhoto(user, file.read()))
        db.session.commit()

        return jsonify(status="200", success="true", result=text)
    return jsonify(status="200", success="false", text="server error")


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
        mobile = request.args.get('mobile')
        password = request.args.get('password')

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
