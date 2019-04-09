import flask, sqlite3, hashlib
from datetime import datetime, date
from flask import request , jsonify
from flask import Response
from flask_basicauth import BasicAuth 

app = flask.Flask(__name__)
app.config["DEBUG"] = True


# Create a class to ensure user exists & autheticate it 


class auth_User(BasicAuth):
    def check_credentials(self, username, password):
        conn = sqlite3.connect("ZL1API.db")
        x = conn.cursor()
        x.execute("SELECT password FROM user WHERE email=?",(username, ))
        value = x.fetchone()

        if value != None:
            hashedpassword = hashlib.md5(password.encode())
            if hashedpassword.hexdigest() == value[0]:
                return True
            else:
                return False
        else:
            return False 
                
basic_auth = auth_User(app)




@app.route('/users', methods=['Post'])
def postUser():
    conn = sqlite3.connect("ZL1API.db")
    x = conn.cursor()
    data = request.get_json()
    keyname = data["name"]
    keyemail = data["email"]
    keypassword = data["password"]
    hashedpassword = hashlib.md5(keypassword.encode())

    try:
        x.execute('INSERT INTO user (name, email, password) Values(?,?,?) ',(keyname,keyemail, hashedpassword.hexdigest(),))
        conn.commit()
        x.close()
        return jsonify("CREATED") , 201
    except Exception as er:
        x.close()
        return str(er), 406


#Implement Authentication in DELETE/CHANGE PASSWORD ==== 
@app.route('/users', methods=['DELETE'])
@basic_auth.required
def delete_user(): 
    conn = sqlite3.connect("ZL1API.db")
    x = conn.cursor()
    data = request.get_json()
    key = data["email"]
    x.execute('SELECT * FROM user WHERE email=?' , (key,))
    value = x.fetchone()
    
    if value != None:

            x.execute('DELETE FROM user WHERE email=?' , (key,))
            conn.commit()
            x.close()
            return "DELETED" , 202

    else:
        x.close()
        return jsonify("User Not Found"), 404 

@app.route('/users', methods=['PATCH'])
@basic_auth.required
def change_pwd(): 
   conn = sqlite3.connect("ZL1API.db")
   x = conn.cursor()
   data = request.get_json()
   keyemail = data ["email"]
   keypassword = data["password"]
   x.execute("SELECT * FROM user WHERE email =?", (keyemail,))
   value = x.fetchone()
   if value != None:
        hashedpassword = hashlib.md5(keypassword.encode())
        x.execute('UPDATE user SET password =? WHERE email=?' , (hashedpassword.hexdigest(),keyemail,))
        conn.commit()
        x.close()
        return jsonify("UPDATED"), 202
   else:
       x.close()
       return jsonify("CONTENT NOT FOUND"), 404

app.run()
