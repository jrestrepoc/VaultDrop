"""Adaptador del catálogo de caracteres publicado por HanZi Mentor."""
import http.client
import json
import random
from urllib.request import urlopen

from apps.core.domain import ExternalServiceError


def reto_pinyin(url):
    try:
        if not url:
            raise ValueError('HANZI_CATALOGO_URL')
        with urlopen(url, timeout=2) as response:
            rows = json.loads(response.read(64 * 1024))['caracteres']
        characters = {}
        for row in rows:
            hanzi, pinyin = row['hanzi'], row['pinyin']
            if isinstance(hanzi, str) and isinstance(pinyin, str) and hanzi.strip() and pinyin.strip():
                characters.setdefault(pinyin.strip(), hanzi.strip())
        options = random.sample(list(characters), 4)
    except (OSError, http.client.HTTPException, ValueError, KeyError, TypeError) as error:
        raise ExternalServiceError('HanZi Mentor') from error
    answer = random.randrange(len(options))
    return {'hanzi': characters[options[answer]], 'opciones': options, 'respuesta': answer}
