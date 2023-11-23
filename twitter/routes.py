from twitter import app
from flask import render_template, url_for, redirect, flash, request
from flask_login import login_required, login_user, current_user
from twitter.models import load_user
from twitter.forms import FormLogin, FormCreateNewAccount, FormCreateNewPost
from twitter import bcrypt
from twitter.models import User, Posts, Like
from twitter import database
from datetime import datetime


import os
from werkzeug.utils import secure_filename


# @app.route('/home')
@app.route('/', methods=['POST', 'GET'])
def homepage():
    _formLogin = FormLogin()
    if _formLogin.validate_on_submit():
        userToLogin = User.query.filter_by(email=_formLogin.email.data).first()
        if userToLogin and bcrypt.check_password_hash(userToLogin.password, _formLogin.password.data):
            login_user(userToLogin)
            return redirect(url_for("profile", user_id=userToLogin.id))

    return render_template('login.html', textinho='TOP', form=_formLogin)


@app.route('/new', methods=['POST', 'GET'])
def createAccount():
    _formCreateNewAccount = FormCreateNewAccount()

    if _formCreateNewAccount.validate_on_submit():
        password = _formCreateNewAccount.password.data
        password_cr = bcrypt.generate_password_hash(password)
        # print(password)
        # print(password_cr)

        newUser = User(
            username=_formCreateNewAccount.usarname.data,
            email=_formCreateNewAccount.email.data,
            password=password_cr
        )

        database.session.add(newUser)
        database.session.commit()

        login_user(newUser, remember=True)
        return redirect(url_for('profile', user_id=newUser.id))

    return render_template('new.html', form=_formCreateNewAccount)


@app.route('/perry')
def perry():
    return render_template('perry.html')


@app.route('/teste')
def teste():
    return render_template('teste.html')


@app.route('/profile/<user_id>', methods=['POST', 'GET'])
@login_required
def profile(user_id):
    if int(user_id) == int(current_user.id):
        _formCreateNewPost = FormCreateNewPost()

        if _formCreateNewPost.validate_on_submit():
            photo_file = _formCreateNewPost.photo.data
            photo_name = secure_filename(photo_file.filename)

            photo_path = f'{os.path.abspath(os.path.dirname(__file__))}/static/assets/{photo_name}'
            photo_file.save(photo_path)

            _postText = _formCreateNewPost.text.data

            new_post = Posts(post_text=_postText, post_img=photo_name, user_id=int(current_user.id))
            database.session.add(new_post)
            database.session.commit()

        return render_template('profile.html', user=current_user, form=_formCreateNewPost)

    else:
        _user = User.query.get(int(user_id))
        reposts = _user.reposts
        return render_template('profile.html', user=_user, reposts=reposts, form=None)


@app.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = Posts.query.get(post_id)
    if post is None:
        flash('Post não encontrado.')
        return redirect(url_for('login'))

    existing_like = Like.query.filter_by(user_id=current_user.id, post_id=post.id).first()

    if existing_like:
        # Se o usuário já deu um like, remova o like existente
        database.session.delete(existing_like)
        post.likes -= 1  # Decrementa o número de likes no post
    else:
        # Se o usuário ainda não deu um like, adicione o like
        like = Like(user_id=current_user.id, post_id=post.id)
        database.session.add(like)
        post.likes += 1  # Incrementa o número de likes no post

    database.session.commit()
    return redirect(request.referrer)

@app.route('/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Posts.query.get(post_id)
    if post is None:
        flash('Post não encontrado.')
        return redirect(url_for('login'))

    database.session.delete(post)
    database.session.commit()
    return redirect(url_for('profile', user_id=current_user.id))


@app.route('/post/<int:post_id>/repost', methods=['POST'])
@login_required
def repost(post_id):
    post = Posts.query.get_or_404(post_id)

    # Create a new post as a repost
    repost_post = Posts(
        post_text=f"{post.post_text}",
        post_img=post.post_img,
        creation_date= datetime.now(),
        reposted=True,
        user_id = current_user.id,
        original_posted_by_id=post.user.username,
        original_posted_date=post.creation_date
    )

    # Add the repost to the database
    database.session.add(repost_post)
    database.session.commit()

    return redirect(url_for('profile', user_id=current_user.id))




@app.route('/timeline')
@login_required
def timeline():
    posts = Posts.query.all()
    return render_template('timeline.html', posts=posts)