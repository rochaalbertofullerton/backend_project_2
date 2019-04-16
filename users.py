import flask, sqlite3, hashlib, requests
from datetime import datetime, date
from flask import request , jsonify
from flask import Response

app = flask.Flask(__name__)


@app.route('/users', methods=['Post'])
def postUser():
    conn = sqlite3.connect("users.db")
    x = conn.cursor()
    data = request.get_json()
    keyname = data["name"]
    keyemail = data["email"]
    keypassword = data["password"]
    hashedpassword = hashlib.md5(keypassword.encode())
    try:
        x.execute('INSERT INTO users (users_name, users_email, users_password) Values(?,?,?) ',(keyname,keyemail, hashedpassword.hexdigest(),))
        conn.commit()
        x.close()
        return jsonify("CREATED") , 201
    except Exception as er:
        x.close()
        return str(er), 400


@app.route('/users', methods=['DELETE'])
def delete_user(): 
    conn = sqlite3.connect("users.db")
    x = conn.cursor()
    data = request.get_json()
    key = data["email"]
    x.execute('SELECT * FROM users WHERE users_email=?' , (key,))
    value = x.fetchone()
    
    if value != None:

            x.execute('DELETE FROM users WHERE users_email=?' , (key,))
            conn.commit()
            x.close()
            return "DELETED" , 202

    else:
        x.close()
        return jsonify("User Not Found"), 404 

@app.route('/users', methods=['PATCH'])
def change_pwd(): 
   conn = sqlite3.connect("users.db")
   x = conn.cursor()
   data = request.get_json()
   keyemail = data ["email"]
   keypassword = data["password"]
   x.execute("SELECT * FROM users WHERE users_email =?", (keyemail,))
   value = x.fetchone()
   if value != None:
        hashedpassword = hashlib.md5(keypassword.encode())
        x.execute('UPDATE users SET users_password =? WHERE users_email=?' , (hashedpassword.hexdigest(),keyemail,))
        conn.commit()
        x.close()
        return jsonify("UPDATED"), 202
   else:
       x.close()
       return jsonify("USER NOT FOUND"), 404

@app.route('/users/auth')
def auth():
    conn = sqlite3.connect('users.db')
    x = conn.cursor()
    auth = request.authorization 
    x.execute('SELECT users_password FROM users WHERE users_email=?' , (auth.username,))
    value = x.fetchone()
    a = {"status" : "ok"}
    b = {"status" : "bad" }
    if value[0]== hashlib.md5(auth.password.encode()).hexdigest():
        return jsonify(a),200
    else:
        return jsonify(b),403


    


   

app.run()
