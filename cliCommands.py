import click, sqlite3, hashlib
from flask import Flask
from datetime import datetime, date


app = Flask(__name__)

@app.cli.command()
@click.argument('id')
@click.argument('title')
@click.argument('author')
@click.argument('text')
def postarticle(id, title, author, text):
    conn = sqlite3.connect("ZL1API.db")
    x = conn.cursor()
    keyurl = '/article/' + title + id
    x.execute('INSERT INTO articles (id, title, content, datecreated , datemod, author, url) Values(?,?,?,?,?,?,? ) ',(id,title, text,datetime.now(),datetime.now(),author,keyurl,))
    conn.commit() 
    x.close()


@app.cli.command()
@click.argument('id')
@click.argument('tag')
@click.argument('article_url')
def posttag(id, tag, article_url):
    conn = sqlite3.connect("ZL1API.db")
    x = conn.cursor()
    x.execute('INSERT INTO tag (id, tag, url) Values(?,?,?) ',(id,tag, article_url ,))
    conn.commit() 
    x.close()


@app.cli.command()
@click.argument('content')
@click.argument('article_url')
@click.argument('author')
def postcomment(content, article_url, author):
    conn = sqlite3.connect("ZL1API.db")
    x = conn.cursor()
    x.execute('INSERT INTO comments (content, url, author, date) Values(?,?,?,?) ',(content, article_url,author,datetime.now(),))
    conn.commit()
    x.close()

@app.cli.command()
@click.argument('name')
@click.argument('email')
@click.argument('password')
def postuser(name , email, password):
    conn = sqlite3.connect("ZL1API.db")
    x = conn.cursor()
    hashedpassword = hashlib.md5(password.encode())
    x.execute('INSERT INTO user (name, email, password) Values(?,?,?) ',(name,email, hashedpassword.hexdigest(),))
    conn.commit()
    x.close()