import flask ,sqlite3, hashlib, requests
from datetime import datetime, date
from flask import request, jsonify
from flask_basicauth import BasicAuth 
app = flask.Flask(__name__)



# POST A NEW COMMENT ON AN ARTICLE

@app.route('/comments/<path:article>', methods=['POST'])
def postComment(article):
    conn = sqlite3.connect("comments.db")
    x = conn.cursor()
    data = request.get_json()
    keycomment = data["comment"]
    keyauthor = data["author"]
    keyurl = '/article/' + article
    req = requests.get('http://localhost/article/'+article, auth=('admin@email.com', 'adminpassword'))
    if req.status_code == 200:
        try:
            x.execute('INSERT INTO comments (comments_content, comments_articles_url, comments_users_author, comments_created) Values(?,?,?,?) ',(keycomment, keyurl,keyauthor,datetime.now(),))
            conn.commit()
            x.close()
            return jsonify("CREATED"), 201
        except Exception as er:
            x.close()
            return str(er)
    else:
        x.close()
        return 'article not found', 404



# DELETE AN INDIVIDUAL COMMENT 
@app.route('/comments', methods=['DELETE'])
def deleteComment():
    conn = sqlite3.connect("comments.db")
    x = conn.cursor()
    data = request.get_json()
    key = data["id"]
    try:
        x.execute('DELETE FROM comments WHERE comments_id=? ', (key,))
        conn.commit()
        x.close()
        return "DELETED", 202
    except Exception as er:
        x.close()
        return str(er), 204

    
# RETRIEVE THE NUMBER OF COMMENTS ON A GIVEN ARTICLE

@app.route('/comments/<path:article>', methods=['GET'])
def getcommentsforarticle(article):
    conn = sqlite3.connect("comments.db")
    x = conn.cursor()
    keyarticle = '/article/' + article
    x.execute('SELECT count(*)  FROM comments WHERE comments_articles_url=?', (keyarticle,))
    value = x.fetchall()
    if value != []:
        x.close()
        return jsonify(value), 202
    else:
        x.close()
        return "NO CONTENT", 204


# RETRIEVE THE 'N' MOST RECENT COMMENTS ON AN URL
@app.route('/comments/get/<path:article>', methods=['GET'] )
def getNthArticle(article):
    conn = sqlite3.connect("comments.db")
    data = request.get_json()
    key = data["count"]
    keyarticle = '/article/' + article
    x = conn.cursor()
    x.execute('SELECT * FROM( SELECT comments_content FROM comments where comments_articles_url = ? ORDER BY comments_created DESC LIMIT ?)',(keyarticle, key,))
    value = x.fetchall()
    x.close()
    if value == None:
        return "<h1>Article Not Found</h1>", 204
    else:
        return jsonify(value),200

app.run()