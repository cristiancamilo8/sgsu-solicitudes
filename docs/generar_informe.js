const fs = require("fs");
const d = require("docx");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun, HeadingLevel,
  AlignmentType, WidthType, ShadingType, LevelFormat, BorderStyle, Footer, PageNumber, PageBreak } = d;

const M = JSON.parse(fs.readFileSync("/tmp/metrics.json"));
const IMG = "/home/claude/gestion_solicitudes/docs/img/";
const AZUL = "1F4E79";
const W = 9360;

function runs(t, base = {}) {
  return t.split(/(\*\*[^*]+\*\*)/).filter(Boolean).map(s =>
    s.startsWith("**") ? new TextRun({ text: s.slice(2, -2), bold: true, ...base }) : new TextRun({ text: s, ...base }));
}
const p = (t, o = {}) => new Paragraph({ spacing: { after: 120, line: 276 }, ...o, children: runs(t) });
const h1 = t => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(t)] });
const h2 = t => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(t)] });
const h3 = t => new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun(t)] });
const bl = t => new Paragraph({ numbering: { reference: "bul", level: 0 }, spacing: { after: 60, line: 276 }, children: runs(t) });
const nl = (t, ref = "num") => new Paragraph({ numbering: { reference: ref, level: 0 }, spacing: { after: 60, line: 276 }, children: runs(t) });
const salto = () => new Paragraph({ children: [new PageBreak()] });
const cap = t => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [new TextRun({ text: t, italics: true, size: 18, color: "59687A" })] });

function img(nombre, ancho, alt) {
  const [w, h] = M.imgs[nombre];
  return new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 80, after: 60 }, keepNext: true,
    children: [new ImageRun({ type: "png", data: fs.readFileSync(IMG + nombre), transformation: { width: ancho, height: Math.round(ancho * h / w) },
      altText: { title: alt, description: alt, name: nombre } })] });
}

const borde = { style: BorderStyle.SINGLE, size: 4, color: "BFC8D3" };
const bordes = { top: borde, bottom: borde, left: borde, right: borde };
function celda(txt, w, o = {}) {
  const partes = String(txt).split("\n");
  return new TableCell({ width: { size: w, type: WidthType.DXA }, borders: bordes,
    shading: o.fill ? { fill: o.fill, type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: 60, bottom: 60, left: 90, right: 90 },
    children: partes.map(x => new Paragraph({ spacing: { after: 20 }, children: runs(x, { size: 19, color: o.color, bold: o.bold }) })) });
}
function tabla(cab, filas, anchos) {
  return new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: anchos,
    rows: [new TableRow({ tableHeader: true, children: cab.map((c, i) => celda(c, anchos[i], { fill: AZUL, color: "FFFFFF", bold: true })) }),
      ...filas.map((f, r) => new TableRow({ cantSplit: true, children: f.map((c, i) => celda(c, anchos[i], { fill: r % 2 ? "F3F5F8" : undefined })) }))] });
}
const esp = () => new Paragraph({ spacing: { after: 160 }, children: [] });

// ======================= CONTENIDO =======================
const c = [];

// ---- Portada
c.push(new Paragraph({ spacing: { before: 1800, after: 120 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: "PROYECTO FINAL", bold: true, size: 40, color: AZUL })] }));
c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 360 }, children: [new TextRun({ text: "INGENIERÍA DE SOFTWARE", bold: true, size: 32 })] }));
c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 600 }, children: [new TextRun({ text: "Sistema de Gestión de Solicitudes Universitarias (SGSU)", size: 30 })] }));
["Asignatura: Ingeniería del Software", "Docente: Kevin Villarreal Jiménez", "Integrante: Cristian Camilo Corzo",
  "Fecha de entrega: 28 de noviembre de 2026"].forEach(t => c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 }, children: [new TextRun({ text: t, size: 24 })] })));
c.push(esp());
c.push(tabla(["Dato", "Información"], [
  ["Nombre del proyecto", "Sistema de Gestión de Solicitudes Universitarias (SGSU)"],
  ["Integrante", "Cristian Camilo Corzo"],
  ["Repositorio", "____________________________________________"],
  ["Tecnologías seleccionadas", "Python 3, Flask, SQLite, plantillas Jinja2 (HTML y CSS), unittest"]], [2600, 6760]));
c.push(salto());

// ======================= ENTREGA 1 =======================
c.push(h1("Entrega 1. Inicio y planificación"));
c.push(h2("1.1 Nombre y descripción del problema"));
c.push(p("**Nombre:** Sistema de Gestión de Solicitudes Universitarias (SGSU)."));
c.push(p("En la universidad, los estudiantes y funcionarios piden cosas todo el tiempo: una constancia de estudio, una revisión de notas, ayuda con la plataforma virtual, información de una beca. Esas peticiones llegan por correo, por WhatsApp o en la ventanilla, y cada canal las guarda a su manera. Un mismo caso puede quedar repartido en tres lugares sin que nadie lo vea completo."));
c.push(p("De ahí salen los problemas que el proyecto quiere atacar: no hay un registro único, a veces no se sabe quién está atendiendo cada caso, el solicitante no tiene cómo ver en qué va su petición y nadie puede medir cuánto se demora la respuesta ni qué tipo de solicitud es la más frecuente."));
c.push(h2("1.2 Justificación"));
c.push(p("Un registro central permite que cada solicitud tenga un código, una categoría, un responsable y un historial de lo que se hizo. El solicitante consulta el estado sin tener que escribir de nuevo para preguntar, el funcionario ve solo lo que le tocó y el supervisor puede sacar números reales: cuántos casos hay abiertos, cuáles llevan más tiempo y quién tiene más carga."));
c.push(p("Para la asignatura, el proyecto sirve para aplicar el proceso completo: planificar, levantar requisitos, modelar con UML, diseñar con objetos, programar, probar y documentar, manteniendo la coherencia entre todo eso."));
c.push(h2("1.3 Objetivos"));
c.push(p("**Objetivo general.** Construir un sistema que permita registrar, asignar, atender y consultar solicitudes de servicios universitarios, aplicando las técnicas de análisis, diseño, gestión de proyectos y control de calidad vistas en la asignatura."));
c.push(p("**Objetivos específicos:**"));
["Levantar y documentar los requisitos funcionales y no funcionales del sistema, junto con sus reglas de negocio.",
  "Modelar el sistema con UML (casos de uso, estados, clases) y con un modelo entidad-relación.",
  "Diseñar una arquitectura por capas con al menos dos patrones de diseño.",
  "Implementar los siete módulos obligatorios con autenticación, roles y base de datos relacional.",
  "Probar el sistema con casos automáticos y medir su calidad con métricas simples.",
  "Dejar el código en un repositorio con control de versiones y un manual breve de uso."].forEach(t => c.push(bl(t)));
c.push(h2("1.4 Alcance, límites y actores"));
c.push(p("**Incluye:** inicio de sesión con cuatro roles; gestión de usuarios y categorías; registro de solicitudes; asignación de responsables; cambios de estado con sus reglas; observaciones y solución; historial; avisos internos; reportes con filtros y descarga en CSV."));
c.push(p("**No incluye:** envío de correos (el enunciado lo marca como opcional), archivos adjuntos, recuperación de contraseña por correo, aplicación móvil ni conexión con los sistemas académicos reales de la universidad."));
c.push(tabla(["Actor", "Qué hace en el sistema"], [
  ["Administrador", "Gestiona usuarios, roles y categorías. También puede asignar responsables y consultar reportes."],
  ["Estudiante", "Registra solicitudes y consulta únicamente las suyas. Puede cerrar o reabrir una solicitud resuelta."],
  ["Funcionario", "Atiende las solicitudes que le asignan, registra observaciones y actualiza estados. También puede registrar sus propias solicitudes."],
  ["Supervisor", "Asigna y reasigna responsables, consulta el estado general, los indicadores y los reportes."]], [2200, 7160]));
c.push(esp());
c.push(h2("1.5 Modelo de proceso seleccionado"));
c.push(p("Elegí un proceso **iterativo e incremental con prácticas de Scrum ligero**: sprints cortos de una semana, un tablero de tareas con tres columnas (por hacer, en curso, hecho) y una revisión personal al final de cada sprint para ver qué quedó hecho y qué se mueve a la semana siguiente."));
c.push(p("Lo justifico así. El docente fija las entregas por etapas, y eso encaja con ir construyendo por incrementos. Para una sola persona, un Scrum completo con todos sus roles y ceremonias sería más papeleo que trabajo. Y una cascada pura me obligaría a tener todo definido antes de programar, cuando varias reglas (por ejemplo, quién puede asignar o quién cierra un caso) solo se aclaran al intentar implementarlas."));
c.push(p("Los incrementos previstos fueron tres: (1) usuarios, roles, categorías y autenticación; (2) registro, asignación, ciclo de vida e historial; (3) notificaciones, reportes, pruebas y documentación."));
c.push(h2("1.6 Cronograma y organización del trabajo"));
c.push(p("Las semanas se cuentan desde el inicio del proyecto. Todo el trabajo lo hace una sola persona, así que el cronograma deja holgura entre sprints."));
c.push(tabla(["Semana", "Actividad", "Producto"], [
  ["1", "Inicio y planificación", "Entrega 1"],
  ["2", "Análisis: requisitos, casos de uso, ER, estados", "Entrega 2"],
  ["3", "Diseño: arquitectura, clases, base de datos, prototipos", "Entrega 3"],
  ["4", "Sprint 1: usuarios, roles, categorías, login", "Módulos 1, 2 y acceso"],
  ["5", "Sprint 2: solicitudes, asignación, ciclo de vida, historial", "Módulos 3, 4 y 5"],
  ["6", "Sprint 3: avisos, reportes, pruebas, informe final", "Módulos 6 y 7, Entregas 4 y 5"],
  ["Final", "Ensayo de la sustentación", "Sustentación preparada"]], [1100, 5000, 3260]));
c.push(esp());
c.push(p("**Organización del trabajo:** como el proyecto lo desarrolla una sola persona, el mismo desarrollador cumple todos los roles: análisis, programación, pruebas y documentación. Como no hay otra persona que revise el código, se compensa con las pruebas automáticas y una relectura del código al cerrar cada sprint."));
c.push(h2("1.7 Riesgos y mitigación"));
c.push(tabla(["Riesgo", "Prob.", "Impacto", "Acción de mitigación"], [
  ["Tiempo insuficiente por cruces con otras materias", "Alta", "Alto", "Priorizar módulos obligatorios, dejar fuera lo opcional (correo) y hacer entregas pequeñas cada semana."],
  ["Errores que nadie más revisa", "Media", "Medio", "Pruebas automáticas en cada cambio y relectura del código al cerrar cada sprint."],
  ["Un imprevisto personal (enfermedad, trabajo, familia) frena varios días el avance", "Media", "Alto", "Avanzar por entregas pequeñas, dejar margen antes del 28 de noviembre y subir el código al repositorio con frecuencia."],
  ["Reglas de negocio ambiguas", "Media", "Medio", "Tabla de transiciones escrita y revisada con el docente antes de programar el ciclo de vida."],
  ["Pérdida de código o de documentos", "Baja", "Alto", "Repositorio con commits frecuentes y copia del informe en la nube."],
  ["Fallas de seguridad (contraseñas, accesos indebidos)", "Media", "Alto", "Contraseñas con hash, permisos validados en el servidor, token CSRF y pruebas de acceso por rol."],
  ["Datos inconsistentes en la base", "Media", "Medio", "Llaves foráneas, restricciones CHECK y validaciones en la capa de servicios."],
  ["Falla de la demostración el día de la sustentación", "Media", "Alto", "Script de datos de prueba (seed.py) y ensayo previo en el computador que se va a usar."],
  ["El alcance crece sin control", "Media", "Medio", "Todo cambio de alcance se anota y se justifica en el informe final."]], [2900, 800, 1100, 4560]));
c.push(salto());

// ======================= ENTREGA 2 =======================
c.push(h1("Entrega 2. Análisis del sistema"));
c.push(h2("2.1 Requisitos"));
c.push(h3("Requisitos funcionales"));
c.push(tabla(["Código", "Descripción"], [
  ["RF01", "Permitir el inicio de sesión y controlar el acceso según el rol."],
  ["RF02", "Permitir al administrador gestionar usuarios y roles."],
  ["RF03", "Permitir gestionar las categorías de solicitudes."],
  ["RF04", "Permitir a un estudiante registrar una solicitud."],
  ["RF05", "Permitir al estudiante consultar sus solicitudes y estados."],
  ["RF06", "Permitir al funcionario consultar las solicitudes asignadas."],
  ["RF07", "Permitir actualizar el estado respetando las reglas de negocio."],
  ["RF08", "Permitir registrar observaciones y la solución aplicada."],
  ["RF09", "Conservar y consultar el historial de cambios."],
  ["RF10", "Generar notificaciones internas ante eventos relevantes."],
  ["RF11", "Generar reportes y estadísticas para el supervisor."],
  ["RF12 (agregado)", "Permitir asignar y reasignar responsables (lo hacen administrador y supervisor)."],
  ["RF13 (agregado)", "Exportar el reporte filtrado a un archivo CSV."]], [1700, 7660]));
c.push(esp());
c.push(h3("Requisitos no funcionales"));
c.push(tabla(["Atributo", "Requisito y cómo se verifica"], [
  ["Seguridad", "Contraseñas guardadas con hash (no en texto plano), mínimo 8 caracteres. Permisos validados en el servidor, no solo ocultando botones. Token CSRF en formularios y cookie de sesión HttpOnly. Se verifica con las pruebas de acceso por rol."],
  ["Usabilidad", "Interfaces en español, con mensajes de error que dicen qué corregir. Las tareas frecuentes (registrar y consultar) están a un clic desde el menú."],
  ["Integridad", "Llaves foráneas activas y restricciones CHECK en roles, estados y prioridades. Cada cambio de estado deja su registro en el historial."],
  ["Disponibilidad", "El sistema corre en un solo equipo sin servicios externos; se arranca con un comando. No se pidió alta disponibilidad."],
  ["Mantenibilidad", "Arquitectura por capas, SQL concentrado en repositorios y reglas del ciclo de vida en una sola tabla de transiciones. Agregar un estado implica tocar un archivo."],
  ["Rendimiento", `Con ${M.total} solicitudes, una consulta filtrada tardó ${M.consulta_filtrada} s y el reporte completo ${M.reporte} s en la máquina de pruebas.`]], [1800, 7560]));
c.push(esp());
c.push(h2("2.2 Reglas de negocio y restricciones"));
c.push(tabla(["Código", "Regla"], [
  ["RN01", "Una solicitud solo puede ser registrada por un usuario autenticado y activo (estudiante o funcionario)."],
  ["RN02", "Toda solicitud debe estar asociada a una categoría activa."],
  ["RN03", "El estado inicial es Registrada."],
  ["RN04", "Solo el administrador o el supervisor pueden asignar o reasignar responsables, y el responsable debe ser un funcionario activo."],
  ["RN05", "Para pasar a Resuelta es obligatorio registrar la solución."],
  ["RN06", "Una solicitud Cerrada no puede modificarse, salvo con una reapertura hecha por el administrador o el supervisor, con motivo."],
  ["RN07", "Cada cambio de estado guarda fecha, usuario y observación o motivo."],
  ["RN08", "El estudiante solo ve sus propias solicitudes. El funcionario ve las que registró y las que tiene asignadas."],
  ["RN09", "Rechazar una solicitud y reabrirla exigen escribir el motivo. Una solicitud Rechazada es definitiva."],
  ["RN10", "Solo el funcionario asignado (o el administrador) puede pasar la solicitud a En proceso y a Resuelta."],
  ["RN11", "El solicitante, el supervisor o el administrador pueden cerrar una solicitud resuelta; el solicitante también puede reabrirla si la solución no le sirvió."],
  ["RN12", "El sistema valida los datos obligatorios (asunto, descripción de mínimo 10 caracteres, prioridad válida) antes de guardar."]], [1200, 8160]));
c.push(esp());
c.push(p("**Restricciones:** trabajo individual (un solo desarrollador), entrega el 28 de noviembre de 2026, base de datos relacional obligatoria y uso de herramientas libres. Las decisiones que el enunciado dejaba abiertas (quién asigna, quién cierra, qué estados extra se usan) quedaron escritas arriba en las reglas RN04, RN09 y RN11."));

c.push(h2("2.3 Historias de usuario"));
c.push(tabla(["ID", "Historia", "Criterio de aceptación"], [
  ["HU01", "Como usuario quiero iniciar sesión para acceder a las opciones de mi rol.", "Con datos correctos entra; con datos incorrectos ve un mensaje y no entra."],
  ["HU02", "Como administrador quiero crear y editar usuarios con su rol para controlar quién usa el sistema.", "No acepta correos repetidos ni contraseñas de menos de 8 caracteres."],
  ["HU03", "Como administrador quiero administrar las categorías para que las solicitudes se clasifiquen bien.", "Una categoría inactiva no aparece al registrar solicitudes."],
  ["HU04", "Como estudiante quiero registrar una solicitud para que la universidad la atienda.", "Se crea con código único, estado Registrada y queda en el historial."],
  ["HU05", "Como estudiante quiero ver el estado de mis solicitudes para no tener que preguntar por otro canal.", "Solo aparecen las mías, con su historial."],
  ["HU06", "Como supervisor quiero asignar cada solicitud a un funcionario para que alguien responda por ella.", "El funcionario recibe un aviso y la solicitud pasa a Asignada."],
  ["HU07", "Como funcionario quiero ver mis solicitudes asignadas y cambiarles el estado para avanzar el trabajo.", "Solo permite las transiciones válidas; Resuelta exige solución."],
  ["HU08", "Como funcionario quiero dejar observaciones para que quede constancia de lo que hice.", "Cada observación queda con fecha y autor."],
  ["HU09", "Como solicitante quiero recibir un aviso cuando mi solicitud cambie para enterarme sin consultar.", "Aparece un contador de avisos nuevos en el menú."],
  ["HU10", "Como supervisor quiero reportes por estado, categoría, prioridad, responsable y periodo para saber cómo vamos.", "Los filtros se combinan y el resultado se puede descargar en CSV."]], [700, 4300, 4360]));
c.push(esp());

c.push(h2("2.4 Diagrama de casos de uso"));
c.push(img("casos.png", 600, "Diagrama de casos de uso"));
c.push(cap("Figura 1. Casos de uso por actor."));
c.push(p("A continuación se describen en detalle tres casos de uso."));
const cu = (titulo, filas) => [h3(titulo), tabla(["Campo", "Descripción"], filas, [2000, 7360]), esp()];
cu("CU04. Registrar solicitud", [
  ["Actor", "Estudiante (también el funcionario, cuando necesita algo para sí)."],
  ["Precondición", "El usuario tiene sesión iniciada y existe al menos una categoría activa."],
  ["Flujo principal", "1. El usuario elige Nueva solicitud.\n2. Selecciona la categoría y escribe asunto y descripción.\n3. Elige la prioridad.\n4. Confirma.\n5. El sistema valida, guarda la solicitud con estado Registrada y le asigna un código SOL-AAAA-NNNN.\n6. El sistema anota el registro en el historial y avisa a administradores, supervisores y al solicitante."],
  ["Flujos alternos", "4a. Falta un dato o la descripción es muy corta: el sistema muestra el error y conserva lo escrito.\n4b. La categoría fue desactivada mientras tanto: el sistema pide elegir otra."],
  ["Postcondición", "Existe una solicitud Registrada con su primer movimiento en el historial."],
  ["Reglas", "RN01, RN02, RN03, RN12"]]).forEach(x => c.push(x));
cu("CU07. Asignar o reasignar responsable", [
  ["Actor", "Supervisor o administrador."],
  ["Precondición", "La solicitud está Registrada, Asignada o Reabierta."],
  ["Flujo principal", "1. El actor abre la solicitud.\n2. Escoge un funcionario de la lista y, si quiere, escribe una nota.\n3. Confirma.\n4. El sistema pone la solicitud en Asignada, guarda el responsable y registra el movimiento.\n5. El sistema avisa al funcionario y al solicitante."],
  ["Flujos alternos", "2a. La solicitud ya está En proceso, Resuelta, Cerrada o Rechazada: la opción no aparece y, si se fuerza, el sistema la rechaza.\n3a. El usuario elegido está inactivo o no es funcionario: error."],
  ["Postcondición", "La solicitud tiene responsable y estado Asignada."],
  ["Reglas", "RN04, RN07"]]).forEach(x => c.push(x));
cu("CU08. Atender y resolver una solicitud", [
  ["Actor", "Funcionario asignado."],
  ["Precondición", "La solicitud está Asignada o Reabierta y el funcionario es su responsable."],
  ["Flujo principal", "1. El funcionario abre la solicitud desde su lista.\n2. Cambia el estado a En proceso.\n3. Agrega observaciones mientras trabaja.\n4. Escribe la solución y cambia el estado a Resuelta.\n5. El sistema guarda la solución y la fecha de resolución, registra el cambio y avisa al solicitante.\n6. El solicitante cierra la solicitud o la reabre con un motivo."],
  ["Flujos alternos", "4a. No escribió la solución: el sistema no deja pasar a Resuelta.\n6a. El solicitante reabre: la solicitud vuelve a Reabierta y el supervisor la reasigna o el funcionario la retoma."],
  ["Postcondición", "La solicitud queda Resuelta (o Cerrada) con solución e historial completos."],
  ["Reglas", "RN05, RN07, RN10, RN11"]]).forEach(x => c.push(x));

c.push(h2("2.5 Flujo de información de la actividad principal"));
c.push(p("La actividad principal es el registro y la atención de una solicitud, de principio a fin."));
c.push(img("flujo.png", 330, "Diagrama de flujo del registro y atención de una solicitud"));
c.push(cap("Figura 2. Flujo de registro y atención."));

c.push(h2("2.6 Modelo entidad-relación"));
c.push(img("er.png", 470, "Modelo entidad-relación"));
c.push(cap("Figura 3. Modelo entidad-relación. La relación punteada entre usuario y solicitud es la del responsable."));
c.push(p("Usuario se relaciona dos veces con Solicitud: como solicitante (obligatorio) y como responsable (opcional, porque una solicitud recién registrada aún no tiene). El historial es un registro de movimientos de cada solicitud, y las notificaciones se guardan por usuario."));

c.push(h2("2.7 Diagrama de estados del ciclo de vida"));
c.push(img("estados.png", 400, "Diagrama de estados de la solicitud"));
c.push(cap("Figura 4. Ciclo de vida de una solicitud."));
c.push(p("Además de los cinco estados del enunciado se usan Rechazada y Reabierta. Rechazada es un estado final: sirve para casos duplicados o que no corresponden a la universidad. Reabierta se usa cuando una solución no sirvió; desde ahí el caso se reasigna o lo retoma el mismo responsable."));
c.push(salto());

// ======================= ENTREGA 3 =======================
c.push(h1("Entrega 3. Diseño del sistema"));
c.push(h2("3.1 Arquitectura y justificación"));
c.push(img("arquitectura.png", 380, "Arquitectura por capas"));
c.push(cap("Figura 5. Arquitectura por capas."));
c.push(p("Es una aplicación web monolítica organizada en cuatro capas. La capa web (Flask) recibe las peticiones, revisa la sesión y el rol, y devuelve las páginas. La capa de servicios aplica las reglas de negocio. Los repositorios son los únicos que escriben SQL. Debajo está SQLite."));
c.push(p("Un monolito por capas se ajusta al tamaño del problema: un solo desarrollador, una sola base de datos y pocos usuarios simultáneos. Separar en servicios independientes agregaría complejidad que no se necesita. Lo que sí se conservó es la separación interna, porque permite probar las reglas sin levantar el servidor web y cambiar la base de datos tocando solo los repositorios."));
c.push(h2("3.2 Módulos y componentes"));
c.push(tabla(["Módulo obligatorio", "Componentes que lo implementan"], [
  ["Gestión de usuarios", "UsuarioService, UsuarioRepo, rutas /usuarios"],
  ["Gestión de categorías", "CategoriaService, CategoriaRepo, ruta /categorias"],
  ["Registro de solicitudes", "SolicitudService.registrar, SolicitudRepo, rutas /solicitudes/nueva"],
  ["Asignación y atención", "SolicitudService.asignar, cambiar_estado y observar; ciclo_vida.py"],
  ["Seguimiento e historial", "HistorialRepo, tabla historial, detalle de la solicitud"],
  ["Notificaciones", "BusEventos, NotificadorInterno, NotificacionRepo, ruta /notificaciones"],
  ["Reportes y estadísticas", "ReporteService, ruta /reportes y /reportes/csv"],
  ["Acceso (transversal)", "AutenticacionService, decoradores de rol, token CSRF"]], [3000, 6360]));
c.push(esp());
c.push(h2("3.3 Diagrama de clases"));
c.push(img("clases.png", 600, "Diagrama de clases"));
c.push(cap("Figura 6. Diagrama de clases con atributos, operaciones, relaciones y multiplicidades."));
c.push(p("El modelo tiene seis clases principales de dominio (Usuario, Categoria, Solicitud, Movimiento de historial, Notificacion y EstadoSolicitud con sus siete subclases) y las clases de servicio que las manipulan."));
c.push(h2("3.4 Responsabilidades y colaboraciones"));
c.push(tabla(["Clase", "Responsabilidad", "Colabora con"], [
  ["Usuario", "Datos de la persona, su rol y si está activa.", "Solicitud, Notificacion"],
  ["Categoria", "Tipo de servicio; puede activarse o desactivarse.", "Solicitud"],
  ["Solicitud", "Datos del caso y su estado actual.", "Usuario, Categoria, Movimiento, EstadoSolicitud"],
  ["Movimiento", "Registro de cada hecho: quién, cuándo, qué cambió y por qué.", "Solicitud"],
  ["EstadoSolicitud", "Sabe a qué estados se puede pasar y quién está autorizado.", "SolicitudService"],
  ["SolicitudService", "Aplica las reglas: valida, cambia estados, guarda historial y publica eventos.", "Repositorios, EstadoSolicitud, BusEventos"],
  ["NotificadorInterno", "Escucha los eventos y crea los avisos a quien corresponda.", "BusEventos, NotificacionRepo"],
  ["ReporteService", "Cuenta y agrupa solicitudes según los filtros; calcula el tiempo promedio de resolución.", "SolicitudRepo"],
  ["Repositorios", "Todas las consultas SQL.", "Base de datos"]], [2000, 4560, 2800]));
c.push(esp());
c.push(h2("3.5 Diseño de la base de datos relacional"));
c.push(tabla(["Tabla", "Columnas principales y restricciones"], [
  ["usuario", "id (PK), nombre, correo (único), password_hash, rol (CHECK: ADMIN, ESTUDIANTE, FUNCIONARIO, SUPERVISOR), activo, creado_en"],
  ["categoria", "id (PK), nombre (único), descripcion, activa"],
  ["solicitud", "id (PK), codigo (único), fecha_registro, solicitante_id (FK usuario), categoria_id (FK categoria), responsable_id (FK usuario, opcional), asunto, descripcion, prioridad (CHECK: BAJA, MEDIA, ALTA, URGENTE), estado (CHECK: siete estados), solucion, fecha_resolucion"],
  ["historial", "id (PK), solicitud_id (FK), usuario_id (FK), fecha, tipo (CHECK: REGISTRO, ASIGNACION, CAMBIO_ESTADO, OBSERVACION), estado_anterior, estado_nuevo, observacion"],
  ["notificacion", "id (PK), usuario_id (FK), solicitud_id (FK, opcional), mensaje, fecha, leida"]], [1800, 7560]));
c.push(esp());
c.push(p("El esquema está en tercera forma normal: los nombres de categoría, solicitante y responsable se obtienen con JOIN y no se repiten en la tabla de solicitudes. Se crearon índices sobre estado, solicitante, responsable, solicitud del historial y usuario de las notificaciones, que son las columnas por las que más se filtra."));
c.push(h2("3.6 Prototipos de las interfaces principales"));
c.push(p("Los prototipos se hicieron directamente como pantallas de la aplicación. Las siguientes son las versiones finales."));
c.push(img("p_login.png", 420, "Pantalla de inicio de sesión")); c.push(cap("Figura 7. Inicio de sesión."));
c.push(img("p_nueva.png", 520, "Formulario de nueva solicitud")); c.push(cap("Figura 8. Registro de una solicitud (estudiante)."));
c.push(img("p_detalle.png", 520, "Detalle de una solicitud para el supervisor")); c.push(cap("Figura 9. Detalle de la solicitud con acciones e historial (supervisor)."));
c.push(img("p_reportes.png", 520, "Pantalla de reportes")); c.push(cap("Figura 10. Reportes y estadísticas (supervisor). Los datos son de demostración."));
c.push(h2("3.7 Patrones de diseño"));
c.push(h3("State (estado) en el ciclo de vida"));
c.push(p("**Dónde:** gestion/ciclo_vida.py. Cada estado es una clase que declara a qué estados puede pasar la solicitud y qué actores pueden hacer ese paso. **Por qué:** sin el patrón, las reglas quedarían como una cadena de if sobre el estado dentro de SolicitudService, y cada estado nuevo (como Rechazada y Reabierta, que se agregaron en pleno análisis) obligaría a editar varios lugares. Con el patrón, agregar un estado es agregar una clase, y las pruebas recorren la misma tabla que usa el sistema."));
c.push(h3("Observer (observador) en las notificaciones"));
c.push(p("**Dónde:** gestion/eventos.py. SolicitudService publica eventos (registrada, asignada, estado_cambiado, observacion) en un BusEventos y NotificadorInterno se suscribe a ellos. **Por qué:** el servicio no debería saber cómo ni a quién se avisa. Así, el envío de correos, que quedó como opcional, se puede sumar después como otro observador sin tocar las reglas de negocio."));
c.push(h3("Repository (repositorio) para el acceso a datos"));
c.push(p("**Dónde:** gestion/repositorios.py. Una clase por entidad con todas las consultas SQL. **Por qué:** los servicios trabajan con objetos y no con SQL, las pruebas usan una base en memoria sin cambiar nada y, si el día de mañana se pasa a PostgreSQL o MySQL, el cambio queda en un solo archivo."));
c.push(salto());

// ======================= ENTREGA 4 =======================
c.push(h1("Entrega 4. Implementación y pruebas"));
c.push(h2("4.1 Aplicación funcional"));
c.push(p(`La aplicación implementa los siete módulos obligatorios y las reglas de negocio RN01 a RN12. Está escrita en Python con Flask; ${M.py[0]} archivos de código (${M.py[1]} líneas), ${M.plant[0]} plantillas HTML (${M.plant[1]} líneas) y una base SQLite que se crea sola al arrancar. Para probarla se carga un conjunto de datos de ejemplo con \`python seed.py\`.`));
c.push(h2("4.2 Autenticación y control de acceso"));
c.push(p("El usuario entra con correo y contraseña. La contraseña se guarda con hash (el que trae Werkzeug) y la sesión va en una cookie firmada. Cada ruta revisa el rol en el servidor; si alguien escribe a mano una dirección que no le corresponde, recibe un error 403. Los formularios llevan un token CSRF."));
c.push(tabla(["Operación", "Admin", "Estudiante", "Funcionario", "Supervisor"], [
  ["Gestionar usuarios, roles y categorías", "Sí", "No", "No", "No"],
  ["Registrar solicitud", "No", "Sí", "Sí", "No"],
  ["Ver solicitudes", "Todas", "Las suyas", "Suyas y asignadas", "Todas"],
  ["Asignar o reasignar responsable", "Sí", "No", "No", "Sí"],
  ["Pasar a En proceso o Resuelta", "Sí", "No", "Si es el responsable", "No"],
  ["Cerrar o reabrir una Resuelta", "Sí", "Sí, si es suya", "No", "Sí"],
  ["Reabrir una Cerrada", "Sí", "No", "No", "Sí"],
  ["Agregar observaciones", "Sí", "En lo suyo", "En lo suyo", "Sí"],
  ["Reportes y CSV", "Sí", "No", "No", "Sí"]], [3300, 1100, 1500, 1860, 1600]));
c.push(esp());
c.push(h2("4.3 Evidencias de las funcionalidades principales"));
c.push(img("p_lista_estudiante.png", 520, "Lista de solicitudes del estudiante")); c.push(cap("Figura 11. Un estudiante solo ve sus solicitudes."));
c.push(img("p_detalle_func.png", 520, "Detalle de una solicitud para el funcionario")); c.push(cap("Figura 12. El funcionario asignado puede pasar el caso a En proceso, anotar observaciones y resolver."));
c.push(img("p_usuarios.png", 520, "Gestión de usuarios")); c.push(cap("Figura 13. Gestión de usuarios (administrador)."));
c.push(img("p_inicio.png", 520, "Pantalla de inicio del supervisor")); c.push(cap("Figura 14. Inicio con contadores por estado."));
c.push(salto());

// ======================= ENTREGA 5 =======================
c.push(h1("Entrega 5. Informe final y sustentación"));
c.push(h2("5.1 Descripción de la solución y comparación con el alcance inicial"));
c.push(p("El SGSU es una aplicación web que centraliza las solicitudes universitarias. Cada solicitud tiene código, categoría, prioridad, solicitante, responsable, estado, solución e historial completo de movimientos. Los avisos internos llegan a quien corresponda y el supervisor puede sacar reportes con filtros y descargarlos."));
c.push(tabla(["Alcance planteado en la Entrega 1", "Resultado"], [
  ["Inicio de sesión con cuatro roles", "Hecho"],
  ["Gestión de usuarios y categorías", "Hecho"],
  ["Registro de solicitudes con validaciones", "Hecho"],
  ["Asignación, atención y ciclo de vida con reglas", "Hecho, con los estados extra Rechazada y Reabierta"],
  ["Seguimiento e historial", "Hecho"],
  ["Notificaciones internas", "Hecho"],
  ["Reportes por estado, categoría, prioridad, responsable y periodo", "Hecho, más descarga en CSV"],
  ["Correo electrónico", "No se hizo (opcional en el enunciado)"],
  ["Adjuntos y recuperación de contraseña", "Fuera del alcance desde el inicio"]], [5400, 3960]));
c.push(esp());
c.push(p("**Cambios de alcance justificados:** (1) se agregó la asignación por parte del administrador y del supervisor, porque el enunciado exigía un usuario autorizado y no decía cuál; (2) se permitió que el funcionario también registre solicitudes, ya que el planteamiento habla de solicitudes de estudiantes y de funcionarios; (3) se sumó la descarga en CSV porque los reportes sin exportar tienen poca utilidad práctica para un supervisor."));
c.push(h2("5.2 Arquitectura definitiva y tecnologías"));
c.push(p("La arquitectura final es la descrita en la Entrega 3; no hubo cambios estructurales. Tecnologías elegidas y por qué:"));
c.push(tabla(["Tecnología", "Motivo de la elección"], [
  ["Python 3", "Lenguaje que ya manejo; permite escribir las reglas de negocio de forma corta y legible."],
  ["Flask", "Framework pequeño: da rutas, sesiones y plantillas sin imponer una estructura pesada. Para siete módulos es suficiente."],
  ["SQLite", "Base de datos relacional incluida en Python, sin instalación ni servidor. Cumple el requisito y facilita la demostración. Para un uso real con muchos usuarios se cambiaría por PostgreSQL o MySQL, y gracias a los repositorios el cambio es acotado."],
  ["Jinja2 con HTML y CSS", "Interfaces simples que funcionan en cualquier navegador, sin proceso de compilación."],
  ["unittest", "Viene con Python, así que cualquiera ejecuta las pruebas sin instalar nada."],
  ["Git y un repositorio remoto", "Control de versiones y evidencia del avance del proyecto."]], [2400, 6960]));
c.push(esp());
c.push(h2("5.3 Resultados y evidencias de pruebas"));
c.push(p("Se escribieron 27 pruebas automáticas: 20 sobre las reglas de negocio y los servicios, y 7 sobre la capa web (acceso, roles y CSRF). Todas pasan. Se ejecutan con `python -m unittest discover -s tests -t .`."));
const pruebas = [
  ["P01", "Estado inicial Registrada y código con formato SOL-AAAA-NNNN", "RN03"],
  ["P02", "No se registra sin usuario autenticado", "RN01"],
  ["P03", "No se registra sin categoría válida", "RN02"],
  ["P04", "Se rechazan asunto vacío, descripción corta y prioridad inválida", "RN12"],
  ["P05", "El supervisor no puede registrar solicitudes", "RN01"],
  ["P06", "Solo administrador o supervisor asignan; estudiante y funcionario no", "RN04"],
  ["P07", "El responsable debe ser un funcionario", "RN04"],
  ["P08", "Asignar cambia el estado y se puede reasignar", "RN04"],
  ["P09", "Flujo completo Registrada a Cerrada", "RN05, RN11"],
  ["P10", "Resuelta exige solución", "RN05"],
  ["P11", "No se pueden saltar estados", "Ciclo de vida"],
  ["P12", "Solo el responsable atiende la solicitud", "RN10"],
  ["P13", "Una solicitud Cerrada no admite cambios salvo reapertura autorizada", "RN06"],
  ["P14", "Rechazar exige motivo", "RN09"],
  ["P15", "El historial guarda fecha, usuario y movimiento", "RN07"],
  ["P16", "Se generan avisos al registrar, asignar y cambiar de estado", "RF10"],
  ["P17", "El estudiante solo ve y abre sus solicitudes", "RN08"],
  ["P18", "El funcionario ve las solicitudes que le asignaron", "RN08"],
  ["P19", "El reporte suma bien y respeta los filtros", "RF11"],
  ["P20", "Usuarios: correo repetido, contraseña corta y hash guardado", "RF02"],
  ["P21", "Sin sesión, las rutas redirigen al login", "RF01"],
  ["P22", "Login con datos incorrectos muestra error", "RF01"],
  ["P23", "Cada rol solo entra a las rutas que le corresponden (403 en las demás)", "RF01"],
  ["P24", "Un estudiante no abre la solicitud de otro por la dirección", "RN08"],
  ["P25", "Registrar una solicitud desde el formulario web", "RF04"],
  ["P26", "El supervisor descarga el CSV", "RF13"],
  ["P27", "Un formulario sin token CSRF es rechazado", "Seguridad"]];
c.push(tabla(["ID", "Prueba", "Cubre", "Resultado"], pruebas.map(x => [...x, "Aprobada"]), [700, 5700, 1500, 1460]));
c.push(esp());
c.push(p("Durante las pruebas apareció un fallo real: la verificación del token CSRF aceptaba la petición cuando tanto el formulario como la sesión llegaban sin token, porque `None` es igual a `None`. La prueba P27 lo detectó y se corrigió exigiendo que el token exista."));
c.push(h3("Trazabilidad entre requisitos, implementación y pruebas"));
c.push(tabla(["Requisito", "Implementación", "Pruebas"], [
  ["RF01", "AutenticacionService, decoradores de rol", "P21, P22, P23"],
  ["RF02", "UsuarioService, /usuarios", "P20"],
  ["RF03", "CategoriaService, /categorias", "P03"],
  ["RF04", "SolicitudService.registrar, /solicitudes/nueva", "P01 a P05, P25"],
  ["RF05", "SolicitudService.listar y obtener", "P17, P24"],
  ["RF06", "SolicitudService.listar (filtro por responsable)", "P18"],
  ["RF07", "SolicitudService.cambiar_estado, ciclo_vida.py", "P09 a P14"],
  ["RF08", "cambiar_estado (solución) y observar", "P10, P13"],
  ["RF09", "HistorialRepo, detalle de la solicitud", "P15"],
  ["RF10", "BusEventos, NotificadorInterno", "P16"],
  ["RF11 y RF13", "ReporteService, /reportes y /reportes/csv", "P19, P26"],
  ["RF12", "SolicitudService.asignar", "P06 a P08"]], [1500, 5060, 2800]));
c.push(esp());
c.push(h2("5.4 Métricas"));
c.push(tabla(["Métrica", "Valor"], [
  ["Archivos de código Python (incluye seed.py)", `${M.py[0]}`],
  ["Líneas de código Python (sin líneas vacías)", `${M.py[1]}`],
  ["Plantillas HTML / líneas", `${M.plant[0]} / ${M.plant[1]}`],
  ["Líneas de pruebas", `${M.tests[1]}`],
  ["Pruebas automáticas / aprobadas", "27 / 27"],
  ["Cobertura de las reglas de negocio y datos (paquete gestion)", "88 %"],
  ["Tablas en la base de datos", "5"],
  ["Estados del ciclo de vida", "7"],
  ["Módulos obligatorios implementados", "7 de 7"],
  ["Requisitos funcionales cubiertos por pruebas", "13 de 13"],
  ["Tiempo de una consulta filtrada con 10 000 solicitudes", `${M.consulta_filtrada} s`],
  ["Tiempo del reporte general con 10 000 solicitudes", `${M.reporte} s`]], [6600, 2760]));
c.push(esp());
c.push(p("La cobertura se midió con la herramienta coverage sobre el paquete gestion, que contiene las reglas, el ciclo de vida, los repositorios y los eventos. La capa web (app.py) se prueba con el cliente de pruebas de Flask, pero no entra en ese porcentaje. Los tiempos son de la máquina de pruebas y sirven como referencia, no como promesa."));
c.push(h2("5.5 Repositorio y manual breve de instalación y uso"));
c.push(p("**Repositorio:** ____________________________________________"));
c.push(h3("Instalación"));
["Instalar Python 3.10 o superior.", "En la carpeta del proyecto: `pip install -r requirements.txt`.",
  "Cargar datos de ejemplo: `python seed.py`.", "Iniciar el sistema: `python app.py`.",
  "Abrir http://127.0.0.1:5000 en el navegador.",
  "Opcional: definir la variable de entorno SECRET_KEY con una clave propia antes de iniciar."].forEach(t => c.push(nl(t, "num2")));
c.push(h3("Usuarios de ejemplo (todos con la clave Clave1234)"));
c.push(tabla(["Rol", "Correo"], [
  ["Administrador", "admin@cul.edu.co"], ["Supervisor", "supervisor@cul.edu.co"],
  ["Funcionarios", "funcionario1@cul.edu.co, funcionario2@cul.edu.co"], ["Estudiantes", "estudiante1@cul.edu.co, estudiante2@cul.edu.co"]], [2400, 6960]));
c.push(esp());
c.push(h3("Recorrido sugerido para la sustentación"));
["Entrar como estudiante1 y registrar una solicitud.", "Entrar como supervisor, abrir la solicitud y asignarla a un funcionario.",
  "Entrar como ese funcionario, pasar a En proceso, dejar una observación y resolver con una solución.",
  "Volver como estudiante1, ver el aviso y cerrar la solicitud.",
  "Como supervisor, abrir Reportes, aplicar un filtro y descargar el CSV.",
  "Mostrar que un estudiante recibe 403 al abrir /usuarios o la solicitud de otro."].forEach(t => c.push(nl(t, "num3")));
c.push(h2("5.6 Limitaciones y trabajo futuro"));
["Los correos electrónicos quedaron sin implementar; con el patrón Observer se pueden sumar como un observador más.",
  "Cada solicitud tiene un solo responsable a la vez.",
  "No hay archivos adjuntos ni recuperación de contraseña.",
  "SQLite es adecuada para una demostración y para pocos usuarios; para producción conviene otro motor de base de datos."].forEach(t => c.push(bl(t)));

// ======================= DOCUMENTO =======================
const numCfg = ref => ({ reference: ref, levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] });
const doc = new Document({
  creator: "Cristian Camilo Corzo", title: "Proyecto final de Ingeniería de Software",
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: "Arial", size: 32, bold: true, color: AZUL }, paragraph: { spacing: { before: 240, after: 160 }, keepNext: true, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: "Arial", size: 26, bold: true, color: AZUL }, paragraph: { spacing: { before: 240, after: 100 }, keepNext: true, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: "Arial", size: 23, bold: true }, paragraph: { spacing: { before: 160, after: 80 }, keepNext: true, outlineLevel: 2 } }] },
  numbering: { config: [
    { reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    numCfg("num"), numCfg("num2"), numCfg("num3")] },
  sections: [{ properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [
      new TextRun({ text: "Proyecto Final – Ingeniería de Software · Página ", size: 18, color: "59687A" }),
      new TextRun({ children: [PageNumber.CURRENT], size: 18, color: "59687A" })] })] }) },
    children: c.flat() }] });

Packer.toBuffer(doc).then(b => { fs.writeFileSync("/home/claude/gestion_solicitudes/docs/Proyecto_Final_SGSU.docx", b); console.log("docx listo"); });
