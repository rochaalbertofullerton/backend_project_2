import flask, sqlite3, hashlib, requests
from datetime import datetime, date
from flask import request , jsonify
app = flask.Flask(__name__)


#ADD TAGS FOR NEW URL  & ADD TAGS TO AN EXISTING URL
#The json must contain "id", "tag"
#Example ----> /tag/The Road Not Taken1 {Hit Enter}
#The author must be created before before an article you can post a tag
#If an error occurs it will reply with the error and 204 Not acceptable
@app.route('/tag/<path:article>', methods=['POST'])
def postTag(article):
    conn = sqlite3.connect("tags.db")
    x = conn.cursor()
    data = request.get_json()
    keytag = data["tag"]
    keyurl ='/article/' + article
    req = requests.get('http://localhost:5000'+keyurl)

    if req.status_code == 200:
        try:
            x.execute('INSERT INTO tags (tags_content, tags_articles_url) Values(?,?) ',(keytag, keyurl,))
            conn.commit()
            x.close()
            return jsonify('CREATED') , 201
        except Exception as er:
            x.close()
            return str(er)
    else:
        x.close()
        return jsonify('ARTICLE NOT FOUND'), 404
    
#REMOVE ONE OR MORE TAGS FROM AN INDIVIDUAL URL
#The json must contain  "tag"
#Example ----> /tag/The Road Not Taken1 {Hit Enter}
#If an error occurs it will reply with the error and 204 Not acceptable
@app.route('/tag/<path:article>', methods=['DELETE'])
def deleteArticle(article):
    conn = sqlite3.connect("tags.db")
    x = conn.cursor()
    data = request.get_json()
    key = data["tag"]
    keyurl ='/article/' + article
    req = requests.get('http://localhost:5000'+keyurl)
    
    if req.status_code == 200:
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
@app.route("/tag/get/<path:article>", methods=['GET'])
def getarticleswithTag(article):
    conn = sqlite3.connect("tags.db")
    keytag = '/article/' + article
    x = conn.cursor()
    x.execute('SELECT tags_articles_url  FROM tags WHERE tags_content=?', (keytag,))
    value = x.fetchall()
    if value != []:
        x.close()
        return jsonify(value), 202
    else:
        x.close()
        return "NO CONTENT", 204

#RETRIEVE THE TAGS FOR AN INDIVIDUAL URL
#Example ----> /tag/The Road Not Taken1 {Hit Enter}
@app.route('/tag/<path:article>', methods=['GET'])
def gettagforUrl(article):
    conn = sqlite3.connect("tags.db")
    x = conn.cursor()
    key = '/article/' + article
    x.execute('SELECT tags_content FROM tags WHERE tags_articles_url=?', (key,))
    value = x.fetchall()
    if value != []:
        x.close()
        return jsonify(value), 202
    else:
        x.close()
        return jsonify("NO CONTENT"), 204


app.run()