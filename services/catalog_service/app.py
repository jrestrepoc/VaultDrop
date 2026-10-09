import os
import sqlite3

from flask import Flask, jsonify, request

from errors import BadRequestError, CatalogError, DataAccessError, NotFoundError
from repository import SQLiteCatalogRepository


def create_app(repository=None):
    app = Flask(__name__)
    db_path = os.environ.get('CATALOG_DB_PATH', '/data/db.sqlite3')
    app.config['CATALOG_REPOSITORY'] = repository or SQLiteCatalogRepository(db_path)

    @app.errorhandler(CatalogError)
    def handle_catalog_error(error):
        return jsonify({'error': {'code': error.code, 'message': error.message}}), error.status_code

    @app.errorhandler(sqlite3.Error)
    def handle_sqlite_error(error):
        app.logger.exception('Catalog data access failed: %s', error)
        data_error = DataAccessError()
        return jsonify({'error': {'code': data_error.code, 'message': data_error.message}}), data_error.status_code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception('Unexpected catalog service failure: %s', error)
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'No se pudo completar la consulta del catalogo.',
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
        parsed_case_id = _parse_positive_int(case_id, 'id')
        box = app.config['CATALOG_REPOSITORY'].get_box(parsed_case_id)
        if box is None:
            raise NotFoundError('Caja no encontrada.')
        return jsonify(box)

    return app


def _parse_positive_int(value, field):
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise BadRequestError(f'El parametro {field} debe ser un entero positivo.') from exc
    if parsed <= 0:
        raise BadRequestError(f'El parametro {field} debe ser un entero positivo.')
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
