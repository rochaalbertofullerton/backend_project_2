import flask ,sqlite3, hashlib
from datetime import datetime, date
from flask import request, jsonify
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

# POST A NEW COMMENT ON AN ARTICLE
@app.route('/comments/<path:article>', methods=['POST'])
def postComment(article):
    conn = sqlite3.connect("ZL1API.db")
    x = conn.cursor()
    data = request.get_json()
    keycomment = data["comment"]
    keyauthor = data["author"]
    keyurl = '/article/' + article
    x.execute("SELECT * FROM articles WHERE url =?", (keyurl,))
    value = x.fetchone()
    if value != None:
        try:
            x.execute('INSERT INTO comments (content, url, author, date) Values(?,?,?,?) ',(keycomment, keyurl,keyauthor,datetime.now(),))
            conn.commit()
            x.close()
            return jsonify("CREATED"), 201
        except Exception as er:
            x.close()
            return str(er)
    else:
        x.close()
        return jsonify("Article not found"), 402


# DELETE AN INDIVIDUAL COMMENT 
@app.route('/comments', methods=['DELETE'])
@basic_auth.required
def deleteComment():
    conn = sqlite3.connect("ZL1API.db")
    x = conn.cursor()
    data = request.get_json()
    key = data["id"]
    x.execute('SELECT * FROM comments WHERE id=?', (key,))
    value = x.fetchone()

    if value != None:
        x.execute('DELETE FROM comments WHERE id=? ', (key,))
        conn.commit()
        x.close()
        return "DELETED", 202
    else:
        x.close()
        return jsonify("CONTENT NOT FOUND"), 402

    
# RETRIEVE THE NUMBER OF COMMENTS ON A GIVEN ARTICLE
@app.route('/comments/<path:article>', methods=['GET'])
def getcommentsforarticle(article):
    conn = sqlite3.connect("ZL1API.db")
    x = conn.cursor()
    keyarticle = '/article/' + article
    x.execute('SELECT content  FROM comments WHERE url=?', (keyarticle,))
    value = x.fetchall()
    if value != []:
        x.close()
        return jsonify(value), 202
    else:
        x.close()
        return "NO CONTENT", 204


# RETRIEVE THE 'N' MOST RECENT COMMENTS ON AN URL
@app.route('/comments', methods=['GET'] )
def getNthArticle():
    conn = sqlite3.connect("ZL1API.db")
    data = request.get_json()
    key = data["count"]
    x = conn.cursor()
    x.execute('SELECT * FROM( SELECT content FROM comments ORDER BY date DESC LIMIT ? )',(key,))
    value = x.fetchall()
    x.close()
    if value == None:
        return "<h1>Article Not Found</h1>", 204
    else:
        return jsonify(value),200

app.run()