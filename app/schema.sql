-- Esquema del prototipo FlotaSegura (SQLite).
-- Es el contrato compartido entre todos los frentes: si alguien necesita
-- cambiar una tabla, se avisa al grupo antes de hacer el commit.

CREATE TABLE IF NOT EXISTS usuarios (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_usuario  TEXT NOT NULL UNIQUE,
    nombre_completo TEXT NOT NULL,
    hash_contrasena TEXT NOT NULL,
    rol             TEXT NOT NULL CHECK (rol IN ('conductor', 'jefe_flota'))
);

CREATE TABLE IF NOT EXISTS camiones (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    patente      TEXT NOT NULL UNIQUE,
    km_actual    INTEGER NOT NULL DEFAULT 0 CHECK (km_actual >= 0),
    estado       TEXT NOT NULL DEFAULT 'operativo'
                 CHECK (estado IN ('operativo', 'alerta_temprana', 'mantencion_vencida')),
    conductor_id INTEGER REFERENCES usuarios (id)
);

CREATE TABLE IF NOT EXISTS planes_mantencion (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    camion_id               INTEGER NOT NULL REFERENCES camiones (id),
    tipo                    TEXT NOT NULL,              -- aceite, frenos, neumaticos
    tipo_calculo            TEXT NOT NULL CHECK (tipo_calculo IN ('km', 'fecha')),
    -- Usados por CalculoPorKm
    intervalo_km            INTEGER,
    km_ultima_mantencion    INTEGER,
    umbral_aviso_km         INTEGER,
    -- Usados por CalculoPorFecha
    intervalo_dias          INTEGER,
    fecha_ultima_mantencion TEXT,                       -- formato AAAA-MM-DD
    umbral_aviso_dias       INTEGER
);

CREATE TABLE IF NOT EXISTS registros_kilometraje (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    camion_id      INTEGER NOT NULL REFERENCES camiones (id),
    conductor_id   INTEGER NOT NULL REFERENCES usuarios (id),
    kilometraje    INTEGER NOT NULL,
    fecha_registro TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS alertas (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    camion_id       INTEGER NOT NULL REFERENCES camiones (id),
    plan_id         INTEGER NOT NULL REFERENCES planes_mantencion (id),
    destinatario_id INTEGER NOT NULL REFERENCES usuarios (id),
    nivel           TEXT NOT NULL CHECK (nivel IN ('alerta_temprana', 'mantencion_vencida')),
    mensaje         TEXT NOT NULL,
    fecha           TEXT NOT NULL DEFAULT (datetime('now'))
);
