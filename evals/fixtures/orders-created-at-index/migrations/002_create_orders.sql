-- created_at is UTC text, 'YYYY-MM-DD HH:MM:SS'.
CREATE TABLE orders (
  id INTEGER PRIMARY KEY,
  customer_id INTEGER NOT NULL REFERENCES customers(id),
  created_at TEXT NOT NULL,
  amount REAL NOT NULL,
  status TEXT NOT NULL,
  channel TEXT NOT NULL,
  note TEXT NOT NULL DEFAULT ''
);
