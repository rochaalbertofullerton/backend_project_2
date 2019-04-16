import flask,requests
from datetime import datetime, date
from flask import request , jsonify
from flask import Response
from feedgen.feed import FeedGenerator

app = flask.Flask(__name__)

@app.route('/summary', methods=['GET'])
def getsummary():
    req= requests.get('http://localhost/article',json={"count" : 10} , auth=('admin@email.com', 'adminpassword'))
    value = req.json()

   
    fg = FeedGenerator()
    fg.title('Summary of 10 newest articles')
    fg.link( href='http://localhost/feed/summary' )
    fg.subtitle('This is a cool feed!')
    fg.language('en')


    for x in value:
        fe = fg.add_entry()
        fe.title(x[0])
        fe.category(term= "Author "+ x[1])
        fe.category(term= "Date "+ x[2])
        fe.link(href="http://localhost"+x[3])
  
    fg.rss_file('summary_10.xml')
    
    return "RSS FILE CREATED summary_10.xml", 200

@app.route('/summary/content', methods=['GET'])
def getcontent():
    req= requests.get('http://localhost/article/content',json={"count" : 10} , auth=('admin@email.com', 'adminpassword'))
    value = req.json()
    fg = FeedGenerator()
    fg.title('A full feed')
    fg.link( href='http://localhost/feed/summary/content' )
    fg.subtitle('This is a cool feed!')
    fg.language('en')
    
    for x in value:
        print(x['count'])
        fe = fg.add_entry()
        fe.content(x['content'])
        outlst = [' '.join([str(c) for c in lst]) for lst in x['tag']]
        tag = ','.join(outlst)
        fe.category(term=tag)
        outlst = [' '.join([str(c) for c in lst]) for lst in x['count']]
        count = ' '.join(outlst)
        fe.category(term='Comment Count'+count)       
    fg.rss_file('content.xml')
    return "YOUR CONTENT WAS CREATED content.xml", 200

@app.route('/summary/comments', methods=['GET'])
def getcomments():
    req= requests.get('http://localhost/article',json={"count" : 10} , auth=('admin@email.com', 'adminpassword'))
    value = req.json()
    fg = FeedGenerator()
    fg.title('A full feed')
    fg.link( href='http://localhost/feed/summary/comments' )
    fg.subtitle('This is a cool feed!')
    fg.language('en')
   
    for x in value:
        split = x[3].split('/')
        reqcomment=requests.get('http://localhost/comment/get/'+split[2],json={"count" : 30} , auth=('admin@email.com', 'adminpassword'))
        print(reqcomment.json())
        fe = fg.add_entry()
        fe.title(x[0])
        outlst = [' '.join([str(c) for c in lst]) for lst in reqcomment.json()]
        comments = ','.join(outlst)        
        fe.category(term=comments)

    fg.rss_file('comments.xml')
    return "YOUR COMMENTS WAS CREATED comments.xml", 200
  