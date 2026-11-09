import sqlite3
from contextlib import contextmanager
from decimal import Decimal
from pathlib import Path

import psycopg
from psycopg.rows import dict_row


class CatalogRepository:
    placeholder = '?'

    def ping(self):
        with self._connect() as connection:
            connection.execute('SELECT 1').fetchone()

    def list_boxes(self, active_filter=True):
        query = '''
            SELECT id, nombre, imagen_url, descripcion, precio, activa
            FROM cases_caja
        '''
        params = []
        if active_filter is not None:
            query += f' WHERE activa = {self.placeholder}'
            params.append(active_filter)
        query += ' ORDER BY nombre'
        with self._connect() as connection:
            boxes = [self._box_from_row(row) for row in connection.execute(query, params).fetchall()]
            self._attach_items(connection, boxes)
            return boxes

    def get_box(self, box_id):
        with self._connect() as connection:
            row = connection.execute(
                f'''
                SELECT id, nombre, imagen_url, descripcion, precio, activa
                FROM cases_caja
                WHERE id = {self.placeholder}
                ''',
                [box_id],
            ).fetchone()
            if row is None:
                return None
            box = self._box_from_row(row)
            self._attach_items(connection, [box])
            return box

    def _attach_items(self, connection, boxes):
        for box in boxes:
            box['items'] = []
        if not boxes:
            return
        boxes_by_id = {box['id']: box for box in boxes}
        placeholders = ','.join(self.placeholder for _ in boxes)
        rows = connection.execute(
            f'''
            SELECT
                ci.caja_id,
                ci.probabilidad,
                i.id,
                i.nombre,
                i.imagen_url,
                i.rareza,
                i.valor_estimado
            FROM cases_cajaitem ci
            JOIN cases_item i ON i.id = ci.item_id
            WHERE ci.caja_id IN ({placeholders})
            ORDER BY ci.caja_id, i.nombre
            ''',
            list(boxes_by_id.keys()),
        ).fetchall()
        for row in rows:
            boxes_by_id[row['caja_id']]['items'].append({
                'item': {
                    'id': row['id'],
                    'nombre': row['nombre'],
                    'imagen_url': row['imagen_url'] or '',
                    'rareza': row['rareza'],
                    'valor_estimado': _decimal_string(row['valor_estimado']),
                },
                'probabilidad': _decimal_string(row['probabilidad']),
            })

    def _box_from_row(self, row):
        return {
            'id': row['id'],
            'nombre': row['nombre'],
            'imagen_url': row['imagen_url'] or '',
            'descripcion': row['descripcion'] or '',
            'precio': _decimal_string(row['precio']),
            'activa': bool(row['activa']),
        }


class SQLiteCatalogRepository(CatalogRepository):
    def __init__(self, db_path):
        self.db_path = Path(db_path)

    @contextmanager
    def _connect(self):
        uri = f'file:{self.db_path.as_posix()}?mode=ro'
        connection = sqlite3.connect(uri, uri=True, timeout=5)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
        finally:
            connection.close()


class PostgresCatalogRepository(CatalogRepository):
    placeholder = '%s'

    def __init__(self, **conninfo):
        self.conninfo = conninfo

    @contextmanager
    def _connect(self):
        connection = psycopg.connect(
            **self.conninfo,
            connect_timeout=5,
            options='-c default_transaction_read_only=on',
            row_factory=dict_row,
        )
        try:
            yield connection
        finally:
            connection.close()


def _decimal_string(value):
    return f'{Decimal(str(value)):.2f}'
