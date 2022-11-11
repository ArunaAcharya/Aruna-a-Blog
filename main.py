from flask import Flask, request, render_template, redirect, url_for, flash,abort
from flask_gravatar import Gravatar
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user,LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, LoginForm, RegisterForm, CommentForm
from functools import wraps
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData
import os

meta= MetaData()
Base= declarative_base()
db = SQLAlchemy()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL","sqlite:/// blog.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
app.config['SECRET_KEY'] = os.environ.get("osuwnue8247692r2u1hy32763")
ckeditor = CKEditor(app)
Bootstrap(app)

login_manager= LoginManager()
login_manager.init_app(app)

gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False, base_url=None)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id !=1:
            return abort(403)
        else:
            return f(*args, **kwargs)
    return decorated_function

#
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable= True)
    password = db.Column(db.String(100), nullable= True)
    name = db.Column(db.String(100), nullable= True)
    posts = relationship("BlogPost", back_populates="author")
    comments= relationship("Comment", back_populates="comment_author")


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    comments= relationship("Comment", back_populates= "parent_post")

class Comment(db.Model):
    __tablename__= "comments"
    id= db.Column(db.Integer, primary_key= True)
    author_id= db.Column(db.Integer, db.ForeignKey("users.id"))
    comment_author= relationship("User", back_populates= "comments")
    post_id= db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    parent_post=relationship("BlogPost", back_populates= "comments")
    text = db.Column(db.String, nullable=False)

with app.app_context():
    db.create_all()

@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    form = CommentForm()
    comments= Comment.query.all()
    if form.validate_on_submit():
        # if not current_user.is_authenticated:
        #     flash("You need to register to comment.")
        #     return redirect(url_for('login'))
        new_comment= Comment(
            text=form.comment.data,
            comment_author= User(name= current_user.name),
            parent_post= requested_post
        )
        db.session.add(new_comment)
        db.session.commit()


    return render_template("post.html", post=requested_post, current_user=current_user, form=form, comments= comments )



@app.route('/login', methods= ['GET','POST'])
def login():
    form= LoginForm()
    if request.method=='POST':
        email= form.email.data
        password= form.Password.data
        user= User.query.filter_by(email= email).first()


        if not user:
            flash ("That email does not exist, please try again!")
            return redirect(url_for('login'))

        elif not check_password_hash(user.password, password):
            flash("password incorrect, please try again.")
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('get_all_posts'))

    return render_template("login.html", form= form,current_user= current_user)

@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    if request.method=='POST':
        if User.query.filter_by(email= request.form.get('email')).first():
            flash('you have already signed up with that email, login instead.')
            return redirect(url_for('login'))

        hash_password= generate_password_hash(
            request.form.get('password'),
            method="pbkdf2:sha256",
            salt_length=8
        )
        new_user=User(
            name=request.form['name'],
            email=request.form['email'],
            password= hash_password
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return render_template("index.html")
    return render_template("register.html", form= form,current_user= current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))

@app.route('/')
def get_all_posts():
    posts= BlogPost.query.all()
    return render_template("index.html", all_posts=posts,current_user= current_user)



@app.route('/new-post', methods=["GET", "POST"])
@admin_only
def new_post():
    form= CreatePostForm()
    if form.validate_on_submit():
        recent_post = BlogPost(
            title=request.form['title'],
            subtitle=request.form['subtitle'],
            date=date.today().strftime("%B %d %Y"),
            body=request.form.get('body'),
            author_id= User(id=current_user.id),
            author=User(name=current_user.name),
            img_url=request.form['img_url'],

        )
        db.session.add(recent_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form= form,current_user= current_user)

@app.route('/edit/<int:post_id>', methods= ["GET", "POST"])
@admin_only
def edit_post(post_id):
    post= BlogPost.query.get(post_id)
    edit_form= CreatePostForm(
        title= post.title,
        subtitle= post.subtitle,
        img_url= post.img_url,
        author=current_user.name,
        body= post.body
    )
    if edit_form.validate_on_submit():
        post.title= edit_form.title.data
        post.subtitle= edit_form.subtitle.data
        post.img_url= edit_form.img_url.data
        post.body= edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id= post.id))

    return render_template("make-post.html",form= edit_form, id_edit= True,current_user= current_user )

@app.route('/delete')
@login_required
def delete():
    post_id= request.args.get('post_id')
    post_to_delete= BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return render_template("index.html",current_user= current_user)

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True)