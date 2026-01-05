# Configuración del Repositorio en GitHub

## Pasos para subir el proyecto a GitHub de forma segura

### 1. Crear el repositorio en GitHub

1. Ve a [GitHub](https://github.com) e inicia sesión
2. Haz clic en el botón **"New"** o **"+"** → **"New repository"**
3. Configura el repositorio:
   - **Nombre**: `mascotia` (o el nombre que prefieras)
   - **Descripción**: "Bitácora Digital de Salud Animal para Tutores"
   - **Visibilidad**: ⚠️ **Selecciona "Private"** (Privado)
   - **NO marques** "Add a README file" (ya tenemos uno)
   - **NO marques** "Add .gitignore" (ya tenemos uno)
   - **NO marques** "Choose a license"
4. Haz clic en **"Create repository"**

### 2. Inicializar Git en tu proyecto local

Abre PowerShell o CMD en la carpeta del proyecto y ejecuta:

```powershell
# Inicializar Git (si no está inicializado)
git init

# Agregar todos los archivos (el .gitignore excluirá los sensibles)
git add .

# Hacer el primer commit
git commit -m "Initial commit: Proyecto Mascotia.app"

# Conectar con el repositorio remoto (reemplaza TU_USUARIO con tu usuario de GitHub)
git remote add origin https://github.com/TU_USUARIO/mascotia.git

# Cambiar a la rama main (si es necesario)
git branch -M main

# Subir el código
git push -u origin main
```

### 3. Configurar el acceso al repositorio

#### Para dar acceso a otros usuarios:

1. Ve a tu repositorio en GitHub
2. Haz clic en **"Settings"** (Configuración)
3. En el menú lateral, haz clic en **"Collaborators"** (Colaboradores)
4. Haz clic en **"Add people"** (Agregar personas)
5. Ingresa el nombre de usuario o email de la persona a la que quieres dar acceso
6. Selecciona el nivel de acceso:
   - **Read**: Solo lectura (pueden ver el código pero no modificarlo)
   - **Write**: Lectura y escritura (pueden modificar el código)
   - **Admin**: Acceso completo (pueden cambiar configuraciones)
7. La persona recibirá una invitación por email

### 4. Verificar que los archivos sensibles NO se suban

Antes de hacer push, verifica que estos archivos NO estén incluidos:

```powershell
# Ver qué archivos se van a subir
git status

# Si ves alguno de estos archivos, NO deberían estar:
# - db.sqlite3
# - mascotia/settings/local.py
# - env/
# - media/
# - __pycache__/
```

Si alguno de estos archivos aparece, verifica que el `.gitignore` esté funcionando correctamente.

### 5. Archivos que SÍ se subirán (y están bien)

✅ `mascotia/settings/base.py` - Configuración base (sin secretos)
✅ `mascotia/settings/local.py.example` - Plantilla de configuración
✅ `requirements.txt` - Dependencias del proyecto
✅ `README.md` - Documentación
✅ `.gitignore` - Archivos a ignorar
✅ Todo el código fuente (templates, views, models, etc.)
✅ Archivos estáticos (CSS, imágenes, etc.)

### 6. Para clonar el repositorio (para otros usuarios autorizados)

Los usuarios autorizados pueden clonar el repositorio así:

```powershell
git clone https://github.com/TU_USUARIO/mascotia.git
cd mascotia

# Crear el archivo de configuración local
copy mascotia\settings\local.py.example mascotia\settings\local.py

# Editar local.py y agregar su propia SECRET_KEY
# (ver instrucciones en README.md)
```

## Seguridad del Repositorio

### ✅ Lo que está protegido:

- **SECRET_KEY**: No está en el repositorio (solo en local.py que está en .gitignore)
- **Base de datos**: `db.sqlite3` está en .gitignore
- **Archivos de usuarios**: La carpeta `media/` está en .gitignore
- **Entorno virtual**: `env/` está en .gitignore
- **Configuración local**: `local.py` está en .gitignore

### ⚠️ Importante:

- El repositorio debe ser **PRIVADO** en GitHub
- Solo tú y los usuarios que autorices podrán ver el código
- Sin el archivo `local.py` y la SECRET_KEY, el proyecto NO funcionará
- Esto asegura que solo usuarios autorizados puedan ejecutar el proyecto

## Actualizar el repositorio después de cambios

Cuando hagas cambios en el código:

```powershell
# Ver qué archivos cambiaron
git status

# Agregar los cambios
git add .

# Hacer commit con un mensaje descriptivo
git commit -m "Descripción de los cambios realizados"

# Subir los cambios
git push
```

## Notas adicionales

- **NUNCA** subas `local.py` al repositorio
- **NUNCA** subas `db.sqlite3` (contiene datos de usuarios)
- **NUNCA** subas la carpeta `media/` (contiene archivos de usuarios)
- Si accidentalmente subiste algo sensible, puedes eliminarlo del historial de Git (pero es mejor prevenir)

