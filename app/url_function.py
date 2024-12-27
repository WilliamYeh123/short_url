from urllib.parse import urlparse
from decimal import Decimal
import random
import string
import logging

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
    """
    if len(url) > 2048:
        return False, "URL too long (should be under 2048)"
    if not url:
        return False, "URL required"
    if not isinstance(url, str):
        return False, "URL must be a string"

    url_parse = urlparse(url)
    if not all([url_parse.scheme, url_parse.netloc]):
        return False, "Invalid URL format, must include scheme (http:// or https://) and domain"

    return True, "Success creating short URL"
