"""Clases del dominio y constantes."""
from dataclasses import dataclass
from typing import Optional

ADMIN, ESTUDIANTE, FUNCIONARIO, SUPERVISOR = "ADMIN", "ESTUDIANTE", "FUNCIONARIO", "SUPERVISOR"
ROLES = (ADMIN, ESTUDIANTE, FUNCIONARIO, SUPERVISOR)
PRIORIDADES = ("BAJA", "MEDIA", "ALTA", "URGENTE")

REGISTRADA, ASIGNADA, EN_PROCESO = "REGISTRADA", "ASIGNADA", "EN_PROCESO"
RESUELTA, CERRADA, RECHAZADA, REABIERTA = "RESUELTA", "CERRADA", "RECHAZADA", "REABIERTA"
ESTADOS = (REGISTRADA, ASIGNADA, EN_PROCESO, RESUELTA, CERRADA, RECHAZADA, REABIERTA)


@dataclass
class Usuario:
    id: int
    nombre: str
    correo: str
    rol: str
    activo: bool = True
    password_hash: str = ""

    @classmethod
    def de_fila(cls, f):
        return cls(f["id"], f["nombre"], f["correo"], f["rol"], bool(f["activo"]), f["password_hash"])


@dataclass
class Categoria:
    id: int
    nombre: str
    descripcion: str
    activa: bool

    @classmethod
    def de_fila(cls, f):
        return cls(f["id"], f["nombre"], f["descripcion"], bool(f["activa"]))


@dataclass
class Solicitud:
    id: int
    codigo: str
    fecha_registro: str
    solicitante_id: int
    categoria_id: int
    asunto: str
    descripcion: str
    prioridad: str
    estado: str
    responsable_id: Optional[int] = None
    solucion: Optional[str] = None
    fecha_resolucion: Optional[str] = None

    @classmethod
    def de_fila(cls, f):
        return cls(f["id"], f["codigo"], f["fecha_registro"], f["solicitante_id"], f["categoria_id"],
                   f["asunto"], f["descripcion"], f["prioridad"], f["estado"], f["responsable_id"],
                   f["solucion"], f["fecha_resolucion"])


class ReglaNegocioError(Exception):
    """Se intentó algo que las reglas de negocio no permiten."""


class PermisoError(Exception):
    """El usuario no tiene permiso para la operación."""
