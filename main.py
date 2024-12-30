from app.url_function import check_url_validation, generate_short_url
from flask import Flask, request, redirect, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta
from config.config import BaseConfig
from deploy.init_db import init_db
import sqlite3

app = Flask(__name__)

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["60 per minute"]
)

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        "error": "Rate limit exceeded",
        "message": "Too many requests. Please try again later."
    }), 429

@app.route('/url/create', methods=['POST'])
@limiter.limit("60 per minute")
def create_url():
    """
    API 1: Create Short URL
    method: POST
    ------------------------------
    input  : {original_url    str}
    output : {
        original_url        str,
        short_url           str,
        reason              str,
        success             bool,
        expiration_date     timestamp
    }
    """
    try:
        response_data = {}
        data = request.json
        if not isinstance(data, dict):
            response_data['success'] = False
            response_data['reason'] = "Bad Request: Request body must be a JSON object"
            return jsonify(response_data), 400

        original_url = data.get('original_url','')
        token_len = data.get('length',20)
        expire = data.get('expire',30)

        # check if original_url is in valid format
        status, message, code = check_url_validation(original_url)
        response_data['success'] = status
        response_data['reason'] = message
        if not status:
            return jsonify(response_data), code

        # define create time and expire time
        create_at = datetime.now()
        expire_at = create_at + timedelta(days=expire)
        create_at = create_at.timestamp()
        expire_at = expire_at.timestamp()

        # save short url to db
        conn = sqlite3.connect(BaseConfig.SQLITE_PATH)
        c = conn.cursor()
        try:
            while True:
                # Check if short_url already exists, if not then save in db
                short = generate_short_url(token_len)
                existing = c.execute('SELECT short FROM urls WHERE short = ?', (short,)).fetchone()

                if not existing:
                    c.execute(
                        '''
                            INSERT INTO urls (url, short, create_at, expire)
                            VALUES (?, ?, ?, ?)
                        ''', (original_url, short, create_at, expire_at))
                    conn.commit()
                    break
        finally:
            conn.close()

        shortened_url = f"{request.host_url}{short}"
        response_data['original_url'] = original_url
        response_data['short_url'] = shortened_url
        response_data['expiration_date'] = expire_at

        return jsonify(response_data), 200

    except Exception as e:
        response_data['success'] = False
        response_data['reason'] = str(e) if app.debug else None
        return jsonify(response_data), 500

@app.route('/<short_url>', methods=['GET'])
@limiter.limit("60 per minute")
def redirect_url(short_url):
    """
    API 2: Redirect Using Short URL
    method: GET
    """
    conn = sqlite3.connect(BaseConfig.SQLITE_PATH)
    c = conn.cursor()
    # Get original URL from sqlite
    result = c.execute('''
        SELECT url, expire
        FROM urls
        WHERE short = ?
    ''', (short_url,)).fetchone()
    conn.close()

    # url not found error
    if not result:
        return jsonify({
            'error': 'URL not found',
            'message':'Short URL not found in database.'
            }), 404

    original_url, expire_str = result

    # Check if URL has expired
    if expire_str < datetime.now().timestamp():
        expired_date = datetime.fromtimestamp(expire_str)
        return jsonify({
            'error': 'URL has expired',
            'message': f"URL has expired since {expired_date}"
            }), 410

    return redirect(original_url)

init_db()
if __name__ == '__main__':
    app.run(host=BaseConfig.HOST, port=BaseConfig.PORT)