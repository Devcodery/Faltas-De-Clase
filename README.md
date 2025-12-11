# 🚀 Asistencia JCCM Tracker

![Python](https://img.shields.io/badge/Python-3.9-blue?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.0-black?style=for-the-badge&logo=flask&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-Scraping-43B02A?style=for-the-badge&logo=selenium&logoColor=white)

> **Automatización inteligente para el control de faltas en EducamosCLM / Papás 2.0**

Una aplicación **Full Stack** dockerizada que monitoriza automáticamente tu asistencia escolar. Realiza web scraping periódico al portal educativo, almacena los datos en PostgreSQL y ofrece un Dashboard visual con **Glassmorphism UI** para saber exactamente cuánto margen de faltas te queda antes de perder la evaluación continua.

---

## 📸 Capturas de Pantalla

| **Login Seguro** | **Dashboard & Métricas** |
|:---:|:---:|
| ![Login Screen](./capturas/login_preview.png) | ![Dashboard](./capturas/dashboard_preview.png) |
| *Acceso protegido con contraseña maestra* | *Visualización de progreso y alertas al 25%* |

---

## ⚡ Características Principales

* 🤖 **Web Scraping Automatizado:** Bot autónomo (Selenium + Chromium Headless) que navega por la intranet de la JCCM.
* 📊 **Cálculo de Riesgo en Tiempo Real:** Calcula automáticamente el límite del **25% de faltas** basado en las horas totales de cada módulo.
* 🎨 **UI Moderna:** Interfaz diseñada con **Bootstrap 5 + Jinja2**, implementando barras de progreso dinámicas (Verde/Amarillo/Rojo).
* 🐳 **Docker First:** Arquitectura de microservicios. Despliegue en un solo comando.
* 🔒 **Seguridad:** Gestión de credenciales mediante variables de entorno (`.env`) y sesiones seguras.
* 💾 **Persistencia:** Base de datos **PostgreSQL** integrada para histórico de datos.

---

## 🛠️ Stack Tecnológico

Este proyecto ha sido diseñado siguiendo el patrón **MVC** (Modelo-Vista-Controlador):

* **Backend:** Python 3 + Flask.
* **Base de Datos:** PostgreSQL + SQLAlchemy (ORM).
* **Scraping:** Selenium WebDriver + Chrome Driver.
* **Frontend:** HTML5, CSS3 (Glassmorphism), Bootstrap 5.
* **Infraestructura:** Docker & Docker Compose.

---

## 🚀 Instalación y Despliegue

### Requisitos previos
* Docker y Docker Compose instalados.
* Una cuenta activa en Papás 2.0 / EducamosCLM.

### 1. Clonar el repositorio
bash
git clone [https://github.com/tu-usuario/asistencia-jccm-tracker.git](https://github.com/tu-usuario/asistencia-jccm-tracker.git)
cd asistencia-jccm-tracker

2. Configurar Variables de Entorno
Crea un archivo .env en la raíz y rellénalo con tus datos:

Fragmento de código

# Base de Datos
DB_USER=admin
DB_PASS=tu_contrasena_db
DB_NAME=asistencia_db

# Seguridad Web
APP_PASSWORD=tu_contrasena_maestra

# Credenciales Instituto (Para el robot)
JCCM_USER=tu_usuario_papas
JCCM_PASS=tu_contrasena_papas
3. Levantar la Infraestructura
Bash

docker-compose up -d --build
4. Inicializar Datos Maestros (Seed)
Carga las asignaturas y horas totales del curso para calcular los porcentajes:

Bash

docker exec -it asistencia-app-web-1 python seed.py
🎉 ¡Listo! Accede a tu panel en: http://localhost:5000

📂 Estructura del Proyecto
Plaintext

asistencia-app/
├── docker-compose.yml      # Orquestación de servicios
├── .env                    # Secretos (NO SUBIR A GITHUB)
└── web/
    ├── Dockerfile          # Imagen de Python + Chrome
    ├── app.py              # Controlador principal (Flask)
    ├── scraper.py          # Lógica de extracción de datos
    ├── seed.py             # Semilla de datos iniciales
    ├── requirements.txt    # Dependencias
    └── templates/          # Vistas (HTML + Jinja2)
        ├── login.html
        └── dashboard.html
💡 Funcionamiento del "Semáforo" de Faltas
El sistema calcula el porcentaje de asistencia perdida sobre el total de horas del módulo:

🟢 < 50% del límite: Zona Segura.

🟡 > 50% del límite: Precaución.

🔴 > 85% del límite: ¡Peligro Crítico! (Riesgo de pérdida de evaluación).

👤 Autor
Desarrollado con ❤️ y mucho café por [Tu Nombre]. Estudiante de DAM - Desarrollo de Aplicaciones Multiplataforma.
