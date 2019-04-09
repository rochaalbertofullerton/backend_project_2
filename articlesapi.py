import flask, sqlite3, hashlib
from datetime import datetime, date
from flask import request , jsonify
from flask_basicauth import BasicAuth 
app = flask.Flask(__name__)
app.config["DEBUG"] = True



class auth_pass(BasicAuth):
    def check_credentials(self, username, password):
        conn = sqlite3.connect("ZL1API.db")
        x = conn.cursor()
        x.execute("SELECT password FROM user WHERE email=?",(username, ))
        value = x.fetchone()
        print(value)

        if value != None:
            
            hashedpassword = hashlib.md5(password.encode())
            if hashedpassword.hexdigest() == value[0]:
                return True
            else:
                return False
        else:
            return False 

basic_pass = auth_pass(app)


#POST A NEW ARTICLE
#This route gets activited when a POST is made. It does expect json 
#The json must contain and id, text, title, author
#The author must be created before before an article can be posted, the author is a foreign key
#If an error occurs it will reply with the error and 406 Not acceptable
@app.route('/article', methods=['POST'])
@basic_pass.required
def postArticle():
    conn = sqlite3.connect("ZL1API.db")
    x = conn.cursor()
    data = request.get_json()
    keyid = data["id"]
    keytext = data["text"]
    keytitle = data["title"]
    keyauthor = data["author"]
    keyurl = '/article/' + keytitle + str(keyid)

    try:
        x.execute('INSERT INTO articles (id, title, content, datecreated , datemod, author, url) Values(?,?,?,?,?,?,? ) ',(keyid,keytitle, keytext,datetime.now(),datetime.now(),keyauthor,keyurl,))
        conn.commit()
        x.close()
        return jsonify("CREATED") , 201
    except Exception as er:
        x.close()
        return str(er), 406


#RETREVE AN INDIVIDUAL ARTICLE
#This route get activated when you pass an article name after the the root file of '/article/
#Example ----> /article/The Road Not Taken1 {Hit Enter}
#If an error is occurs a 204 status will be returned not content found else if no error is found it will return a 200 OK
@app.route("/article/<path:article>", methods=['GET'])
def getArticle(article):
    conn = sqlite3.connect("ZL1API.db")
    x = conn.cursor()
    key = '/article/' + article
    x.execute('SELECT * FROM articles WHERE url=?' , (key,))
    value = x.fetchone()
    x.close()
    if value == None:
        return "<h1>Article Not Found</h1>", 204
    else:
        return jsonify(value[2]),200

# EDIT AN INDIVIDUAL ARTICLE
#This route gets activited when a PATCH is made. It does expect json 
#The json must contain  "text"
#Example ----> /article/The Road Not Taken1 {Hit Enter}
#If an error occurs it will reply with the error and 204 There was no article with that url
@app.route("/article/<path:article>", methods=['PATCH'])
@basic_pass.required
def patchArticle(article):
    conn = sqlite3.connect("ZL1API.db")
    x = conn.cursor()
    data = request.get_json()
    keyid = '/article/' + article
    keytext = data ["text"]
    x.execute("SELECT * FROM articles WHERE url =?", (keyid,))
    value = x.fetchone()
    if value != None:
        x.execute('UPDATE articles SET content=?, datemod=? WHERE url=?' , (keytext, datetime.now(), keyid,))
        conn.commit()
        x.close()
        return jsonify("UPDATED"), 202
    else:
        x.close()
        return jsonify("CONTENT NOT FOUND"), 204

#DELETE A SPECIFIC EXISTING ARTICLE
#This route gets activited when a DELETE is made. It does expect json 
#The json must contain and id
#If an error occurs it will reply with the error and 204 There was no article with that id
@app.route("/article/<path:article>", methods=['DELETE'])
@basic_pass.required
def deleteArticle(article):
    conn = sqlite3.connect("ZL1API.db")
    x = conn.cursor()
    key = '/article/' + article
    x.execute("SELECT * FROM articles WHERE url =?", (key,))
    value = x.fetchone()
    if value != None:
        x.execute('DELETE FROM articles WHERE url=?' , (key,))
        conn.commit()
        x.close()
        return jsonify("DELETED"), 202
    else:
        x.close()
        return jsonify("article does not exist"), 204


#RETRIEVE THE ENITRE CONTENTS (INCLUDING ARTICLE TEXT) FOR THE N MOST RECENT ARTICLE
@app.route('/article/content', methods=['GET'] )
def getArticleContent():
    conn = sqlite3.connect("ZL1API.db")
    x = conn.cursor()
    x.execute('SELECT articles.content , articles.author , tag.tag , comments.content FROM articles inner join tag on articles.url = tag.url inner join comments on tag.url = comments.url')
    value = x.fetchall()
    x.close()
    if value == None:
        return jsonify("CONTENT NOT FOUND"), 402
    else:
        return jsonify(value),200



#RETRIEVE METADATA FOR THE  N MOST RECENT ARTICLES, INCLUDING TITLE, AUTOR, DATE, AND URL
#This route gets activated the param "count" which allows the user to enter how many article they want. It must be in the body in json
#This route will get the most recent article added to the database
#It will RETURN the whole row with all informtion 
#If an error is occurs a 204 status will be returned not content found else if no error is found it will return a 200 OK 
@app.route('/article', methods=['GET'] )
def getNthArticle():
    conn = sqlite3.connect("ZL1API.db")
    data = request.get_json()
    key = data["count"]
    x = conn.cursor()
    x.execute('SELECT * FROM( SELECT * FROM articles ORDER BY datecreated DESC LIMIT ? )',(key,))
    value = x.fetchall()
    x.close()
    if value == None:
        return "<h1>Article Not Found</h1>", 204
    else:
        return jsonify(value),200



app.run() 