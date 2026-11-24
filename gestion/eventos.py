"""Patrón Observer: el servicio publica eventos y los observadores reaccionan sin acoplarse."""
from collections import defaultdict
from .repositorios import UsuarioRepo, NotificacionRepo
from .modelos import ADMIN, SUPERVISOR


class BusEventos:
    def __init__(self):
        self._obs = defaultdict(list)

    def suscribir(self, evento, fn):
        self._obs[evento].append(fn)

    def publicar(self, evento, **datos):
        for fn in self._obs[evento]:
            fn(**datos)


class NotificadorInterno:
    """Observador que genera los avisos internos (RF10)."""

    def __init__(self, conn, bus):
        self.usuarios, self.notis = UsuarioRepo(conn), NotificacionRepo(conn)
        bus.suscribir("registrada", self.registrada)
        bus.suscribir("asignada", self.asignada)
        bus.suscribir("estado_cambiado", self.estado_cambiado)
        bus.suscribir("observacion", self.observacion)

    def _avisar(self, destinatarios, solicitud, mensaje, excepto=None):
        for uid in {d for d in destinatarios if d and d != excepto}:
            self.notis.crear(uid, solicitud.id, mensaje)

    def registrada(self, solicitud, actor):
        jefes = [u.id for u in self.usuarios.listar(solo_activos=True) if u.rol in (ADMIN, SUPERVISOR)]
        self._avisar(jefes + [solicitud.solicitante_id], solicitud,
                     f"Se registró la solicitud {solicitud.codigo}: {solicitud.asunto}")

    def asignada(self, solicitud, actor):
        self._avisar([solicitud.responsable_id], solicitud,
                     f"Se te asignó la solicitud {solicitud.codigo}: {solicitud.asunto}")
        self._avisar([solicitud.solicitante_id], solicitud,
                     f"Tu solicitud {solicitud.codigo} ya tiene un responsable", excepto=actor.id)

    def estado_cambiado(self, solicitud, actor, anterior):
        self._avisar([solicitud.solicitante_id, solicitud.responsable_id], solicitud,
                     f"La solicitud {solicitud.codigo} pasó de {anterior} a {solicitud.estado}",
                     excepto=actor.id)

    def observacion(self, solicitud, actor):
        self._avisar([solicitud.solicitante_id, solicitud.responsable_id], solicitud,
                     f"Nueva observación en la solicitud {solicitud.codigo}", excepto=actor.id)
