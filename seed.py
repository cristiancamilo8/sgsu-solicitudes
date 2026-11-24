"""Carga datos de prueba. Uso: python seed.py"""
import os
from werkzeug.security import generate_password_hash
from gestion import db
from gestion.repositorios import UsuarioRepo, CategoriaRepo
from gestion.servicios import construir_servicios

RUTA = os.path.join(os.path.dirname(__file__), "solicitudes.db")


def sembrar(conn):
    db.crear_esquema(conn)
    u, c = UsuarioRepo(conn), CategoriaRepo(conn)
    if u.listar():
        return False
    for nombre, correo, rol in [("Administrador General", "admin@cul.edu.co", "ADMIN"),
                                ("Laura Gómez", "supervisor@cul.edu.co", "SUPERVISOR"),
                                ("Carlos Pérez", "funcionario1@cul.edu.co", "FUNCIONARIO"),
                                ("María Rodríguez", "funcionario2@cul.edu.co", "FUNCIONARIO"),
                                ("Cristian Corzo", "estudiante1@cul.edu.co", "ESTUDIANTE"),
                                ("Sofía Martínez", "estudiante2@cul.edu.co", "ESTUDIANTE")]:
        u.crear(nombre, correo, generate_password_hash("Clave1234"), rol)
    for n, d in [("Certificados y constancias", "Solicitud de documentos académicos"),
                 ("Soporte técnico", "Fallas de plataforma, correo o red"),
                 ("Bienestar universitario", "Apoyos, becas y actividades"),
                 ("Registro y matrículas", "Inscripción, homologaciones y notas")]:
        c.crear(n, d)
    conn.commit()
    svc = construir_servicios(conn)
    est1, est2 = u.por_correo("estudiante1@cul.edu.co"), u.por_correo("estudiante2@cul.edu.co")
    sup, f1 = u.por_correo("supervisor@cul.edu.co"), u.por_correo("funcionario1@cul.edu.co")
    a = svc.registrar(est1, 1, "Constancia de estudio", "Necesito una constancia de estudio para una EPS.", "MEDIA")
    svc.registrar(est2, 2, "No puedo entrar al aula virtual", "Me sale error de contraseña desde ayer.", "ALTA")
    svc.asignar(sup, a.id, f1.id, "Atender hoy")
    return True


if __name__ == "__main__":
    conn = db.conectar(RUTA)
    print("Datos de prueba cargados." if sembrar(conn) else "La base ya tenía usuarios; no se cambió nada.")
    print("Usuarios (clave: Clave1234): admin@, supervisor@, funcionario1@, funcionario2@, estudiante1@, estudiante2@ + cul.edu.co")
