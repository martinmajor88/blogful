import mistune
from werkzeug.security import generate_password_hash
from flask import render_template
from flask import request, redirect, url_for
from getpass import getpass

from blog import app
from .database import session
from .models import Post
from flask import flash
from flask.ext.login import login_user
from flask.ext.login import current_user
from werkzeug.security import check_password_hash
from .models import User
from flask.ext.login import login_required
from flask.ext.login import logout_user


@app.route("/")
@app.route("/page/<int:page>")
def posts(page=1, paginate_by=10):
    page_index = page - 1

    count = session.query(Post).count()

    start = page_index * paginate_by
    end = start + paginate_by

    total_pages = (count - 1) / paginate_by + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0

    posts = session.query(Post)
    posts = posts.order_by(Post.datetime.desc())
    posts = posts[start:end]

    for post in posts:
        post.markdown_content = mistune.markdown(post.content)

    return render_template("posts.html",
                           posts=posts,
                           has_next=has_next,
                           has_prev=has_prev,
                           page=page,
                           total_pages=total_pages
    )

@app.route("/post/<int:id>")
def view_post(id):

    post = session.query(Post).get(id)
    post.markdown_content = mistune.markdown(post.content)
    view_post = post

    return render_template("post.html",
                           post=post
    )

@app.route("/post/<int:id>/edit")
@login_required
def edit_post(id):

    post = session.query(Post).get(id)

    return render_template("edit.html",
                           post=post
    )

@app.route("/post/<int:id>/edit", methods=["POST"])
@login_required
def add_edit_post(id=1):

    post = session.query(Post).get(id)

    post.title = request.form["title"]
    post.content = request.form["content"]

    session.commit()
    return redirect(url_for("posts"))

@app.route("/post/add", methods=["GET"])
@login_required
def add_post_get():
    return render_template("add_post.html")

@app.route("/post/add", methods=["POST"])
@login_required
def add_post_post():
    post = Post(
        title=request.form["title"],
        content=request.form["content"],
        author=current_user
    )
    session.add(post)
    session.commit()
    return redirect(url_for("posts"))

@app.route("/post/<int:id>/delete", methods=["Get"])
@login_required
def confirm_delete(id):
    post = session.query(Post).get(id)

    return render_template("confirm_delete.html",
                           post=post
    )

@app.route("/post/<int:id>/delete", methods=["POST"])
@login_required
def delete_post(id):
    post = session.query(Post).get(id)

    session.delete(post)
    session.commit()

    return redirect(url_for("posts"))

@app.route("/login", methods=["GET"])
def login_get():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_post():
    email = request.form["email"]
    password = request.form["password"]
    user = session.query(User).filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        flash("Incorrect username or password", "danger")
        return redirect(url_for("login_get"))

    login_user(user)
    return redirect(request.args.get('next') or url_for("posts"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login_get"))

@app.route("/newaccount", methods=["GET"])
def new_user_get():
    return render_template("newaccount.html")

@app.route("/newaccount", methods=["POST"])
def adduser():
    name = request.form["name"]
    email = request.form["email"]
    if session.query(User).filter_by(email=email).first():
        print "User with that email address already exists"
        return

    password = request.form["password"]
    password_2 = request.form["password"]
    while not (password and password_2) or password != password_2:
        password = getpass()
        password_2 = getpass()
    user = User(name=name, email=email,
                password=generate_password_hash(password))
    session.add(user)
    session.commit()
    return redirect(url_for("posts"))
