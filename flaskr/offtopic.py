from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('offtopic', __name__)


@bp.route('/offtopic')
def index():
    db = get_db()
    offtopicposts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM offtopicpost p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('offtopic/index.html', posts=offtopicposts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO offtopicpost (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('offtopic.index'))

    return render_template('offtopic/create.html')


def get_offtopicpost(id, check_author=True):
    offtopicpost = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM offtopicpost p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if offtopicpost is None:
        abort(404, f"Off-Topic Post id {id} doesn't exist.")

    if check_author and offtopicpost['author_id'] != g.user['id']:
        abort(403)

    return offtopicpost


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    offtopicpost = get_offtopicpost(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE offtopicpost SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('offtopic.index'))

    return render_template('offtopic/update.html', post=offtopicpost)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_offtopicpost(id)
    db = get_db()
    db.execute('DELETE FROM offtopicpost WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('offtopic.index'))