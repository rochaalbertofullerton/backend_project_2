import flask, requests, sqlite3, json
from datetime import datetime, date
from flask import request , jsonify
from flask_basicauth import BasicAuth 
app = flask.Flask(__name__)



#POST A NEW ARTICLE
#This route gets activited when a POST is made. It does expect json 
#The json must contain and id, text, title, author
#The author must be created before before an article can be posted, the author is a foreign key
#If an error occurs it will reply with the error and 406 Not acceptable
@app.route('/article', methods=['POST'])
def postArticle():
    conn = sqlite3.connect("articles.db")
    x = conn.cursor()
    data = request.get_json()
    keytext = data["text"]
    keytitle = data["title"]
    keyauthor = data["author"]
    keyurl = '/article/' + keytitle.replace(" ", "") 
    try:
        x.execute('INSERT INTO articles (articles_title, articles_content, articles_created , articles_modified, articles_users_author, articles_url) Values(?,?,?,?,?,? ) ',(keytitle, keytext,datetime.now(),datetime.now(),keyauthor,keyurl,))
        conn.commit()
        x.close()
        return jsonify("CREATED") , 201
    except Exception as er:
        x.close()
        return str(er), 400


#RETREVE AN INDIVIDUAL ARTICLE
#This route get activated when you pass an article name after the the root file of '/article/
#Example ----> /article/The Road Not Taken1 {Hit Enter}
#If an error is occurs a 204 status will be returned not content found else if no error is found it will return a 200 OK
@app.route("/article/<path:article>", methods=['GET'])
def getArticle(article):
    conn = sqlite3.connect("articles.db")
    x = conn.cursor()
    key = '/article/' + article

    try:
        x.execute('SELECT * FROM articles WHERE articles_url=?' , (key,))
        value = x.fetchone()
        x.close()
        if value == None:
            return "<h1>Article Not Found</h1>", 400
        else:
            return jsonify(value[2]),200
    except Exception as er:
        x.close()
        return str(er), 400

# EDIT AN INDIVIDUAL ARTICLE
#This route gets activited when a PATCH is made. It does expect json 
#The json must contain  "text"
#Example ----> /article/The Road Not Taken1 {Hit Enter}
#If an error occurs it will reply with the error and 204 There was no article with that url
@app.route("/article/<path:article>", methods=['PATCH'])
def patchArticle(article):
    conn = sqlite3.connect("articles.db")
    x = conn.cursor()
    data = request.get_json()
    keyid = '/article/' + article
    keytext = data ["text"]
    try:
        x.execute("SELECT * FROM articles WHERE articles_url =?", (keyid,))
        value = x.fetchone()
        if value != None:
            try:
                x.execute('UPDATE articles SET articles_content=?, articles_modified=? WHERE articles_url=?' , (keytext, datetime.now(), keyid,))
                conn.commit()
                x.close()
                return jsonify("UPDATED"), 202
            except Exception as er:
                x.close()
                return str(er), 406
        else:
            x.close()
            return jsonify("CONTENT NOT FOUND"), 204
    except Exception as er:
        x.close()
        return str(er), 406

#DELETE A SPECIFIC EXISTING ARTICLE
#This route gets activited when a DELETE is made. It does expect json 
#The json must contain and id
#If an error occurs it will reply with the error and 204 There was no article with that id
@app.route("/article/<path:article>", methods=['DELETE'])
def deleteArticle(article):
    conn = sqlite3.connect("articles.db")
    x = conn.cursor()
    key = '/article/' + article
    try:
        x.execute("SELECT * FROM articles WHERE articles_url =?", (key,))
        value = x.fetchone()
        if value != None:
            try:
                x.execute('DELETE FROM articles WHERE articles_url=?' , (key,))
                conn.commit()
                x.close()
                return jsonify("DELETED"), 202
            except Exception as er:
                x.close()
                return str(er), 406
        else:
            x.close()
            return jsonify("article does not exist"), 204
    except Exception as er:
        x.close()
        return str(er), 406

#RETRIEVE THE ENITRE CONTENTS (INCLUDING ARTICLE TEXT) FOR THE N MOST RECENT ARTICLE


@app.route('/article/content', methods=['GET'] )
def getArticleContent():
    conn = sqlite3.connect("articles.db")
    x = conn.cursor()
    data = request.get_json()
    key = data['count']
    x.execute(' SELECT * FROM (SELECT articles_content, articles_url FROM articles ORDER BY articles_created DESC LIMIT ? )', (key,))
    value = x.fetchall()
    re=[]
    for t in value:

        split = t[1].split('/')
        reqtag= requests.get('http://localhost/tag/'+split[2],json={"count" : key} , auth=('admin@email.com', 'adminpassword'))
        reqcomment=requests.get('http://localhost/comment/'+split[2],json={"count" : key} , auth=('admin@email.com', 'adminpassword'))
        c ={'content' : t[0],
             'tag' :reqtag.json(), 
            'count' :reqcomment.json()}
        re.append(c)
         
    x.close()
    if value == None:
        return jsonify("CONTENT NOT FOUND"), 402
    else:
        return jsonify(re),200



#RETRIEVE METADATA FOR THE  N MOST RECENT ARTICLES, INCLUDING TITLE, AUTOR, DATE, AND URL
#This route gets activated the param "count" which allows the user to enter how many article they want. It must be in the body in json
#This route will get the most recent article added to the database
#It will RETURN the whole row with all informtion 
#If an error is occurs a 204 status will be returned not content found else if no error is found it will return a 200 OK 

@app.route('/article', methods=['GET'] )
def getNthArticle():
    conn = sqlite3.connect("articles.db")
    data = request.get_json()
    key = data["count"]
    x = conn.cursor()
    try:
        x.execute('SELECT * FROM( SELECT articles_title, articles_users_author, articles_created, articles_url FROM articles ORDER BY articles_created DESC LIMIT ? )',(key,))
        value = x.fetchall()
        x.close()
        if value == None:
            return "<h1>Article Not Found</h1>", 204
        else:
            return jsonify(value),200
    except Exception as er:
        x.close()
        return str(er), 406



app.run() 
