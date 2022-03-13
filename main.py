from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from datetime import datetime
from werkzeug.utils import secure_filename
import json
import os
import math


####################### Open databse file ##############################

with open('config.json',"r") as js:
    para = json.load(js)["para"]

####################### App initlization ###############################

app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config["SQLALCHEMY_DATABASE_URI"] = para['local_host']
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = para['upload_location']
db = SQLAlchemy(app)

########################## creating database  model for contect ##################

class Contact(db.Model):

    "sno,name,email,phone_num ,mess"
    sno       = db.Column(db.Integer, primary_key=True)
    name      = db.Column(db.String(20),  nullable=False)
    email     = db.Column(db.String(20),  nullable=False)
    phone_num = db.Column(db.String(12),  nullable=False)
    mess      = db.Column(db.String(80),  nullable=False)
    date      = db.Column(db.String(20),  nullable=False)

########################## creating database  model for posts ##################

class Posts(db.Model):

    sno       = db.Column(db.Integer, primary_key=True)
    title      = db.Column(db.String(200),  nullable=False)
    tagline = db.Column(db.String(200),  nullable=False)
    slug     = db.Column(db.String(25),  nullable=False)
    content = db.Column(db.String(500),  nullable=False)
    date      = db.Column(db.String(12),  nullable=True)
    img_file = db.Column(db.String(12),  nullable=True) 
    
########################## Home page ################################

@app.route("/")
def home():
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts)/int(para['no_of_posts']))
    page = request.args.get('page')

    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    posts = posts[((page-1)*int(para['no_of_posts'])):((page-1)*int(para['no_of_posts']))+ (int(para['no_of_posts']))]
    if page==1:
        prev = "#"
        next = "/?page="+ str(page+1)
    elif page==last:
        prev = "/?page="+ str(page-1)
        next = "#"
    else:
        prev = "/?page="+ str(page-1)
        next = "/?page="+ str(page+1)
    return render_template("index.html", para = para , posts = posts, prev = prev, next = next)

############################ About page #############################

@app.route("/about")
def about():
    return render_template("about.html", para = para)

############################ Post page ##############################

@app.route("/post/<string:post_slug>",methods =['GET'])
def post(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template("post.html", para = para , post = post)

############################# DASHBORD page #########################

@app.route("/dashbord", methods = [ 'GET', 'POST' ])
def dashbord():
    if ("user" in session and session['user'] == para['admin_login']):
        posts = Posts.query.all()
        return render_template("dashbord.html", para=para,posts=posts)
    
    if (request.method == 'POST'):
        username =  request.form.get("uname")
        userpass =  request.form.get("pass")
        if (username==para['admin_login'] and userpass==para['admin_pass']):
            #set the session variable
            session['user'] = username
            posts = Posts.query.all()
            return render_template("dashbord.html",para = para, posts= posts)
    
    return render_template("login.html", para = para)

########################### DASHBORD END ############################

@app.route("/contact", methods = [ 'GET', 'POST' ])
def contact():
    if (request.method == 'POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contact(name=name, phone_num = phone, mess = message, date= datetime.now(),email = email )
        db.session.add(entry)
        db.session.commit()

    return render_template("contact.html", para = para)

########################### Edit and update posts ###########################

@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    if ("user" in session and session['user'] == para['admin_login']):
        if (request.method == 'POST'):
            box_title = request.form.get('title')
            tline = request.form.get('tline')
            slug= request.form.get('slug')
            content= request.form.get('content')
            img_file= request.form.get('img_file')
            date= datetime.now()
            
            if sno =='0':
                post = Posts(title = box_title, slug=slug, content=content, tagline=tline, img_file=img_file, date=date)
                db.session.add(post)
                db.session.commit()  
                
            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title = box_title
                post.tline = tline
                post.slug = slug
                post.content = content
                post.date = date
                db.session.commit()
                return redirect('/edit/' + sno)

        post = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html',para = para, post=post, sno=sno )

########################### upload file  ###########################

@app.route("/uploader", methods=['GET', 'POST'])
def uploader():
    if ("user" in session and session['user'] == para['admin_login']):
        if request.method=="POST":
            f = request.files["file1"]
            f.save(os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(f.filename)))

            return redirect('/dashbord')

########################### Delete posts ###########################

@app.route("/delete/<string:sno>", methods=['GET', 'POST'])
def delete(sno):
    if ("user" in session and session['user'] == para['admin_login']):
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()

        return redirect('/dashbord')

########################### Logout from deshboard ###########################

@app.route('/logout')
def logout():
    try:
        session.pop('user')
        return redirect('/dashbord')
    except(Exception):
        return redirect('/dashbord')

########################### main function ###########################

if __name__ == "__main__":
    app.run(debug=True)