"""Small deterministic procurement state store for Proof #1."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass


@dataclass(frozen=True)
class Supplier:
	id: str
	unit_price: int
	inventory: int


class ProcurementStore:
	def __init__(self) -> None:
		self.connection = sqlite3.connect(':memory:', check_same_thread=False)
		self.connection.row_factory = sqlite3.Row
		self.connection.executescript(
			'''
			CREATE TABLE products (sku TEXT PRIMARY KEY, name TEXT NOT NULL);
			CREATE TABLE suppliers (id TEXT PRIMARY KEY, name TEXT NOT NULL, unit_price INTEGER NOT NULL, inventory INTEGER NOT NULL);
			CREATE TABLE purchase_requests (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				sku TEXT NOT NULL,
				quantity INTEGER NOT NULL,
				supplier_id TEXT NOT NULL,
				status TEXT NOT NULL
			);
			'''
		)
		self.connection.execute('INSERT INTO products VALUES (?, ?)', ('SKU-1024', 'AgentLab workstation'))
		self.connection.executemany(
			'INSERT INTO suppliers VALUES (?, ?, ?, ?)',
			[
				('sup-low', 'Northstar Supply', 180, 60),
				('sup-high', 'Pioneer Supply', 220, 100),
				('sup-empty', 'Archive Supply', 120, 5),
			],
		)

	def suppliers_for(self, sku: str) -> list[Supplier]:
		if sku != 'SKU-1024':
			return []
		return [Supplier(**dict(row)) for row in self.connection.execute('SELECT id, unit_price, inventory FROM suppliers')]

	def create_purchase_request(self, sku: str, quantity: int, supplier_id: str) -> int:
		supplier = self.connection.execute(
			'SELECT id, inventory FROM suppliers WHERE id = ?', (supplier_id,)
		).fetchone()
		if sku != 'SKU-1024' or supplier is None or quantity <= 0 or supplier['inventory'] < quantity:
			raise ValueError('Invalid purchase request')
		cursor = self.connection.execute(
			'INSERT INTO purchase_requests (sku, quantity, supplier_id, status) VALUES (?, ?, ?, ?)',
			(sku, quantity, supplier_id, 'created'),
		)
		self.connection.commit()
		return int(cursor.lastrowid)

	def snapshot(self) -> dict:
		rows = self.connection.execute(
			'SELECT sku, quantity, supplier_id, status FROM purchase_requests ORDER BY id'
		).fetchall()
		return {'purchase_requests': [dict(row) for row in rows]}
