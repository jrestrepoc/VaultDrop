import gettext
import os
import sqlite3
from pathlib import Path

import psycopg
from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

from errors import BadRequestError, CatalogError, DataAccessError, NotFoundError
from repository import PostgresCatalogRepository, SQLiteCatalogRepository


LOCALE_DIR = Path(__file__).resolve().parent / 'locale'


def _traducir(mensaje):
    idioma = request.cookies.get('django_language') or request.accept_languages.best_match(['es', 'en'])
    if idioma != 'en':
        return mensaje
    return gettext.translation('messages', LOCALE_DIR, ['en'], fallback=True).gettext(mensaje)


def _default_repository():
    if os.environ.get('POSTGRES_HOST'):
        return PostgresCatalogRepository(
            host=os.environ['POSTGRES_HOST'],
            dbname=os.environ['POSTGRES_DB'],
            user=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD'],
        )
    return SQLiteCatalogRepository(os.environ.get('CATALOG_DB_PATH', '/data/db.sqlite3'))


def create_app(repository=None):
    app = Flask(__name__)
    app.config['CATALOG_REPOSITORY'] = repository or _default_repository()

    @app.errorhandler(CatalogError)
    def handle_catalog_error(error):
        return jsonify({'error': {'code': error.code, 'message': _traducir(error.message)}}), error.status_code

    @app.errorhandler(sqlite3.Error)
    @app.errorhandler(psycopg.Error)
    def handle_data_error(error):
        app.logger.exception('Catalog data access failed: %s', error)
        data_error = DataAccessError()
        return jsonify({'error': {'code': data_error.code, 'message': _traducir(data_error.message)}}), data_error.status_code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        if isinstance(error, HTTPException):
            return error
        app.logger.exception('Unexpected catalog service failure: %s', error)
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': _traducir('No se pudo completar la consulta del catalogo.'),
            }
        }), 500

    @app.get('/health')
    def health():
        app.config['CATALOG_REPOSITORY'].ping()
        return jsonify({'status': 'ok', 'service': 'catalog'})

    @app.get('/api/v2/catalogo/')
    def list_catalog():
        active_filter = _parse_active_filter(request.args.get('activa', 'true'))
        return jsonify(app.config['CATALOG_REPOSITORY'].list_boxes(active_filter))

    @app.get('/api/v2/catalogo/<case_id>/')
    def get_catalog_detail(case_id):
        parsed_case_id = _parse_positive_int(case_id)
        box = app.config['CATALOG_REPOSITORY'].get_box(parsed_case_id)
        if box is None:
            raise NotFoundError('Caja no encontrada.')
        return jsonify(box)

    return app


def _parse_positive_int(value):
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise BadRequestError('El parametro id debe ser un entero positivo.') from exc
    if parsed <= 0:
        raise BadRequestError('El parametro id debe ser un entero positivo.')
    return parsed


def _parse_active_filter(value):
    normalized = (value or '').strip().lower()
    if normalized in ('true', '1', 'si', 'yes'):
        return True
    if normalized in ('false', '0', 'no'):
        return False
    if normalized in ('all', 'todos'):
        return None
    raise BadRequestError('El parametro activa debe ser true, false o all.')


app = create_app()
