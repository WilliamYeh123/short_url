from app.url_function import check_url_validation, generate_short_url
from flask import Flask, request, redirect, jsonify
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta
from config.config import BaseConfig
from deploy.init_db import init_db
from app import create_app
import sqlite3
import logging

logger = logging.getLogger(__name__)

app = create_app()

@app.route('/url/create', methods=['POST'])
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
        data = request.json
        original_url = data.get('original_url','')
        response_data = {
            'original_url':original_url,
        }

        # check if original_url is in valid format
        status, message = check_url_validation(original_url)
        response_data['success'] = status
        response_data['reason'] = message
        if not status:
            return jsonify(response_data), 400

        # define create time and expire time
        create_at = datetime.now()
        expire_at = create_at + timedelta(days=30)
        create_at = create_at.timestamp()
        expire_at = expire_at.timestamp()

        # save short url to db
        conn = sqlite3.connect(BaseConfig.SQLITE_PATH)
        c = conn.cursor()
        try:
            while True:
                short = generate_short_url()
                # Check if short_url already exists, if not then save in db
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
        response_data['short_url'] = shortened_url
        response_data['expiration_date'] = expire_at

        return jsonify(response_data), 200

    except Exception as e:
        # Log the error here if you have logging configured
        response_data['success'] = False
        response_data['reason'] = str(e) if app.debug else None
        return jsonify(response_data), 500

@app.route('/<short_url>', methods=['GET'])
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
        return jsonify({'error': 'URL not found'}), 404

    original_url, expire_str = result

    # Check if URL has expired
    if expire_str < datetime.now().timestamp():
        return jsonify({
            'error': 'URL has expired',
            'expired_at': expire_str
        }), 410

    return redirect(original_url)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)