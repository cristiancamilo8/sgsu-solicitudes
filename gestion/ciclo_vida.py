"""Patrón State: cada estado de la solicitud sabe a cuáles puede pasar y quién puede hacerlo.

Quién puede hacerlo se expresa con "actores": ADMIN, SUPERVISOR, RESPONSABLE (el funcionario
asignado) y SOLICITANTE (quien registró el caso).
"""
from .modelos import *  # noqa: F401,F403


class EstadoSolicitud:
    nombre = ""
    siguientes = {}          # estado destino -> actores autorizados
    exige_observacion = ()   # destinos que piden motivo u observación obligatoria
    editable = True          # admite observaciones nuevas


class EstRegistrada(EstadoSolicitud):
    nombre = REGISTRADA
    siguientes = {ASIGNADA: {ADMIN, SUPERVISOR}, RECHAZADA: {ADMIN, SUPERVISOR}}
    exige_observacion = (RECHAZADA,)


class EstAsignada(EstadoSolicitud):
    nombre = ASIGNADA
    siguientes = {EN_PROCESO: {ADMIN, "RESPONSABLE"},
                  ASIGNADA: {ADMIN, SUPERVISOR},                       # reasignación
                  RECHAZADA: {ADMIN, SUPERVISOR, "RESPONSABLE"}}
    exige_observacion = (RECHAZADA,)


class EstEnProceso(EstadoSolicitud):
    nombre = EN_PROCESO
    siguientes = {RESUELTA: {ADMIN, "RESPONSABLE"}}
    exige_observacion = (RESUELTA,)


class EstResuelta(EstadoSolicitud):
    nombre = RESUELTA
    siguientes = {CERRADA: {ADMIN, SUPERVISOR, "SOLICITANTE"},
                  REABIERTA: {ADMIN, SUPERVISOR, "SOLICITANTE"}}
    exige_observacion = (REABIERTA,)


class EstCerrada(EstadoSolicitud):
    nombre = CERRADA
    siguientes = {REABIERTA: {ADMIN, SUPERVISOR}}   # única forma de modificar un caso cerrado
    exige_observacion = (REABIERTA,)
    editable = False


class EstRechazada(EstadoSolicitud):
    nombre = RECHAZADA
    siguientes = {}
    editable = False


class EstReabierta(EstadoSolicitud):
    nombre = REABIERTA
    siguientes = {ASIGNADA: {ADMIN, SUPERVISOR}, EN_PROCESO: {ADMIN, "RESPONSABLE"}}


ESTADOS_CLASES = {c.nombre: c for c in (EstRegistrada, EstAsignada, EstEnProceso, EstResuelta,
                                        EstCerrada, EstRechazada, EstReabierta)}


def estado_de(nombre):
    return ESTADOS_CLASES[nombre]


def roles_efectivos(usuario, solicitud):
    """Rol del usuario más los 'actores' que cumple respecto de esta solicitud."""
    actores = {usuario.rol}
    if solicitud.responsable_id == usuario.id:
        actores.add("RESPONSABLE")
    if solicitud.solicitante_id == usuario.id:
        actores.add("SOLICITANTE")
    return actores


def destinos_permitidos(usuario, solicitud):
    """Estados a los que este usuario puede llevar la solicitud ahora mismo."""
    est = estado_de(solicitud.estado)
    mios = roles_efectivos(usuario, solicitud)
    return [d for d, quienes in est.siguientes.items() if mios & quienes]
