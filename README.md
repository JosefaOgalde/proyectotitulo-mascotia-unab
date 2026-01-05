🐾 Mascotia.app – Proyecto de Título
Mascotia.app es una aplicación web desarrollada como proyecto de título para Ingeniería en Informática / Computación, orientada a la gestión digital del historial sanitario de mascotas.
Este repositorio es público con fines de portafolio profesional y no contiene datos personales reales ni credenciales.

🎯 Objetivo
Desarrollar un MVP funcional que permita a tutores registrar y administrar la información básica y clínica de sus mascotas, aplicando buenas prácticas de desarrollo web, seguridad y arquitectura.

🧩 Funcionalidades
Registro e inicio de sesión de usuarios.
Creación y gestión de perfiles de mascotas.
Asociación tutor–mascota.
Rutas protegidas mediante autenticación.
Configuración sensible separada del código versionado.

🛠️ Tecnologías
Backend: Python · Django
Frontend: HTML · Tailwind CSS
Base de datos: SQLite (desarrollo)
Control de versiones: Git · GitHub

🔐 Seguridad
No se versionan claves ni credenciales.
La configuración local se realiza mediante local.py (archivo no versionado).
Los datos utilizados son ficticios.

Ejecución local
git clone https://github.com/JosefaOgalde/proyectotitulo-mascotia-unab.git
cd proyectotitulo-mascotia-unab
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
cp mascotia/settings/local.py.example mascotia/settings/local.py
python manage.py migrate
python manage.py runserver
