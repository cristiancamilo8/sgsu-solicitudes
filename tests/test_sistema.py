import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from gestion import db
from gestion.modelos import *  # noqa
from gestion.repositorios import UsuarioRepo, NotificacionRepo
from gestion.servicios import construir_servicios, ReporteService, UsuarioService
from seed import sembrar
from app import crear_app


def base():
    conn = db.conectar(":memory:")
    sembrar(conn)
    return conn


class PruebasReglas(unittest.TestCase):
    def setUp(self):
        self.conn = base()
        u = UsuarioRepo(self.conn)
        self.admin, self.sup = u.por_correo("admin@cul.edu.co"), u.por_correo("supervisor@cul.edu.co")
        self.f1, self.f2 = u.por_correo("funcionario1@cul.edu.co"), u.por_correo("funcionario2@cul.edu.co")
        self.e1, self.e2 = u.por_correo("estudiante1@cul.edu.co"), u.por_correo("estudiante2@cul.edu.co")
        self.svc = construir_servicios(self.conn)
        self.s = self.svc.registrar(self.e1, 1, "Prueba", "Descripción suficiente para la prueba", "BAJA")

    def llevar_a_en_proceso(self):
        self.svc.asignar(self.sup, self.s.id, self.f1.id)
        return self.svc.cambiar_estado(self.f1, self.s.id, EN_PROCESO)

    # --- registro ---
    def test_estado_inicial_registrada_y_codigo(self):
        self.assertEqual(self.s.estado, REGISTRADA)
        self.assertRegex(self.s.codigo, r"^SOL-\d{4}-\d{4}$")

    def test_registro_exige_usuario_autenticado(self):
        with self.assertRaises(PermisoError):
            self.svc.registrar(None, 1, "x", "descripcion larga ok", "BAJA")

    def test_registro_exige_categoria(self):
        with self.assertRaises(ReglaNegocioError):
            self.svc.registrar(self.e1, "", "x", "descripcion larga ok", "BAJA")

    def test_registro_valida_campos(self):
        with self.assertRaises(ReglaNegocioError):
            self.svc.registrar(self.e1, 1, "  ", "corta", "BAJA")
        with self.assertRaises(ReglaNegocioError):
            self.svc.registrar(self.e1, 1, "ok", "descripcion larga ok", "MAXIMA")

    def test_supervisor_no_registra(self):
        with self.assertRaises(PermisoError):
            self.svc.registrar(self.sup, 1, "x", "descripcion larga ok", "BAJA")

    # --- asignación ---
    def test_solo_autorizados_asignan(self):
        with self.assertRaises(PermisoError):
            self.svc.asignar(self.e1, self.s.id, self.f1.id)
        with self.assertRaises(PermisoError):
            self.svc.asignar(self.f1, self.s.id, self.f1.id)

    def test_responsable_debe_ser_funcionario(self):
        with self.assertRaises(ReglaNegocioError):
            self.svc.asignar(self.sup, self.s.id, self.e2.id)

    def test_asignar_cambia_estado_y_reasignar_funciona(self):
        s = self.svc.asignar(self.sup, self.s.id, self.f1.id)
        self.assertEqual((s.estado, s.responsable_id), (ASIGNADA, self.f1.id))
        s = self.svc.asignar(self.sup, self.s.id, self.f2.id)
        self.assertEqual(s.responsable_id, self.f2.id)

    # --- ciclo de vida ---
    def test_flujo_completo(self):
        self.llevar_a_en_proceso()
        s = self.svc.cambiar_estado(self.f1, self.s.id, RESUELTA, solucion="Se entregó la constancia")
        self.assertEqual(s.estado, RESUELTA)
        self.assertIsNotNone(s.fecha_resolucion)
        s = self.svc.cambiar_estado(self.e1, self.s.id, CERRADA)
        self.assertEqual(s.estado, CERRADA)

    def test_resuelta_exige_solucion(self):
        self.llevar_a_en_proceso()
        with self.assertRaises(ReglaNegocioError):
            self.svc.cambiar_estado(self.f1, self.s.id, RESUELTA)

    def test_no_se_saltan_estados(self):
        with self.assertRaises(ReglaNegocioError):
            self.svc.cambiar_estado(self.admin, self.s.id, CERRADA)
        with self.assertRaises(ReglaNegocioError):
            self.svc.cambiar_estado(self.admin, self.s.id, EN_PROCESO)

    def test_solo_el_responsable_atiende(self):
        self.svc.asignar(self.sup, self.s.id, self.f1.id)
        with self.assertRaises(PermisoError):
            self.svc.cambiar_estado(self.f2, self.s.id, EN_PROCESO)

    def test_cerrada_no_se_modifica_salvo_reapertura(self):
        self.llevar_a_en_proceso()
        self.svc.cambiar_estado(self.f1, self.s.id, RESUELTA, solucion="Listo")
        self.svc.cambiar_estado(self.e1, self.s.id, CERRADA)
        with self.assertRaises(ReglaNegocioError):
            self.svc.observar(self.e1, self.s.id, "Quiero agregar algo")
        with self.assertRaises(PermisoError):
            self.svc.cambiar_estado(self.e1, self.s.id, REABIERTA, "no funcionó")
        s = self.svc.cambiar_estado(self.sup, self.s.id, REABIERTA, "El estudiante reclama")
        self.assertEqual(s.estado, REABIERTA)

    def test_rechazo_exige_motivo(self):
        with self.assertRaises(ReglaNegocioError):
            self.svc.cambiar_estado(self.sup, self.s.id, RECHAZADA)
        s = self.svc.cambiar_estado(self.sup, self.s.id, RECHAZADA, "Solicitud duplicada")
        self.assertEqual(s.estado, RECHAZADA)

    # --- historial y notificaciones ---
    def test_historial_guarda_fecha_usuario_y_motivo(self):
        self.llevar_a_en_proceso()
        h = self.svc.historial.de_solicitud(self.s.id)
        self.assertEqual([x["tipo"] for x in h], ["REGISTRO", "ASIGNACION", "CAMBIO_ESTADO"])
        self.assertTrue(all(x["fecha"] and x["usuario_id"] for x in h))

    def test_notificaciones_en_eventos(self):
        n = NotificacionRepo(self.conn)
        self.assertGreaterEqual(n.no_leidas(self.sup.id), 1)      # aviso de registro
        self.svc.asignar(self.sup, self.s.id, self.f1.id)
        self.assertGreaterEqual(n.no_leidas(self.f1.id), 1)       # aviso de asignación
        self.svc.cambiar_estado(self.f1, self.s.id, EN_PROCESO)
        self.assertGreaterEqual(n.no_leidas(self.e1.id), 2)

    # --- visibilidad ---
    def test_estudiante_solo_ve_las_suyas(self):
        self.assertEqual(len(self.svc.listar(self.e2)), 1)   # solo la sembrada de e2
        with self.assertRaises(PermisoError):
            self.svc.obtener(self.e2, self.s.id)

    def test_funcionario_ve_asignadas(self):
        self.svc.asignar(self.sup, self.s.id, self.f2.id)
        self.assertIn(self.s.id, [r["id"] for r in self.svc.listar(self.f2)])

    # --- reportes ---
    def test_reporte_filtros_y_totales(self):
        r = ReporteService(self.conn).generar()
        self.assertEqual(r["total"], 3)
        self.assertEqual(sum(r["por_estado"].values()), 3)
        r2 = ReporteService(self.conn).generar(estado=REGISTRADA, prioridad="BAJA")
        self.assertEqual(r2["total"], 1)

    # --- usuarios ---
    def test_usuarios_validaciones(self):
        us = UsuarioService(self.conn)
        with self.assertRaises(ReglaNegocioError):
            us.crear("X", "admin@cul.edu.co", ESTUDIANTE, "Clave1234")   # correo repetido
        with self.assertRaises(ReglaNegocioError):
            us.crear("X", "nuevo@cul.edu.co", ESTUDIANTE, "123")          # clave corta
        uid = us.crear("Nuevo", "nuevo@cul.edu.co", ESTUDIANTE, "Clave1234")
        self.assertTrue(UsuarioRepo(self.conn).por_id(uid).password_hash.startswith(("scrypt", "pbkdf2")))


class PruebasWeb(unittest.TestCase):
    def setUp(self):
        self.app = crear_app(":memory:", pruebas=True)
        sembrar(self.app.conn)

    def entrar(self, correo):
        c = self.app.test_client()
        r = c.post("/login", data={"correo": correo, "password": "Clave1234"})
        self.assertEqual(r.status_code, 302)
        return c

    def test_sin_sesion_redirige(self):
        self.assertEqual(self.app.test_client().get("/solicitudes").status_code, 302)

    def test_login_incorrecto(self):
        r = self.app.test_client().post("/login", data={"correo": "admin@cul.edu.co", "password": "mala"})
        self.assertIn("incorrectos", r.get_data(as_text=True))

    def test_control_de_acceso_por_rol(self):
        est = self.entrar("estudiante1@cul.edu.co")
        for ruta in ("/usuarios", "/categorias", "/reportes"):
            self.assertEqual(est.get(ruta).status_code, 403, ruta)
        sup = self.entrar("supervisor@cul.edu.co")
        self.assertEqual(sup.get("/reportes").status_code, 200)
        self.assertEqual(sup.get("/usuarios").status_code, 403)
        self.assertEqual(self.entrar("admin@cul.edu.co").get("/usuarios").status_code, 200)

    def test_estudiante_no_ve_ajena(self):
        est2 = self.entrar("estudiante2@cul.edu.co")
        self.assertEqual(est2.get("/solicitudes/1").status_code, 403)
        self.assertEqual(est2.get("/solicitudes/2").status_code, 200)

    def test_registrar_por_web(self):
        c = self.entrar("estudiante1@cul.edu.co")
        r = c.post("/solicitudes/nueva", data={"categoria_id": "1", "asunto": "Web", "descripcion": "Probando desde la web", "prioridad": "ALTA"})
        self.assertEqual(r.status_code, 302)
        self.assertIn("Web", c.get("/solicitudes").get_data(as_text=True))

    def test_csv_para_supervisor(self):
        r = self.entrar("supervisor@cul.edu.co").get("/reportes/csv")
        self.assertEqual(r.mimetype, "text/csv")

    def test_csrf_se_exige_fuera_de_pruebas(self):
        app = crear_app(":memory:", pruebas=False)
        sembrar(app.conn)
        r = app.test_client().post("/login", data={"correo": "admin@cul.edu.co", "password": "Clave1234"})
        self.assertEqual(r.status_code, 400)


if __name__ == "__main__":
    unittest.main()
