# 🎓 Control de Asistencia y Faltas de Clase (Multi-Usuario & RGPD)

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.3-black?style=for-the-badge&logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-purple?style=for-the-badge&logo=bootstrap&logoColor=white)
![RGPD](<https://img.shields.io/badge/RGPD%20%2F%20LSSI--CE-Compliant-success?style=for-the-badge>)

Sistema web multi-usuario con arquitectura modular, control de roles (Admin/Usuario), gestión dinámica de planes de estudio (cursos, asignaturas, límites personalizables al 25% o custom), integración preparada para Google OAuth y cumplimiento normativo RGPD/LSSI-CE.

---

## ✨ Nuevas Características Implementadas

1. **👥 Sistema Multi-Usuario & Autenticación Segura:**

   - Registro e inicio de sesión independiente para múltiples alumnos y profesores/administradores.
   - Hashing seguro de contraseñas con `werkzeug.security`.
   - Flujo preparado para **Google OAuth 2.0 (Google Identity Services)** con botón nativo y checkbox mandatorio de consentimiento previo.
   - Cuentas de demostración iniciales creadas en el seed (`admin@faltas.local` y `estudiante@faltas.local`).
2. **📚 Planes de Estudio Dinámicos y Personalizables:**

   - Asistente de configuración inicial: el usuario define qué estudia (ej. DAM, DAW, Ingeniería, Grado...), cuántos años lectivos dura (1, 2, 3, 4+ años) y qué porcentaje límite de faltas aplica (25% por defecto, 15%, 20%, etc.).
   - Organización automática de asignaturas por curso/año con cálculo automático del límite (`horas_totales * (porcentaje / 100)`).
   - CRUD completo de módulos/asignaturas: crear, editar horas o porcentaje, y eliminar.
   - Contadores rápidos **[+]** y **[-]** de faltas con actualización instantánea y semáforo visual de riesgo (🟢 Seguro, 🟡 Advertencia, 🔴 Peligro).
3. **👑 Panel de Administración Independiente (`/admin`):**

   - Landing page exclusiva para administradores con métricas globales del sistema.
   - Tabla de gestión de usuarios: supervisión de cuentas, visualización detallada de lo que estudia cada usuario, cambio dinámico de roles (Admin/Usuario) y eliminación de cuentas.
4. **⚖️ Cumplimiento Legal y Normativo (RGPD / LSSI-CE):**

   - Footer responsivo con enlaces legales en todas las vistas.
   - Banner de consentimiento de cookies técnicas (ePrivacy) con almacenamiento de preferencia local.
   - Checkbox obligatorio en el login/registro: *"Acepto los Términos y Condiciones y la Política de Privacidad"*.
   - Páginas legales dedicadas en español:
     - `/privacidad`: Política de Privacidad con cláusula específica sobre Google OAuth y tratamiento de datos escolares privados.
     - `/terminos`: Términos y Condiciones de Uso con descargo de responsabilidad sobre la exactitud de los horarios.
     - `/aviso-legal`: Aviso Legal conforme al Art. 10 de la Ley 34/2002 (LSSI-CE) con placeholders de titularidad.
     - `/cookies`: Política de Cookies técnicas y de sesión.

---

## 💾 Modelo de Datos Relacional

```Python
 [User] (1) <------------ (N) [Estudio] (1) <------------ (N) [Asignatura]
  - id                         - id                            - id
  - email (unique)             - user_id (FK)                  - estudio_id (FK)
  - nombre                     - nombre                        - nombre
  - rol (admin/usuario)        - duracion_anos                 - curso (1, 2, 3...)
  - password_hash              - porcentaje_calculo (25.0)     - horas_totales
  - google_id (unique)         - activo                        - porcentaje_calculo
  - acepto_terminos                                            - horas_limite
  - creado_en                                                  - horas_llevo
```

---

## 🧭 Rutas y Endpoints Principales

| Ruta                           | Método   | Descripción                                            | Permisos            |
| ------------------------------ | --------- | ------------------------------------------------------- | ------------------- |
| `/`                          | GET       | Redirección inteligente al Dashboard o Login           | Público            |
| `/login`                     | GET, POST | Inicio de sesión (con validación de términos RGPD)   | Público            |
| `/register`                  | GET, POST | Registro de nuevos alumnos                              | Público            |
| `/login/google`              | POST      | Endpoint de autenticación con Google OAuth             | Público            |
| `/logout`                    | GET       | Cierre de sesión seguro                                | Usuario autenticado |
| `/dashboard`                 | GET       | Dashboard del alumno con módulos por año y contadores | Usuario autenticado |
| `/setup-estudio`             | GET, POST | Asistente de configuración de titulación y %          | Usuario autenticado |
| `/asignaturas/nueva`         | POST      | Añadir nuevo módulo a un curso                        | Usuario autenticado |
| `/asignaturas/editar/<id>`   | POST      | Editar datos u horas de un módulo                      | Propietario / Admin |
| `/asignaturas/eliminar/<id>` | POST      | Eliminar módulo                                        | Propietario / Admin |
| `/sumar/<id>`                | GET, POST | Sumar 1 hora de falta al módulo                        | Propietario / Admin |
| `/restar/<id>`               | GET, POST | Restar 1 hora de falta al módulo                       | Propietario / Admin |
| `/admin`                     | GET       | Panel de control y métricas globales                   | Solo Administrador  |
| `/admin/usuario/<id>`        | GET       | Ficha y plan de estudio detallado de un alumno          | Solo Administrador  |
| `/privacidad`                | GET       | Política de Privacidad (RGPD)                          | Público            |
| `/terminos`                  | GET       | Términos y Condiciones de Uso                          | Público            |
| `/aviso-legal`               | GET       | Aviso Legal (LSSI-CE)                                   | Público            |
| `/cookies`                   | GET       | Política de Cookies                                    | Público            |

---

## 🚀 Puesta en Marcha con Docker

### 1. Variables de Entorno (`.env`)

Configura tus variables en `.env`:

```env
# Base de Datos
DB_USER=admin
DB_PASS=secreto123
SECRET_KEY=clave_secreta_super_segura

# Credenciales de Administrador (Creado/sincronizado automáticamente al arrancar)
ADMIN_EMAIL=admin@faltas.local
ADMIN_PASSWORD=admin123
ADMIN_NAME=Administrador Sistema

# Opcional para Google Sign-In (OAuth 2.0)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```

### 2. Arrancar Contenedores

```bash
docker-compose up -d --build
```

🎉 **¡Listo!** El sistema crea y sincroniza automáticamente la cuenta del Administrador al iniciar el contenedor. Ya no hace falta ejecutar ningún script de seed manual. Puedes modificar el correo o contraseña del administrador directamente desde el `.env`.

* **👑 Acceso Administrador:** El configurado en `ADMIN_EMAIL` y `ADMIN_PASSWORD` (ej: `admin@faltas.local` / `admin123`).
* **🎓 Alumnos:** Se registran desde la propia web (`/register` o con Google) y configuran en 1 minuto su plan de estudios y porcentaje de faltas.
