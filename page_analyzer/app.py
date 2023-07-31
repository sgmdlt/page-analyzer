import os

import requests
from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from page_analyzer import db
from page_analyzer import html
from page_analyzer import urls


load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')


@app.route('/')
def index():
    return render_template('index.html')


@app.get('/urls')
def urls_show():
    conn = db.get_db(app)
    data = db.get_urls_with_checks(conn)
    db.commit(conn)
    db.close(conn)

    return render_template(
        'urls/index.html',
        data=data,
    )


@app.post('/urls')
def post_url():
    url = request.form['url']
    errors = urls.validate(url)
    if errors:
        for error in errors:
            flash(error, 'danger')
        return render_template('index.html', url_name=url), 422

    conn = db.get_db(app)
    normalized_url = urls.normalize(url)
    existed_url = db.get_url_by_name(conn, normalized_url)
    db.commit(conn)

    if existed_url:
        id = existed_url.id
        flash('Страница уже существует', 'info')
    else:
        id = db.insert_url(conn, normalized_url)
        db.commit(conn)
        flash('Страница успешно добавлена', 'success')
    db.close(conn)

    return redirect(url_for('url_show', id=id))


@app.route('/urls/<int:id>')
def url_show(id):
    conn = db.get_db(app)
    url = db.get_url_by_id(conn, id)
    db.commit(conn)
    if url is None:
        abort(404)

    checks = db.get_url_checks(conn, id)
    db.commit(conn)

    db.close(conn)

    return render_template(
        'urls/url.html',
        url=url,
        checks=checks,
    )


@app.route('/urls/<int:id>/checks', methods=['POST'])
def url_checks(id):
    conn = db.get_db(app)
    url = db.get_url_by_id(conn, id)
    db.commit(conn)

    try:
        resp = requests.get(url.name)
        resp.raise_for_status()
    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('url_show', id=id))

    page_data = html.get_page_data(resp)
    db.insert_page_check(conn, id, page_data)
    db.commit(conn)
    flash('Страница успешно проверена', 'success')
    db.close(conn)

    return redirect(url_for('url_show', id=id))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500
