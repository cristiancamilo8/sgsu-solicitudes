# SGSU · Sistema de Gestión de Solicitudes Universitarias

Proyecto final de Ingeniería de Software. Aplicación web con Flask y SQLite.

## Cómo correrlo
```
pip install -r requirements.txt
python seed.py        # crea la base y los datos de ejemplo
python app.py         # abrir http://127.0.0.1:5000
```
Usuarios de ejemplo (clave `Clave1234`): admin@, supervisor@, funcionario1@, funcionario2@, estudiante1@, estudiante2@ + `cul.edu.co`.

## Pruebas
```
python -m unittest discover -s tests -t .
```

## Estructura
- `app.py`: rutas web, sesión, roles y CSRF
- `gestion/servicios.py`: reglas de negocio
- `gestion/ciclo_vida.py`: patrón State (estados y transiciones)
- `gestion/eventos.py`: patrón Observer (notificaciones)
- `gestion/repositorios.py`: patrón Repository (SQL)
- `gestion/db.py`: esquema de la base de datos
- `docs/Proyecto_Final_SGSU.docx`: informe con las cinco entregas
