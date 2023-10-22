from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('guide', __name__)


@bp.route('/guide')
def index():
    db = get_db()
    guides = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM guide p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('guide/index.html', posts=guides)

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
                'INSERT INTO guide (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('guide.index'))

    return render_template('guide/create.html')


def get_guide(id, check_author=True):
    guide = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM guide p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if guide is None:
        abort(404, f"Guide id {id} doesn't exist.")

    if check_author and guide['author_id'] != g.user['id']:
        abort(403)

    return guide


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    guide = get_guide(id)

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
                'UPDATE guide SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('guide.index'))

    return render_template('guide/update.html', post=guide)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_guide(id)
    db = get_db()
    db.execute('DELETE FROM guide WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('guide.index'))