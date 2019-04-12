import flask, sqlite3, hashlib
from datetime import datetime, date
from flask import request , jsonify
from flask_basicauth import BasicAuth 
app = flask.Flask(__name__)
app.config["DEBUG"] = True



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

#ADD TAGS FOR NEW URL  & ADD TAGS TO AN EXISTING URL
#The json must contain "id", "tag"
#Example ----> /tag/The Road Not Taken1 {Hit Enter}
#The author must be created before before an article you can post a tag
#If an error occurs it will reply with the error and 204 Not acceptable
@app.route('/tag/<path:article>', methods=['POST'])
@basic_auth.required
def postTag(article):
    conn = sqlite3.connect("ZL1API.db")
    x = conn.cursor()
    data = request.get_json()
    keyid = data["id"]
    keytag = data["tag"]
    keyurl ='/article/' + article
    x.execute("SELECT * FROM articles WHERE url =?", (keyurl,))
    value = x.fetchone()
    if value != None:
        try:
            x.execute('INSERT INTO tag (id, tag, url) Values(?,?,?) ',(keyid,keytag, keyurl,))
            conn.commit()
            x.close()
            return jsonify("CREATED") , 201
        except Exception as er:
            x.close()
            return str(er)
    else:
        x.close()
        return jsonify("Article not found"), 204
    
#REMOVE ONE OR MORE TAGS FROM AN INDIVIDUAL URL
#The json must contain  "tag"
#Example ----> /tag/The Road Not Taken1 {Hit Enter}
#If an error occurs it will reply with the error and 204 Not acceptable
@app.route('/tag/<path:article>', methods=['DELETE'])
@basic_auth.required
def deleteArticle(article):
    conn = sqlite3.connect("ZL1API.db")
    x = conn.cursor()
    data = request.get_json()
    key = data["tag"]
    keyurl ='/article/' + article
    x.execute('SELECT * FROM articles WHERE url=?' , (keyurl,))
    value = x.fetchone()
    
    if value != None:
        x.execute('SELECT * FROM tag WHERE url=? AND tag=?' , (keyurl,key,))
        valuetag = x.fetchone()
        if valuetag != None:
            x.execute('DELETE FROM tag WHERE tag=? AND  url=?' , (key,keyurl,))
            conn.commit()
            x.close()
            return "DELETED" , 202
        else:
             x.close()
             return jsonify("Tag to URL does not Exists"), 204 
    else:
        x.close()
        return jsonify("article does not exist"), 204 


#RETRIEVE THE A LIST URLS WITH A GIVEN TAG
#Example ----> /tag/The Road Not Taken1 {Hit Enter}
@app.route("/tag/<path:tag>", methods=['GET'])
def getarticleswithTag(tag):
    conn = sqlite3.connect("ZL1API.db")
    x = conn.cursor()
    x.execute('SELECT url  FROM tag WHERE tag=?', (tag,))
    value = x.fetchall()
    if value != []:
        x.close()
        return jsonify(value), 202
    else:
        x.close()
        return "NO CONTENT", 204

#RETRIEVE THE TAGS FOR AN INDIVIDUAL URL
#Example ----> /tag/The Road Not Taken1 {Hit Enter}
@app.route('/tag/url/<path:article>', methods=['GET'])
def gettagforUrl(article):
    conn = sqlite3.connect("ZL1API.db")
    x = conn.cursor()
    key = '/article/' + article
    x.execute('SELECT tag FROM tag WHERE url=?', (key,))
    value = x.fetchall()
    if value != []:
        x.close()
        return jsonify(value), 202
    else:
        x.close()
        return jsonify("NO CONTENT"), 204


app.run()