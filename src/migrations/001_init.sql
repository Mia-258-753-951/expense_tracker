

CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER NOT NULL
);

-- Insertamos la versión solo si no existe ya (para evitar duplicados)
INSERT INTO schema_version (version)
SELECT 1 WHERE NOT EXISTS (SELECT 1 FROM schema_version); --en lugar de hacer VALUES(1) le decimos al insert que tome los datos de una consulta
                                                        -- se evalúa el SELECT entre paréntesis, si la tabla está vacía se cumple NOT EXISTS y se insertará el 1 
                                                        -- si la tabla está vacía (el select entre paréntesis devolverá algo si la tabla no está vacía-no evalúa solo si hay un 1) 
CREATE TABLE IF NOT EXISTS expenses (                   -- el NOT EXISTS sera FALSE y no se insertará el 1 en la tabla.    
    id TEXT PRIMARY KEY,
    date TEXT NOT NULL,
    amount INTEGER NOT NULL,
    category TEXT NOT NULL,
    wallet TEXT NOT NULL,
    note TEXT,
    currency TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT
    );

CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date);
CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category);
CREATE INDEX IF NOT EXISTS idx_expenses_wallet ON expenses(wallet);

