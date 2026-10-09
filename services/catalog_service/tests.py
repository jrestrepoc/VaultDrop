import os
import sqlite3
import tempfile
import unittest

from app import create_app
from repository import SQLiteCatalogRepository


class BrokenRepository:
    def ping(self):
        raise RuntimeError('database unavailable')

    def list_boxes(self, active_filter=True):
        raise RuntimeError('database unavailable')

    def get_box(self, box_id):
        raise RuntimeError('database unavailable')


class CatalogServiceTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tempdir.name, 'db.sqlite3')
        self._create_catalog_db()
        app = create_app(SQLiteCatalogRepository(self.db_path))
        app.config['TESTING'] = True
        self.client = app.test_client()

    def tearDown(self):
        self.tempdir.cleanup()

    def test_health_returns_json(self):
        response = self.client.get('/health')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {'service': 'catalog', 'status': 'ok'})

    def test_list_catalog_returns_active_boxes(self):
        response = self.client.get('/api/v2/catalogo/')

        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['nombre'], 'Caja Activa')
        self.assertEqual(data[0]['precio'], '100.00')
        self.assertEqual(data[0]['items'][0]['item']['nombre'], 'Skin Azul')

    def test_detail_returns_box(self):
        response = self.client.get('/api/v2/catalogo/1/')

        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['items'][0]['probabilidad'], '100.00')

    def test_detail_not_found_uses_structured_error(self):
        response = self.client.get('/api/v2/catalogo/999/')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()['error']['code'], 'RESOURCE_NOT_FOUND')

    def test_invalid_id_returns_400(self):
        response = self.client.get('/api/v2/catalogo/abc/')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['error']['code'], 'BAD_REQUEST')

    def test_invalid_query_returns_400(self):
        response = self.client.get('/api/v2/catalogo/?activa=maybe')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['error']['code'], 'BAD_REQUEST')

    def test_internal_error_is_controlled(self):
        app = create_app(BrokenRepository())
        app.config['TESTING'] = True
        client = app.test_client()

        response = client.get('/api/v2/catalogo/')

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json()['error']['code'], 'INTERNAL_ERROR')

    def _create_catalog_db(self):
        connection = sqlite3.connect(self.db_path)
        connection.executescript(
            '''
            CREATE TABLE cases_caja (
                id integer primary key,
                nombre varchar(120) not null,
                imagen_url varchar(1000) not null default '',
                descripcion text not null default '',
                precio decimal not null,
                activa bool not null,
                created_at datetime not null
            );
            CREATE TABLE cases_item (
                id integer primary key,
                nombre varchar(120) not null,
                imagen_url varchar(1000) not null default '',
                rareza varchar(20) not null,
                valor_estimado decimal not null
            );
            CREATE TABLE cases_cajaitem (
                id integer primary key,
                probabilidad decimal not null,
                caja_id bigint not null,
                item_id bigint not null
            );
            '''
        )
        connection.execute(
            'INSERT INTO cases_caja VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)',
            [1, 'Caja Activa', '/static/caja.png', 'Catalogo publico', '100.00', 1],
        )
        connection.execute(
            'INSERT INTO cases_caja VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)',
            [2, 'Caja Inactiva', '', '', '200.00', 0],
        )
        connection.execute(
            'INSERT INTO cases_item VALUES (?, ?, ?, ?, ?)',
            [1, 'Skin Azul', '/static/skin.png', 'RARO', '50.00'],
        )
        connection.execute(
            'INSERT INTO cases_cajaitem VALUES (?, ?, ?, ?)',
            [1, '100.00', 1, 1],
        )
        connection.commit()
        connection.close()


if __name__ == '__main__':
    unittest.main()
