from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from app.auth import login_required
from app.db import get_db

import bleach

bp = Blueprint('account', __name__)


@bp.route('/')
@login_required
def index():
    return redirect(url_for('account.profile'))


@bp.route('/bio', methods=("GET", "POST"))
@login_required
def bio():
    if request.method == "POST":
        bio = request.form["bio"]
        error = None

        if not bio:
            error = "Bio is required."

        if error is None:
            db = get_db()

            existing_record = db.execute(
                'SELECT bio FROM users WHERE id = ?',
                (g.user['id'],)
            ).fetchone()

            if existing_record:
                db.execute(
                    'UPDATE users SET bio = ? WHERE id = ?',
                    (bio, g.user['id'])
                )
            else:
                db.execute(
                    'INSERT INTO users (id, bio) VALUES (?, ?)',
                    (g.user['id'], bio)
                )

            db.commit()
            return redirect(url_for('account.profile'))
        else:
            flash(error)

    return render_template('account/bio.html')


@bp.route('/blogs')
@login_required
def blogs():
    db = get_db()
    posts = [dict(row) for row in db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM posts p JOIN users u ON p.author_id = u.id WHERE u.id = ?'
        ' ORDER BY created DESC',
        (g.user['id'],)
    ).fetchall()]

    for post in posts:
        post['body'] = bleach.clean(post['body'], tags=['p', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'br', 'span', 'ol', 'ul', 'li'], attributes={'*': ['class']})

    return render_template('account/blogs.html', posts=posts)


@bp.route('/btc', methods=("GET", "POST"))
@login_required
def btc():
    if request.method == "POST":
        address = request.form["address"]
        error = None

        if not address:
            error = "Address is required."

        if error is None:
            db = get_db()

            existing_record = db.execute(
                'SELECT * FROM crypto WHERE user_id = ?',
                (g.user['id'],)
            ).fetchone()

            if existing_record:
                db.execute(
                    'UPDATE crypto SET btc = ? WHERE user_id = ?',
                    (address, g.user['id'])
                )
                db.commit()
            else:
                db.execute(
                    'INSERT INTO crypto (user_id, btc) VALUES (?, ?)',
                    (g.user['id'], address)
                )
                db.commit()

            return redirect(url_for('account.monetization'))
        else:
            flash(error)

    return render_template('account/btc.html')


@bp.route('/monetization')
@login_required
def monetization():
    db = get_db()

    wallet_data = db.execute(
        'SELECT btc, xmr FROM crypto WHERE user_id = ?', (g.user['id'],)
    ).fetchone()

    wallets = dict(wallet_data) if wallet_data else {}

    return render_template('account/monetization.html', wallets=wallets)


@bp.route('/profile')
@login_required
def profile():
    db = get_db()
    profile = db.execute(
        "SELECT username, bio, followers FROM users WHERE id = ?",
        (g.user['id'],)
    ).fetchone()
    return render_template('account/profile.html', profile=profile)


@bp.route('/xmr', methods=("GET", "POST"))
@login_required
def xmr():
    if request.method == "POST":
        address = request.form["address"]
        error = None

        if not address:
            error = "Address is required."

        if error is None:
            db = get_db()

            existing_record = db.execute(
                'SELECT * FROM crypto WHERE user_id = ?',
                (g.user['id'],)
            ).fetchone()

            if existing_record:
                db.execute(
                    'UPDATE crypto SET xmr = ? WHERE user_id = ?',
                    (address, g.user['id'])
                )
                db.commit()
            else:
                db.execute(
                    'INSERT INTO crypto (user_id, xmr) VALUES (?, ?)',
                    (g.user['id'], address)
                )
                db.commit()
            try:
                # Add print statements for debugging
                print("SQL Query:", 'UPDATE crypto SET xmr = ? WHERE user_id = ?', (address, g.user['id']))
                print("SQL Query:", 'INSERT INTO crypto (user_id, xmr) VALUES (?, ?)', (g.user['id'], address))

            except Exception as e:
                print("Error:", str(e))
                flash("An error occurred.")

            return redirect(url_for('account.monetization'))
        else:
            flash(error)

    return render_template('account/xmr.html')

