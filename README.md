# Mascotia.app — Bitácora de salud para mascotas

Aplicación web para que tutores de mascotas registren el perfil de sus animales y lleven una **bitácora de salud** (visitas al veterinario, vacunas, peso, fichas clínicas).

**Para reclutadores:** Proyecto académico en Django (Python). Incluye autenticación, perfiles de tutor con ubicación (región/ciudad/comuna), registro de mascotas y bitácora de salud por mascota. Para probar: clonar → copiar `mascotia/settings/local.py.example` a `local.py` y añadir una `SECRET_KEY` → `pip install -r requirements.txt` → `python manage.py migrate` → `python manage.py runserver` → abrir http://127.0.0.1:8000

---

## Sobre el proyecto

**Mascotia.app** es un proyecto académico desarrollado con **Django**. Incluye registro e inicio de sesión, flujo de completado de perfil del tutor (datos personales y ubicación con región/ciudad/comuna), registro de mascotas con foto y datos básicos, y un panel donde consultar el historial de salud de cada mascota (eventos clínicos, peso, vacunas, etc.).

Está pensado para que un reclutador o evaluador pueda entender de un vistazo qué hace la aplicación y cómo ponerla en marcha de forma local.

---

## Tecnologías

| Área        | Stack                          |
|------------|---------------------------------|
| Backend    | Python 3, Django 5.x            |
| Base de datos | SQLite (desarrollo)          |
| Frontend   | HTML, CSS, JavaScript, Tailwind CSS |
| Autenticación | Django auth (login/registro) |

---

## Funcionalidades principales

- **Autenticación**: registro con email/contraseña, login, recuperación de clave, logout.
- **Perfil del tutor**: flujo guiado para completar datos (teléfono, ocupación, dirección, región/ciudad/comuna en cascada).
- **Registro de mascotas**: nombre, especie (perro/gato), raza, fecha de nacimiento, sexo, esterilización, foto, microchip.
- **Panel principal (home)**: listado de mascotas del usuario con acceso a perfil y bitácora de cada una.
- **Bitácora por mascota**: historial de eventos clínicos, vacunas, peso y fichas clínicas.
- **Notificaciones en UI**: mensajes de éxito/error que se muestran y se ocultan automáticamente.
- **Diseño responsivo** y navegación consistente (navbar, footer reutilizable).

---

## Estructura del proyecto

```
mascotia/
├── manage.py
├── requirements.txt
├── README.md
├── mascotia/                    # Proyecto Django
│   ├── settings/
│   │   ├── base.py              # Configuración base
│   │   ├── local.py.example     # Plantilla para config local (copiar a local.py)
│   │   └── __init__.py
│   ├── registro/                # App principal (auth + perfiles + mascotas)
│   │   ├── models.py            # User, PerfilTutor, Mascota, FichaClínica, etc.
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   ├── templates/registro/   # Plantillas HTML
│   │   └── static/registro/     # CSS, JS, imágenes, iconos
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── (env/ o venv/ no se sube al repo)
```

---

## Cómo ejecutarlo (desarrollo local)

### 1. Clonar y entrar al proyecto

```bash
git clone <url-del-repositorio>
cd mascotia
```

### 2. Entorno virtual y dependencias

```bash
python -m venv env
# Windows:
env\Scripts\activate
# Linux/macOS:
# source env/bin/activate

pip install -r requirements.txt
```

### 3. Configuración local (obligatoria)

El proyecto no incluye `local.py` por seguridad. Hay que crearlo a partir del ejemplo:

```bash
# Copiar la plantilla
copy mascotia\settings\local.py.example mascotia\settings\local.py   # Windows
# cp mascotia/settings/local.py.example mascotia/settings/local.py   # Linux/macOS
```

Generar una `SECRET_KEY` y añadirla en `mascotia/settings/local.py`:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. Base de datos y servidor

```bash
python manage.py migrate
python manage.py runserver
```

Opcional: usuario administrador para acceder a `/admin/`:

```bash
python manage.py createsuperuser
```

### 5. Acceso en el navegador

- **Inicio / Login**: http://127.0.0.1:8000/
- **Registro**: http://127.0.0.1:8000/registro/
- **Home (tras login)**: http://127.0.0.1:8000/home/
- **Admin**: http://127.0.0.1:8000/admin/

---

## Rutas principales

| Ruta | Descripción |
|------|-------------|
| `/` | Página de inicio (redirige a login) |
| `/login/` | Inicio de sesión |
| `/registro/` | Crear cuenta |
| `/completar-perfil/` | Completar datos del tutor |
| `/registro-mascota/` | Registrar una mascota |
| `/home/` | Panel con mascotas del usuario |
| `/mascotas/<id>/bitacora/` | Bitácora de salud de la mascota |
| `/mascotas/<id>/perfil/` | Perfil de la mascota |

---

## Nota de seguridad

Este repositorio está preparado para no incluir datos sensibles: `db.sqlite3`, `local.py`, `env/` y archivos de medios están en `.gitignore`. Cada desarrollador debe crear su propio `local.py` a partir de `local.py.example` y usar su propia `SECRET_KEY`.

---

## Resumen para reclutadores

- **Qué es**: aplicación web Django para bitácora de salud de mascotas (registro, perfil tutor, mascotas, historial clínico).
- **Qué ver**: código organizado en una app `registro` (models, views, forms, templates, estáticos), configuración en `settings/` y URLs en `mascotia/urls.py` y `registro/urls.py`.
- **Cómo probarlo**: clonar, crear `local.py` desde el ejemplo, `migrate`, `runserver`, y navegar por registro → completar perfil → registrar mascota → home y bitácora.

Si tienes dudas sobre el proyecto o quieres ver una demo, puedes contactar al autor del repositorio.
