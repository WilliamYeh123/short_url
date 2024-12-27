from urllib.parse import urlparse
from decimal import Decimal
import random
import string
import logging
import re

logger = logging.getLogger(__name__)

def generate_short_url(length = 20):
    """
    create letter and int combined token
    init len: 20
    """
    characters = string.ascii_letters + string.digits
    token = ''.join(random.choices(characters, k=length))

    return token

def check_url_validation(url):
    """
    total length < 2048
    url required
    url must be string
    must be http or https
    must include http and domain
    """
    if len(url) > 2048:
        return False, "URL too long (should be under 2048)"
    if not url:
        return False, "URL required"
    if not isinstance(url, str):
        return False, "URL must be a string"

    try:
        url_parse = urlparse(url)
        if not all([url_parse.scheme, url_parse.netloc]):
            return False, "Invalid URL format, must include scheme (http:// or https://) and domain"
        if url_parse.scheme not in ['http', 'https']:
            return False, "URL must use http or https protocol"
        domain = url_parse.netloc
        if not re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', domain):
            return False, "Invalid domain format"
    except Exception as e:
        return False, "Invalid URL format"

    return True, "Success creating short URL"
