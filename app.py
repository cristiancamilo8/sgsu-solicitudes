"""Sistema de gestión de servicios y solicitudes universitarias (Flask + SQLite)."""
import csv, io, os, secrets
from functools import wraps
from flask import (Flask, abort, flash, g, redirect, render_template, request, session, url_for, Response)
from gestion import db
from gestion.modelos import *  # noqa: F401,F403
from gestion.ciclo_vida import destinos_permitidos
from gestion.repositorios import (UsuarioRepo, CategoriaRepo, NotificacionRepo, HistorialRepo)
from gestion.servicios import (AutenticacionService, UsuarioService, CategoriaService, ReporteService,
                           construir_servicios)


def crear_app(ruta_db=None, pruebas=False):
    app = Flask(__name__, template_folder="gestion/templates")
    app.config.update(SECRET_KEY=os.environ.get("SECRET_KEY", "cambia-esta-clave-en-produccion"),
                      TESTING=pruebas, SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")
    ruta_db = ruta_db or os.path.join(os.path.dirname(__file__), "solicitudes.db")
    conn = db.conectar(ruta_db)
    db.crear_esquema(conn)
    app.conn = conn
    solicitudes = construir_servicios(conn)
    usuarios_repo, cats_repo = UsuarioRepo(conn), CategoriaRepo(conn)
    notis_repo, hist_repo = NotificacionRepo(conn), HistorialRepo(conn)

    # ---------- seguridad: sesión, roles y CSRF ----------
    def usuario_actual():
        uid = session.get("uid")
        u = usuarios_repo.por_id(uid) if uid else None
        return u if u and u.activo else None

    @app.before_request
    def preparar():
        g.usuario = usuario_actual()
        if request.method == "POST" and not app.config["TESTING"]:
            token = session.get("_csrf")
            if not token or request.form.get("_csrf") != token:
                abort(400, "Token de seguridad inválido. Recarga la página.")

    @app.context_processor
    def comunes():
        if "_csrf" not in session:
            session["_csrf"] = secrets.token_hex(16)
        no_leidas = notis_repo.no_leidas(g.usuario.id) if g.usuario else 0
        return dict(csrf=session["_csrf"], usuario=g.usuario, no_leidas=no_leidas,
                    PRIORIDADES=PRIORIDADES, ESTADOS=ESTADOS, ROLES=ROLES)

    def requiere_login(f):
        @wraps(f)
        def w(*a, **k):
            if not g.usuario:
                return redirect(url_for("login"))
            return f(*a, **k)
        return w

    def requiere_rol(*roles):
        def deco(f):
            @wraps(f)
            @requiere_login
            def w(*a, **k):
                if g.usuario.rol not in roles:
                    abort(403)
                return f(*a, **k)
            return w
        return deco

    @app.errorhandler(403)
    def prohibido(e):
        return render_template("error.html", codigo=403, texto="No tienes permiso para ver esta página."), 403

    @app.errorhandler(PermisoError)
    def permiso(e):
        return render_template("error.html", codigo=403, texto=str(e)), 403

    # ---------- acceso ----------
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            try:
                u = AutenticacionService(conn).iniciar_sesion(request.form.get("correo"), request.form.get("password"))
                session.clear(); session["uid"] = u.id
                return redirect(url_for("inicio"))
            except ReglaNegocioError as e:
                flash(str(e), "error")
        return render_template("login.html")

    @app.route("/logout", methods=["POST"])
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.route("/")
    @requiere_login
    def inicio():
        resumen = ReporteService(conn).generar(
            **({} if g.usuario.rol in (ADMIN, SUPERVISOR) else {"o_responsable_o_solicitante": g.usuario.id}))
        recientes = resumen["filas"][:5]
        return render_template("inicio.html", resumen=resumen, recientes=recientes)

    # ---------- usuarios (RF02) ----------
    @app.route("/usuarios")
    @requiere_rol(ADMIN)
    def usuarios():
        return render_template("usuarios.html", lista=usuarios_repo.listar())

    @app.route("/usuarios/nuevo", methods=["GET", "POST"])
    @app.route("/usuarios/<int:uid>/editar", methods=["GET", "POST"])
    @requiere_rol(ADMIN)
    def usuario_form(uid=None):
        u = usuarios_repo.por_id(uid) if uid else None
        if uid and not u:
            abort(404)
        if request.method == "POST":
            f = request.form
            try:
                svc = UsuarioService(conn)
                if uid:
                    if uid == g.usuario.id and (f.get("rol") != ADMIN or not f.get("activo")):
                        raise ReglaNegocioError("No puedes quitarte el rol de administrador ni desactivarte.")
                    svc.editar(uid, f["nombre"], f["correo"], f["rol"], bool(f.get("activo")), f.get("password", ""))
                else:
                    svc.crear(f["nombre"], f["correo"], f["rol"], f.get("password", ""))
                flash("Usuario guardado.", "ok")
                return redirect(url_for("usuarios"))
            except ReglaNegocioError as e:
                flash(str(e), "error")
        return render_template("usuario_form.html", u=u)

    # ---------- categorías (RF03) ----------
    @app.route("/categorias", methods=["GET", "POST"])
    @requiere_rol(ADMIN)
    def categorias():
        if request.method == "POST":
            f = request.form
            try:
                cid = int(f["id"]) if f.get("id") else None
                CategoriaService(conn).guardar(cid, f["nombre"], f.get("descripcion", ""), bool(f.get("activa", "1")) if not cid else bool(f.get("activa")))
                flash("Categoría guardada.", "ok")
            except ReglaNegocioError as e:
                flash(str(e), "error")
            return redirect(url_for("categorias"))
        return render_template("categorias.html", lista=cats_repo.listar())

    # ---------- solicitudes (RF04 a RF09) ----------
    @app.route("/solicitudes")
    @requiere_login
    def solicitudes_lista():
        a = request.args
        filas = solicitudes.listar(g.usuario, estado=a.get("estado"), prioridad=a.get("prioridad"),
                                   categoria_id=a.get("categoria_id"), texto=a.get("q"))
        return render_template("solicitudes.html", filas=filas, categorias=cats_repo.listar(), f=a)

    @app.route("/solicitudes/nueva", methods=["GET", "POST"])
    @requiere_rol(ESTUDIANTE, FUNCIONARIO)
    def solicitud_nueva():
        if request.method == "POST":
            f = request.form
            try:
                s = solicitudes.registrar(g.usuario, f.get("categoria_id", ""), f.get("asunto", ""),
                                          f.get("descripcion", ""), f.get("prioridad", ""))
                flash(f"Solicitud {s.codigo} registrada.", "ok")
                return redirect(url_for("solicitud_detalle", sid=s.id))
            except ReglaNegocioError as e:
                flash(str(e), "error")
        return render_template("solicitud_form.html", categorias=cats_repo.listar(True), f=request.form)

    @app.route("/solicitudes/<int:sid>")
    @requiere_login
    def solicitud_detalle(sid):
        try:
            s = solicitudes.obtener(g.usuario, sid)
        except ReglaNegocioError:
            abort(404)
        return render_template(
            "solicitud_detalle.html", s=solicitudes.solicitudes.detalle(sid), hist=hist_repo.de_solicitud(sid),
            destinos=[d for d in destinos_permitidos(g.usuario, s) if d != ASIGNADA],
            puede_asignar=ASIGNADA in destinos_permitidos(g.usuario, s),
            funcionarios=usuarios_repo.listar(FUNCIONARIO, True),
            editable=estado_de_editable(s))

    def estado_de_editable(s):
        from gestion.ciclo_vida import estado_de
        return estado_de(s.estado).editable

    def accion(sid, fn, ok):
        try:
            fn()
            flash(ok, "ok")
        except ReglaNegocioError as e:
            flash(str(e), "error")
        return redirect(url_for("solicitud_detalle", sid=sid))

    @app.route("/solicitudes/<int:sid>/asignar", methods=["POST"])
    @requiere_login
    def solicitud_asignar(sid):
        f = request.form
        return accion(sid, lambda: solicitudes.asignar(g.usuario, sid, f.get("responsable_id", ""), f.get("observacion", "")),
                      "Responsable asignado.")

    @app.route("/solicitudes/<int:sid>/estado", methods=["POST"])
    @requiere_login
    def solicitud_estado(sid):
        f = request.form
        return accion(sid, lambda: solicitudes.cambiar_estado(g.usuario, sid, f.get("nuevo", ""),
                                                              f.get("observacion", ""), f.get("solucion", "")),
                      "Estado actualizado.")

    @app.route("/solicitudes/<int:sid>/observacion", methods=["POST"])
    @requiere_login
    def solicitud_observacion(sid):
        return accion(sid, lambda: solicitudes.observar(g.usuario, sid, request.form.get("texto", "")),
                      "Observación registrada.")

    # ---------- notificaciones (RF10) ----------
    @app.route("/notificaciones", methods=["GET", "POST"])
    @requiere_login
    def notificaciones():
        if request.method == "POST":
            notis_repo.marcar_leidas(g.usuario.id); conn.commit()
            return redirect(url_for("notificaciones"))
        return render_template("notificaciones.html", lista=notis_repo.de_usuario(g.usuario.id))

    # ---------- reportes (RF11) ----------
    def filtros_reporte():
        a = request.args
        return dict(estado=a.get("estado") or None, categoria_id=a.get("categoria_id") or None,
                    prioridad=a.get("prioridad") or None, responsable_id=a.get("responsable_id") or None,
                    desde=a.get("desde") or None, hasta=a.get("hasta") or None)

    @app.route("/reportes")
    @requiere_rol(SUPERVISOR, ADMIN)
    def reportes():
        r = ReporteService(conn).generar(**filtros_reporte())
        return render_template("reportes.html", r=r, f=request.args, categorias=cats_repo.listar(),
                               funcionarios=usuarios_repo.listar(FUNCIONARIO))

    @app.route("/reportes/csv")
    @requiere_rol(SUPERVISOR, ADMIN)
    def reportes_csv():
        r = ReporteService(conn).generar(**filtros_reporte())
        out = io.StringIO(); w = csv.writer(out)
        w.writerow(["Código", "Fecha", "Solicitante", "Categoría", "Prioridad", "Responsable", "Estado", "Asunto"])
        for x in r["filas"]:
            w.writerow([x["codigo"], x["fecha_registro"], x["solicitante"], x["categoria"], x["prioridad"],
                        x["responsable"] or "", x["estado"], x["asunto"]])
        return Response("\ufeff" + out.getvalue(), mimetype="text/csv",
                        headers={"Content-Disposition": "attachment; filename=reporte_solicitudes.csv"})

    return app


if __name__ == "__main__":
    aplicacion = crear_app()
    print("Abre http://127.0.0.1:5000  (usuarios de prueba: python seed.py)")
    aplicacion.run(debug=False)
