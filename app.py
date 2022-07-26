from flask import Flask, jsonify,request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
import os
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_mail import Mail, Message

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'main.db')
app.config['JWT_SECRET_KEY'] = 'my-secret-key'
app.config['MAIL_SERVER']='smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '4297f9d037d051'
app.config['MAIL_PASSWORD'] = '476c92b596f34e'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)
mail=Mail(app)

@app.cli.command('db_create')
def createDb():
    db.create_all()
    print("DB's are created!")

@app.cli.command('db_drop')
def dropDb():
    db.drop_all()
    print("DB's are droped!")

@app.cli.command('db_seed')
def seedDb():
    jo = User(first_name='Jo',
              last_name='Grit',
              email='jogrit@gmail.com',
              password='1')

    db.session.add(jo)
    db.session.commit()
    print("db seeded!")

@app.route('/user_info', methods=['GET'])
def userInfo():
    user_list = User.query.all()
    result = users_schema.dump(user_list)
    return jsonify(result)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/fibo')
def fibo():
    return 'Fibonnacci!'

@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    test = User.query.filter_by(email=email).first()
    if test:
        return jsonify(message='That email already exist'), 409
    else:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        user = User(first_name=first_name,last_name=last_name,password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify(message='User create successfully'), 201


@app.route('/login',methods=['POST'])
def login():
    if request.is_json:
        email = request.json['email']
        password = request.json['password']
    else:
        email = request.form['email']
        password = request.form['password']

    test = User.query.filter_by(email=email,password=password).first()
    if test:
        access_token = create_access_token(identity=email)
        return jsonify(message='Login succeeded!',access_token=access_token)
    else:
        return jsonify(message='Bad email or password'),401

@app.route('/retrieve_password/<string:email>', methods=['GET'])
def retrieve_password(email: str):
    user = User.query.filter_by(email=email).first()
    if user:
        msg = Message('your api password is'+ user.password, sender="admin", recipients=[email])
        mail.send(msg)
        return jsonify(message='Password send to '+email)
    else:
        return jsonify(message='That email doesn\'t exist'),401

@app.route('/params')
def parems():
    name = request.args.get('name')
    age = int(request.args.get('age'))
    if age < 18:
        return jsonify(message="Sorry, you are not old enough"), 401
    else:
        return jsonify(message='Hi '+name+', you are old enough')

@app.route('/url_veriables/<string:name>/<int:age>')
def url_veriables(name: str, age: int):
    if age < 18:
        return jsonify(message="Sorry, you are not old enough"), 401
    else:
        return jsonify(message='Hi '+name+', you are old enough')

class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id','first_name','last_name','email','password')

user_schema = UserSchema()
users_schema = UserSchema(many=True)

if __name__ == '__main__':
    app.run()
