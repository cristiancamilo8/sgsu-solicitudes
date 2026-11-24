"""Conexión y esquema de la base de datos relacional (SQLite)."""
import sqlite3

ESQUEMA = """
CREATE TABLE IF NOT EXISTS usuario (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre        TEXT NOT NULL,
    correo        TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    rol           TEXT NOT NULL CHECK (rol IN ('ADMIN','ESTUDIANTE','FUNCIONARIO','SUPERVISOR')),
    activo        INTEGER NOT NULL DEFAULT 1,
    creado_en     TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS categoria (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      TEXT NOT NULL UNIQUE,
    descripcion TEXT NOT NULL DEFAULT '',
    activa      INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS solicitud (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo          TEXT NOT NULL UNIQUE,
    fecha_registro  TEXT NOT NULL,
    solicitante_id  INTEGER NOT NULL REFERENCES usuario(id),
    categoria_id    INTEGER NOT NULL REFERENCES categoria(id),
    asunto          TEXT NOT NULL,
    descripcion     TEXT NOT NULL,
    prioridad       TEXT NOT NULL CHECK (prioridad IN ('BAJA','MEDIA','ALTA','URGENTE')),
    responsable_id  INTEGER REFERENCES usuario(id),
    estado          TEXT NOT NULL CHECK (estado IN
        ('REGISTRADA','ASIGNADA','EN_PROCESO','RESUELTA','CERRADA','RECHAZADA','REABIERTA')),
    solucion        TEXT,
    fecha_resolucion TEXT
);
CREATE TABLE IF NOT EXISTS historial (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    solicitud_id    INTEGER NOT NULL REFERENCES solicitud(id),
    fecha           TEXT NOT NULL,
    usuario_id      INTEGER NOT NULL REFERENCES usuario(id),
    tipo            TEXT NOT NULL CHECK (tipo IN ('REGISTRO','ASIGNACION','CAMBIO_ESTADO','OBSERVACION')),
    estado_anterior TEXT,
    estado_nuevo    TEXT,
    observacion     TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS notificacion (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id   INTEGER NOT NULL REFERENCES usuario(id),
    solicitud_id INTEGER REFERENCES solicitud(id),
    mensaje      TEXT NOT NULL,
    fecha        TEXT NOT NULL,
    leida        INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS ix_solicitud_estado ON solicitud(estado);
CREATE INDEX IF NOT EXISTS ix_solicitud_solicitante ON solicitud(solicitante_id);
CREATE INDEX IF NOT EXISTS ix_solicitud_responsable ON solicitud(responsable_id);
CREATE INDEX IF NOT EXISTS ix_historial_solicitud ON historial(solicitud_id);
CREATE INDEX IF NOT EXISTS ix_notificacion_usuario ON notificacion(usuario_id, leida);
"""


def conectar(ruta):
    conn = sqlite3.connect(ruta, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def crear_esquema(conn):
    conn.executescript(ESQUEMA)
    conn.commit()
