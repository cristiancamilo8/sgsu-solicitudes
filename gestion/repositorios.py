"""Patrón Repository: todo el SQL vive aquí; el resto del sistema trabaja con objetos."""
from datetime import datetime
from .modelos import Usuario, Categoria, Solicitud


def ahora():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class UsuarioRepo:
    def __init__(self, conn):
        self.c = conn

    def crear(self, nombre, correo, password_hash, rol):
        cur = self.c.execute(
            "INSERT INTO usuario(nombre, correo, password_hash, rol, creado_en) VALUES (?,?,?,?,?)",
            (nombre, correo.lower(), password_hash, rol, ahora()))
        return cur.lastrowid

    def por_id(self, uid):
        f = self.c.execute("SELECT * FROM usuario WHERE id=?", (uid,)).fetchone()
        return Usuario.de_fila(f) if f else None

    def por_correo(self, correo):
        f = self.c.execute("SELECT * FROM usuario WHERE correo=?", (correo.lower(),)).fetchone()
        return Usuario.de_fila(f) if f else None

    def listar(self, rol=None, solo_activos=False):
        sql, args = "SELECT * FROM usuario WHERE 1=1", []
        if rol:
            sql += " AND rol=?"; args.append(rol)
        if solo_activos:
            sql += " AND activo=1"
        return [Usuario.de_fila(f) for f in self.c.execute(sql + " ORDER BY nombre", args)]

    def actualizar(self, uid, nombre, correo, rol, activo, password_hash=None):
        self.c.execute("UPDATE usuario SET nombre=?, correo=?, rol=?, activo=? WHERE id=?",
                       (nombre, correo.lower(), rol, int(activo), uid))
        if password_hash:
            self.c.execute("UPDATE usuario SET password_hash=? WHERE id=?", (password_hash, uid))


class CategoriaRepo:
    def __init__(self, conn):
        self.c = conn

    def crear(self, nombre, descripcion):
        return self.c.execute("INSERT INTO categoria(nombre, descripcion) VALUES (?,?)",
                              (nombre, descripcion)).lastrowid

    def por_id(self, cid):
        f = self.c.execute("SELECT * FROM categoria WHERE id=?", (cid,)).fetchone()
        return Categoria.de_fila(f) if f else None

    def listar(self, solo_activas=False):
        sql = "SELECT * FROM categoria" + (" WHERE activa=1" if solo_activas else "") + " ORDER BY nombre"
        return [Categoria.de_fila(f) for f in self.c.execute(sql)]

    def actualizar(self, cid, nombre, descripcion, activa):
        self.c.execute("UPDATE categoria SET nombre=?, descripcion=?, activa=? WHERE id=?",
                       (nombre, descripcion, int(activa), cid))


CONSULTA_SOLICITUD = """
SELECT s.*, c.nombre AS categoria, u.nombre AS solicitante, r.nombre AS responsable
FROM solicitud s
JOIN categoria c ON c.id = s.categoria_id
JOIN usuario u ON u.id = s.solicitante_id
LEFT JOIN usuario r ON r.id = s.responsable_id
"""


class SolicitudRepo:
    def __init__(self, conn):
        self.c = conn

    def crear(self, solicitante_id, categoria_id, asunto, descripcion, prioridad, estado):
        fecha = ahora()
        cur = self.c.execute(
            "INSERT INTO solicitud(codigo, fecha_registro, solicitante_id, categoria_id, asunto,"
            " descripcion, prioridad, estado) VALUES ('TMP',?,?,?,?,?,?,?)",
            (fecha, solicitante_id, categoria_id, asunto, descripcion, prioridad, estado))
        sid = cur.lastrowid
        self.c.execute("UPDATE solicitud SET codigo=? WHERE id=?",
                       (f"SOL-{fecha[:4]}-{sid:04d}", sid))
        return sid

    def por_id(self, sid):
        f = self.c.execute("SELECT * FROM solicitud WHERE id=?", (sid,)).fetchone()
        return Solicitud.de_fila(f) if f else None

    def detalle(self, sid):
        return self.c.execute(CONSULTA_SOLICITUD + " WHERE s.id=?", (sid,)).fetchone()

    def buscar(self, estado=None, categoria_id=None, prioridad=None, responsable_id=None,
               solicitante_id=None, desde=None, hasta=None, o_responsable_o_solicitante=None,
               texto=None):
        sql, args = CONSULTA_SOLICITUD + " WHERE 1=1", []
        for col, val in (("s.estado", estado), ("s.categoria_id", categoria_id),
                         ("s.prioridad", prioridad), ("s.responsable_id", responsable_id),
                         ("s.solicitante_id", solicitante_id)):
            if val not in (None, ""):
                sql += f" AND {col}=?"; args.append(val)
        if desde:
            sql += " AND date(s.fecha_registro) >= date(?)"; args.append(desde)
        if hasta:
            sql += " AND date(s.fecha_registro) <= date(?)"; args.append(hasta)
        if o_responsable_o_solicitante:
            sql += " AND (s.solicitante_id=? OR s.responsable_id=?)"
            args += [o_responsable_o_solicitante] * 2
        if texto:
            sql += " AND (s.asunto LIKE ? OR s.codigo LIKE ?)"; args += [f"%{texto}%"] * 2
        return self.c.execute(sql + " ORDER BY s.id DESC", args).fetchall()

    def actualizar_estado(self, sid, estado, responsable_id=None, solucion=None, resuelta=False):
        self.c.execute("UPDATE solicitud SET estado=? WHERE id=?", (estado, sid))
        if responsable_id is not None:
            self.c.execute("UPDATE solicitud SET responsable_id=? WHERE id=?", (responsable_id, sid))
        if solucion is not None:
            self.c.execute("UPDATE solicitud SET solucion=? WHERE id=?", (solucion, sid))
        if resuelta:
            self.c.execute("UPDATE solicitud SET fecha_resolucion=? WHERE id=?", (ahora(), sid))


class HistorialRepo:
    def __init__(self, conn):
        self.c = conn

    def registrar(self, solicitud_id, usuario_id, tipo, estado_anterior, estado_nuevo, observacion=""):
        self.c.execute(
            "INSERT INTO historial(solicitud_id, fecha, usuario_id, tipo, estado_anterior,"
            " estado_nuevo, observacion) VALUES (?,?,?,?,?,?,?)",
            (solicitud_id, ahora(), usuario_id, tipo, estado_anterior, estado_nuevo, observacion))

    def de_solicitud(self, sid):
        return self.c.execute(
            "SELECT h.*, u.nombre AS usuario FROM historial h JOIN usuario u ON u.id=h.usuario_id"
            " WHERE h.solicitud_id=? ORDER BY h.id", (sid,)).fetchall()


class NotificacionRepo:
    def __init__(self, conn):
        self.c = conn

    def crear(self, usuario_id, solicitud_id, mensaje):
        self.c.execute("INSERT INTO notificacion(usuario_id, solicitud_id, mensaje, fecha) VALUES (?,?,?,?)",
                       (usuario_id, solicitud_id, mensaje, ahora()))

    def de_usuario(self, uid, limite=100):
        return self.c.execute("SELECT * FROM notificacion WHERE usuario_id=? ORDER BY id DESC LIMIT ?",
                              (uid, limite)).fetchall()

    def no_leidas(self, uid):
        return self.c.execute("SELECT COUNT(*) FROM notificacion WHERE usuario_id=? AND leida=0",
                              (uid,)).fetchone()[0]

    def marcar_leidas(self, uid):
        self.c.execute("UPDATE notificacion SET leida=1 WHERE usuario_id=?", (uid,))
