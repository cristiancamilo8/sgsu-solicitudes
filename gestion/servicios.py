"""Capa de servicios: aquí se aplican las reglas de negocio."""
from werkzeug.security import generate_password_hash, check_password_hash
from .modelos import *  # noqa: F401,F403
from .repositorios import (UsuarioRepo, CategoriaRepo, SolicitudRepo, HistorialRepo, ahora)
from .ciclo_vida import estado_de, destinos_permitidos, roles_efectivos
from .eventos import BusEventos, NotificadorInterno


class AutenticacionService:
    def __init__(self, conn):
        self.usuarios = UsuarioRepo(conn)

    def iniciar_sesion(self, correo, password):
        u = self.usuarios.por_correo((correo or "").strip())
        if not u or not u.activo or not check_password_hash(u.password_hash, password or ""):
            raise ReglaNegocioError("Correo o contraseña incorrectos.")
        return u


class UsuarioService:
    def __init__(self, conn):
        self.c, self.repo = conn, UsuarioRepo(conn)

    def _validar(self, nombre, correo, rol, password, obligatoria):
        if not nombre.strip() or "@" not in correo or rol not in ROLES:
            raise ReglaNegocioError("Nombre, correo válido y rol son obligatorios.")
        if (obligatoria or password) and len(password) < 8:
            raise ReglaNegocioError("La contraseña debe tener mínimo 8 caracteres.")

    def crear(self, nombre, correo, rol, password):
        self._validar(nombre, correo, rol, password, True)
        if self.repo.por_correo(correo):
            raise ReglaNegocioError("Ya existe un usuario con ese correo.")
        uid = self.repo.crear(nombre.strip(), correo.strip(), generate_password_hash(password), rol)
        self.c.commit()
        return uid

    def editar(self, uid, nombre, correo, rol, activo, password=""):
        self._validar(nombre, correo, rol, password, False)
        otro = self.repo.por_correo(correo)
        if otro and otro.id != uid:
            raise ReglaNegocioError("Ese correo ya lo usa otro usuario.")
        self.repo.actualizar(uid, nombre.strip(), correo.strip(), rol, activo,
                             generate_password_hash(password) if password else None)
        self.c.commit()


class CategoriaService:
    def __init__(self, conn):
        self.c, self.repo = conn, CategoriaRepo(conn)

    def guardar(self, cid, nombre, descripcion, activa=True):
        if not nombre.strip():
            raise ReglaNegocioError("El nombre de la categoría es obligatorio.")
        try:
            if cid:
                self.repo.actualizar(cid, nombre.strip(), descripcion.strip(), activa)
            else:
                self.repo.crear(nombre.strip(), descripcion.strip())
        except Exception as e:  # nombre duplicado
            if "UNIQUE" in str(e):
                raise ReglaNegocioError("Ya existe una categoría con ese nombre.")
            raise
        self.c.commit()


class SolicitudService:
    def __init__(self, conn, bus=None):
        self.c = conn
        self.bus = bus or BusEventos()
        self.usuarios, self.categorias = UsuarioRepo(conn), CategoriaRepo(conn)
        self.solicitudes, self.historial = SolicitudRepo(conn), HistorialRepo(conn)

    # ---- consultas con control de visibilidad -------------------------------------------------
    def puede_ver(self, usuario, s):
        if usuario.rol in (ADMIN, SUPERVISOR):
            return True
        return usuario.id in (s.solicitante_id, s.responsable_id)

    def obtener(self, usuario, sid):
        s = self.solicitudes.por_id(sid)
        if not s:
            raise ReglaNegocioError("La solicitud no existe.")
        if not self.puede_ver(usuario, s):
            raise PermisoError("No tienes permiso para ver esta solicitud.")
        return s

    def listar(self, usuario, **filtros):
        if usuario.rol not in (ADMIN, SUPERVISOR):
            filtros["o_responsable_o_solicitante"] = usuario.id
        return self.solicitudes.buscar(**filtros)

    # ---- operaciones --------------------------------------------------------------------------
    def registrar(self, usuario, categoria_id, asunto, descripcion, prioridad):
        if usuario is None or not usuario.activo:
            raise PermisoError("Debes iniciar sesión para registrar una solicitud.")
        if usuario.rol not in (ESTUDIANTE, FUNCIONARIO):
            raise PermisoError("Tu rol no registra solicitudes.")
        cat = self.categorias.por_id(int(categoria_id)) if str(categoria_id).isdigit() else None
        if not cat or not cat.activa:
            raise ReglaNegocioError("Toda solicitud debe tener una categoría válida.")
        if not asunto.strip() or len(descripcion.strip()) < 10:
            raise ReglaNegocioError("Escribe un asunto y una descripción de al menos 10 caracteres.")
        if prioridad not in PRIORIDADES:
            raise ReglaNegocioError("La prioridad no es válida.")
        sid = self.solicitudes.crear(usuario.id, cat.id, asunto.strip(), descripcion.strip(),
                                     prioridad, REGISTRADA)
        self.historial.registrar(sid, usuario.id, "REGISTRO", None, REGISTRADA, "Solicitud registrada")
        self.c.commit()
        s = self.solicitudes.por_id(sid)
        self.bus.publicar("registrada", solicitud=s, actor=usuario)
        self.c.commit()
        return s

    def asignar(self, usuario, sid, responsable_id, observacion=""):
        s = self.obtener(usuario, sid)
        if ASIGNADA not in destinos_permitidos(usuario, s) and not (
                s.estado == REABIERTA and ASIGNADA in destinos_permitidos(usuario, s)):
            raise PermisoError("No puedes asignar esta solicitud en su estado actual.")
        resp = self.usuarios.por_id(int(responsable_id)) if str(responsable_id).isdigit() else None
        if not resp or resp.rol != FUNCIONARIO or not resp.activo:
            raise ReglaNegocioError("El responsable debe ser un funcionario activo.")
        anterior = s.estado
        self.solicitudes.actualizar_estado(s.id, ASIGNADA, responsable_id=resp.id)
        self.historial.registrar(s.id, usuario.id, "ASIGNACION", anterior, ASIGNADA,
                                 f"Responsable: {resp.nombre}. {observacion}".strip())
        self.c.commit()
        s = self.solicitudes.por_id(s.id)
        self.bus.publicar("asignada", solicitud=s, actor=usuario)
        self.c.commit()
        return s

    def cambiar_estado(self, usuario, sid, nuevo, observacion="", solucion=""):
        s = self.obtener(usuario, sid)
        actual = estado_de(s.estado)
        if nuevo not in actual.siguientes:
            raise ReglaNegocioError(f"No se puede pasar de {s.estado} a {nuevo}.")
        if nuevo == ASIGNADA:
            raise ReglaNegocioError("Para asignar o reasignar usa la opción de asignación.")
        if nuevo not in destinos_permitidos(usuario, s):
            raise PermisoError("No tienes autorización para este cambio de estado.")
        observacion, solucion = observacion.strip(), solucion.strip()
        if nuevo in actual.exige_observacion and not (observacion or solucion):
            raise ReglaNegocioError("Este cambio exige registrar una observación o el motivo.")
        if nuevo == RESUELTA and not solucion:
            raise ReglaNegocioError("Para marcar como Resuelta debes registrar la solución.")
        self.solicitudes.actualizar_estado(
            s.id, nuevo, solucion=solucion or None, resuelta=(nuevo == RESUELTA))
        self.historial.registrar(s.id, usuario.id, "CAMBIO_ESTADO", s.estado, nuevo,
                                 solucion if nuevo == RESUELTA else observacion)
        self.c.commit()
        nueva = self.solicitudes.por_id(s.id)
        self.bus.publicar("estado_cambiado", solicitud=nueva, actor=usuario, anterior=s.estado)
        self.c.commit()
        return nueva

    def observar(self, usuario, sid, texto):
        s = self.obtener(usuario, sid)
        if not estado_de(s.estado).editable:
            raise ReglaNegocioError("Una solicitud cerrada o rechazada no admite cambios.")
        if not texto.strip():
            raise ReglaNegocioError("La observación no puede estar vacía.")
        self.historial.registrar(s.id, usuario.id, "OBSERVACION", s.estado, s.estado, texto.strip())
        self.c.commit()
        self.bus.publicar("observacion", solicitud=s, actor=usuario)
        self.c.commit()


class ReporteService:
    def __init__(self, conn):
        self.c, self.repo = conn, SolicitudRepo(conn)

    def generar(self, **f):
        filas = self.repo.buscar(**f)

        def contar(clave):
            d = {}
            for r in filas:
                k = r[clave] or "Sin asignar"
                d[k] = d.get(k, 0) + 1
            return dict(sorted(d.items(), key=lambda x: -x[1]))

        horas = []
        for r in filas:
            if r["fecha_resolucion"]:
                a = datetime_(r["fecha_registro"]); b = datetime_(r["fecha_resolucion"])
                horas.append((b - a).total_seconds() / 3600)
        return {"total": len(filas), "filas": filas,
                "por_estado": contar("estado"), "por_categoria": contar("categoria"),
                "por_prioridad": contar("prioridad"), "por_responsable": contar("responsable"),
                "resueltas": len(horas),
                "promedio_horas": round(sum(horas) / len(horas), 1) if horas else None}


def datetime_(texto):
    from datetime import datetime
    return datetime.strptime(texto, "%Y-%m-%d %H:%M:%S")


def construir_servicios(conn):
    bus = BusEventos()
    NotificadorInterno(conn, bus)
    return SolicitudService(conn, bus)
