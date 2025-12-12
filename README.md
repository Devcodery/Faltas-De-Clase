# 🎓 Asistencia JCCM Tracker (Manual Edition)

![Python](https://img.shields.io/badge/Python-3.9-blue?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.3-black?style=for-the-badge&logo=flask&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-purple?style=for-the-badge&logo=bootstrap&logoColor=white)

> **Sistema web dockerizado para el control manual de faltas en FP (DAM/DAW).**

---

## ⚡ Características Principales

* 👆 **Control Manual Rápido:** Botones de **Sumar (+)** y **Restar (-)** faltas directamente desde el dashboard.
* 📊 **Semáforo de Riesgo:** Las barras de progreso cambian de color según tu porcentaje de faltas (basado en el 15%/25% del límite).
    * 🟢 **Verde:** Todo bien.
    * 🟡 **Amarillo:** Cuidado (>50% consumido).
    * 🔴 **Rojo:** Peligro crítico (>80% consumido).
* 🐳 **100% Dockerizado:** Base de datos y Web en contenedores aislados.
* 🔒 **Seguridad:** Proxy inverso con **Caddy** (HTTPS automático) y gestión de secretos con `.env`.
* 📚 **Multicurso:** Separa visualmente las asignaturas de 1º y 2º de DAM.

---

## 🚀 Instalación y Despliegue

### 1. Configurar Variables
Crea un archivo `.env` en la raíz (basado en `.env.example`):
```env
DB_USER=admin
DB_PASS=tu_password_secreto
DB_NAME=asistencia_db
APP_PASSWORD=tu_contrasena_de_acceso_web
DATABASE_URL=postgresql://admin:tu_password_secreto@db:5432/asistencia_db
```

### 2. Arrancar el Servidor
```docker-compose up -d --build```

### 3. Carga Inicial de Datos (Seed)
Este paso es obligatorio la primera vez para crear las asignaturas en la base de datos:

```docker exec -it asistencia-app-web-1 python seed.py```

🎉 ¡Listo! Entra en http://localhost:5000 (o tu dominio si configuraste Caddy).

## 🛠️ Comandos de Mantenimiento (Cheatsheet)
Aquí tienes los comandos que necesitarás usar en el día a día para gestionar el servidor:

### 🌱 Reiniciar / Resetear las Asignaturas
Si cambias las horas en seed.py o quieres empezar de cero, ejecuta esto:

```docker exec -it asistencia-app-web-1 python seed.py```

### 📋 Ver Logs (Errores o Accesos)
Si algo falla (error 500), mira aquí qué está pasando en tiempo real:
```docker-compose logs -f web```

### 🐚 Entrar a la Terminal del Contenedor
Si necesitas investigar dentro del "ordenador" de Docker:
docker exec -it asistencia-app-web-1 /bin/bash

### 🔄 Recargar Caddy (Si cambias el dominio)
Si editas el Caddyfile, usa esto para aplicar cambios sin apagar la web:
```docker-compose restart caddy```

### 🗑️ Borrón y Cuenta Nueva (Peligro ⚠️)
Si quieres borrar toda la base de datos y empezar de cero absoluto:
```
docker-compose down -v
docker-compose up -d
docker exec -it asistencia-app-web-1 python seed.py
```

👤 Autor
Desarrollado por Eros Pacheco. Estudiante de Desarrollo de Aplicaciones Multiplataforma (DAM).