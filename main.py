from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:0812@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title,body, user):   
        self.title = title
        self.body = body     
        self.user = user

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    username =  db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))    
    blogs = db.relationship('Blog', backref='user')

    def __init__(self, username,password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['signup', 'login','blog','index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/login')

@app.route('/', methods=['POST','GET'])
def index():

    users= User.query.all()
    username = request.args.get('user_name')
    return render_template('index.html', users=users)

    if request.args.get('user', ''):
        user_id = request.args.get('user')
        users = User.query.get(user_id)
        blogs = Blog.query.filter_by(user=users).all()
        return render_template('singleuser.html',blogs=blogs)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        username=request.form['username']
        password_error=''
        password1 = request.form['pwd1']
        password2 = request.form['pwd2']
        if password1 != password2:
            password_error = "Passwords must match."
            return render_template('signup.html',password_error=password_error)
            

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user and not password_error:
            new_user = User(username, password1)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')

        else:
            flash('Username already exists.', 'error')
    
    return render_template('signup.html')
      
@app.route('/blog',methods = ['POST', 'GET'])
def blog():

    blogs = Blog.query.all()
    blog_id= request.args.get('id')

    if request.args.get('id', ''):

        blog = Blog.query.get(blog_id)
        return render_template('single_blog.html'
        ,blog=blog)

    
    if request.args.get('user', ''):
        user_id = request.args.get('user')
        users = User.query.get(user_id)
        blogs = Blog.query.filter_by(user=users).all()
        return render_template('singleuser.html',blogs=blogs)

    else:
        return render_template('blog.html', 
        title="Build a Blog!", blogs=blogs )



@app.route('/newpost',methods = ['POST', 'GET'])
def newpost():
    user = User.query.filter_by(username=session['username']).first()
    if request.method == 'POST':

        title = request.form['title']
        body = request.form['body']
        new_blog = Blog(title,body,user)
        db.session.add(new_blog)
        db.session.commit()
        blog = Blog.query.order_by('-Blog.id').first()
        return render_template('single_blog.html',blog=blog)

    else:
        return render_template('newpost.html',title="Add a Blog Post")



if __name__ == '__main__':
    app.run()
