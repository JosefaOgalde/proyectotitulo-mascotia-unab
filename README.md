# Proyecto Django - Mascotia.app

Este es un proyecto Django con sistema de autenticación (login y registro) para Mascotia.app - bitácora de salud animal.

## ⚠️ IMPORTANTE - Seguridad

**Este repositorio es privado y solo accesible para usuarios autorizados.**

Para poder ejecutar este proyecto localmente, necesitas:

1. **Configurar el archivo de configuración local**: 
   - Copia `mascotia/settings/local.py.example` a `mascotia/settings/local.py`
   - Ajusta los valores según tu entorno

2. **Generar tu propia SECRET_KEY**:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
   Luego agrega esta clave en `mascotia/settings/local.py`

3. **Crear la base de datos**:
   ```bash
   python manage.py migrate
   ```

**Sin estos pasos, el proyecto NO funcionará. Esto asegura que solo usuarios autorizados puedan utilizarlo.**

## Requisitos

- Python 3.x
- Dependencias de Python instaladas con `pip install -r requirements.txt`

## Estructura del Proyecto

```
mascotia/
├── manage.py
├── requirements.txt
├── ejecutar_django.ps1
├── iniciar_servidor.bat
├── limpiar_proyecto.ps1
├── mascotia/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── local.py
│   ├── registro/
│   │   ├── __init__.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   ├── models.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── tests.py
│   │   └── templates/
│   │       └── registro/
│   │           ├── base.html
│   │           ├── login.html
│   │           ├── registro.html
│   │           └── home.html
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── env/ (entorno virtual)
```

## Instalación y Ejecución

### Opción 1: Usar el script Batch (Recomendado para Windows)

1. Abre el archivo `iniciar_servidor.bat` haciendo doble clic
2. El servidor se iniciará automáticamente

### Opción 2: Usar el script PowerShell

1. Abre PowerShell en el directorio `mascotia/`
2. Ejecuta el script:
```powershell
.\ejecutar_django.ps1
```

### Opción 3: Ejecución manual

1. Activa el entorno virtual:
```powershell
.\env\Scripts\Activate.ps1
```

2. Instala dependencias:
```powershell
pip install -r requirements.txt
```

3. Aplica las migraciones:
```powershell
python manage.py migrate
```

4. Inicia el servidor de desarrollo:
```powershell
python manage.py runserver
```

## Acceso al Proyecto

Una vez que el servidor esté en ejecución, puedes acceder a:

- **Página de inicio (redirige a login)**: http://127.0.0.1:8000
- **Página de login**: http://127.0.0.1:8000/login/
- **Página de registro**: http://127.0.0.1:8000/registro/
- **Página principal (requiere autenticación)**: http://127.0.0.1:8000/home/
- **Panel de administración**: http://127.0.0.1:8000/admin/

## Funcionalidades

### Sistema de Autenticación

- **Registro de usuarios**: Los usuarios pueden crear una cuenta usando su email y contraseña
- **Login**: Los usuarios pueden iniciar sesión con su email y contraseña
- **Logout**: Los usuarios pueden cerrar sesión
- **Protección de rutas**: La página home requiere autenticación

### Características

- Validación de formularios y mensajes de feedback
- Diseño responsivo con Tailwind CSS
- Interfaz similar al diseño React original
- Autenticación segura usando el sistema de Django
- Flujo guiado de completado de perfil (sobrenombre, teléfono chileno, ocupación, dirección y ciudad)
- Sugerencias de dirección y ciudad mediante `datalist`
- Panel de control que muestra los datos del tutor una vez completado el perfil

## Aplicaciones Instaladas

- `mascotia.registro`: Aplicación de registro y autenticación

## Configuración

El proyecto usa un sistema de configuración dividido:
- `settings/base.py`: Configuración base
- `settings/local.py`: Configuración de desarrollo local

### Configuración de Autenticación

- `LOGIN_URL`: 'login' - URL para redirigir usuarios no autenticados
- `LOGIN_REDIRECT_URL`: 'home' - URL a la que redirigir después del login
- `LOGOUT_REDIRECT_URL`: 'login' - URL a la que redirigir después del logout

## Limpieza del Proyecto

Si necesitas limpiar carpetas redundantes y archivos temporales, ejecuta:

```powershell
.\limpiar_proyecto.ps1
```

**Nota**: Ejecuta este script cuando el servidor de Django NO esté corriendo.

## Notas

- Los usuarios se registran usando su email como nombre de usuario
- Las contraseñas deben tener al menos 6 caracteres
- Los mensajes de éxito/error se muestran automáticamente y se ocultan después de 5 segundos
- El flujo fuerza a completar el perfil (sobrenombre, teléfono, ocupación, dirección, ciudad) antes de ingresar al panel
- El proyecto utiliza SQLite como base de datos por defecto
- Si encuentras una carpeta `mascotia/mascotia/mascotia/` redundante, ciérrala en el explorador y ejecuta el script de limpieza

