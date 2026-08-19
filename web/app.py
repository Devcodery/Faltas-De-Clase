import os
import time
import gzip
import requests
from functools import wraps
from datetime import datetime
from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify, g, send_from_directory, Response
from dotenv import load_dotenv
from models import db, User, Estudio, Asignatura

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'faltas-super-secret-key-change-in-prod-2026')

# Configuración DB
uri = os.getenv('DATABASE_URL')
if not uri:
    # Fallback para local si no se usa Docker
    uri = 'postgresql://admin:secreto123@localhost:5433/asistencia_db'
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Google OAuth Config
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')

# Google AdSense Config
ADSENSE_CLIENT_ID = os.getenv('ADSENSE_CLIENT_ID', '').strip()
ADSENSE_ENABLED = os.getenv('ADSENSE_ENABLED', 'true').strip().lower() in ('true', '1', 'yes')

db.init_app(app)


# --- DECORADORES DE SEGURIDAD ---

def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)

@app.before_request
def load_logged_in_user():
    g.user = get_current_user()

@app.after_request
def compress_and_cache(response):
    # Cabeceras de caché para archivos estáticos
    if request.path.startswith('/static/') or request.path in ('/favicon.ico', '/ads.txt'):
        response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
    
    # Compresión gzip para respuestas de texto/html/json
    accept_encoding = request.headers.get('Accept-Encoding', '')
    if ('gzip' in accept_encoding.lower() and 
        200 <= response.status_code < 300 and 
        'Content-Encoding' not in response.headers and
        response.mimetype in ('text/html', 'text/css', 'application/javascript', 'application/json', 'text/plain', 'image/svg+xml')):
        
        data = response.get_data()
        if len(data) > 400:
            response.direct_passthrough = False
            compressed_data = gzip.compress(data)
            response.set_data(compressed_data)
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Content-Length'] = len(compressed_data)
            response.headers['Vary'] = 'Accept-Encoding'

    return response

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            flash('Por favor inicia sesión para acceder a esta página.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            flash('Debes iniciar sesión con una cuenta de administrador.', 'warning')
            return redirect(url_for('login', next=request.url))
        if not g.user.is_admin:
            flash('Acceso denegado: Se requieren permisos de administrador.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_global_context():
    return {
        'current_user': g.user,
        'google_client_id': GOOGLE_CLIENT_ID,
        'adsense_client_id': ADSENSE_CLIENT_ID,
        'adsense_enabled': ADSENSE_ENABLED,
        'admin_email': ADMIN_EMAIL,
        'current_year': datetime.now().year
    }


# Variables de Administrador desde .env
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@faltas.local')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
ADMIN_NAME = os.getenv('ADMIN_NAME', 'Administrador Sistema')

def init_db_and_admin_user():
    # Espera activa y reintentos para permitir que PostgreSQL y la red interna inicien
    max_retries = 10
    for attempt in range(1, max_retries + 1):
        try:
            db.create_all()
            break
        except Exception as err:
            if attempt == max_retries:
                print(f"❌ Error al conectar con la base de datos tras {max_retries} intentos: {err}")
                raise err
            print(f"⏳ Conectando a la base de datos (intento {attempt}/{max_retries})...")
            time.sleep(2)

    if ADMIN_EMAIL and ADMIN_PASSWORD:
        email_clean = ADMIN_EMAIL.strip().lower()
        admin = User.query.filter_by(email=email_clean).first()
        if not admin:
            admin = User(
                email=email_clean,
                nombre=ADMIN_NAME.strip() if ADMIN_NAME else "Administrador",
                rol='admin',
                acepto_terminos=True
            )
            admin.set_password(ADMIN_PASSWORD)
            db.session.add(admin)
            db.session.commit()
            print(f"👑 Usuario Administrador creado automáticamente desde .env: {admin.email}")
        else:
            # Mantener sincronizado el rol y credencial desde .env
            admin.rol = 'admin'
            if ADMIN_NAME:
                admin.nombre = ADMIN_NAME.strip()
            admin.set_password(ADMIN_PASSWORD)
            db.session.commit()
            print(f"✔ Usuario Administrador sincronizado desde .env: {admin.email}")

# --- INICIALIZACIÓN AUTOMÁTICA AL ARRANCAR ---
with app.app_context():
    init_db_and_admin_user()


# --- RUTAS DE NAVEGACIÓN Y AUTENTICACIÓN ---

@app.route('/')
def index():
    if g.user:
        if g.user.is_admin and request.args.get('view') != 'user':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/ads.txt')
def ads_txt():
    if ADSENSE_CLIENT_ID:
        pub_id = ADSENSE_CLIENT_ID.replace('ca-', '')
        content = f"google.com, {pub_id}, DIRECT, f08c47fec0942fa0\n"
        return Response(content, mimetype='text/plain')
    return send_from_directory(app.root_path, 'ads.txt', mimetype='text/plain')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        # Verificación del checkbox obligatorio RGPD si se envió
        terminos = request.form.get('acepto_terminos')
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        # Compatibilidad con contraseña maestra antigua si se usa
        app_password = os.getenv('APP_PASSWORD')
        if app_password and password == app_password and not email:
            # Login rápido con admin demo
            admin_user = User.query.filter_by(rol='admin').first()
            if admin_user:
                session['user_id'] = admin_user.id
                flash(f'¡Bienvenido de nuevo, {admin_user.nombre}!', 'success')
                return redirect(url_for('admin_dashboard'))

        if not email or not password:
            flash('Por favor ingresa tu correo y contraseña.', 'danger')
            return render_template('login.html')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash(f'¡Bienvenido de nuevo, {user.nombre}!', 'success')
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))
        else:
            flash('Correo electrónico o contraseña incorrectos.', 'danger')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if g.user:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        acepto_terminos = request.form.get('acepto_terminos')

        if not acepto_terminos:
            flash('Debes aceptar los Términos y Condiciones y la Política de Privacidad para registrarte.', 'warning')
            return render_template('register.html')

        if not nombre or not email or not password:
            flash('Todos los campos son obligatorios.', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('Las contraseñas no coinciden.', 'danger')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('Ya existe una cuenta registrada con este correo electrónico.', 'danger')
            return render_template('register.html')

        # Crear nuevo usuario
        nuevo_usuario = User(
            nombre=nombre,
            email=email,
            rol='usuario',
            acepto_terminos=True
        )
        nuevo_usuario.set_password(password)
        db.session.add(nuevo_usuario)
        db.session.commit()

        session['user_id'] = nuevo_usuario.id
        flash('¡Cuenta creada exitosamente! Ahora configura tu plan de estudios.', 'success')
        return redirect(url_for('setup_estudio'))

    return render_template('register.html')


def verify_google_token(token):
    """
    Verifica el token de Google ID (JWT) contra los servidores de autenticación de Google.
    """
    try:
        resp = requests.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={token}", timeout=10)
        if resp.status_code == 200:
            payload = resp.json()
            # Si se configuró client_id, verificamos que coincida con el audience
            if GOOGLE_CLIENT_ID and payload.get('aud') != GOOGLE_CLIENT_ID:
                print(f"Audience mismatch: {payload.get('aud')} != {GOOGLE_CLIENT_ID}")
                return None
            return payload
    except Exception as e:
        print(f"Error verificando token de Google: {e}")
    return None


@app.route('/login/google', methods=['POST'])
def login_google():
    """
    Endpoint para autenticación con Google Identity Services (OAuth 2.0).
    Recibe el token de Google, verifica el payload y registra/inicia sesión.
    """
    data = request.get_json(silent=True) or request.form
    google_token = data.get('credential')
    google_email = data.get('email')
    google_name = data.get('name')
    google_sub = data.get('sub')
    avatar_url = data.get('picture')

    # Si recibimos el ID Token oficial de Google Identity Services
    if google_token:
        payload = verify_google_token(google_token)
        if payload:
            google_email = payload.get('email')
            google_name = payload.get('name', google_name or 'Usuario Google')
            google_sub = payload.get('sub')
            avatar_url = payload.get('picture')
        else:
            if request.is_json:
                return jsonify({'status': 'error', 'message': 'Token de Google no válido o expirado'}), 400
            flash('El token de autenticación de Google no es válido.', 'danger')
            return redirect(url_for('login'))

    if not google_email:
        if request.is_json:
            return jsonify({'status': 'error', 'message': 'No se recibieron credenciales válidas de Google'}), 400
        flash('No se recibieron credenciales válidas de Google.', 'danger')
        return redirect(url_for('login'))

    email_clean = google_email.strip().lower()
    user = User.query.filter((User.email == email_clean) | (User.google_id == google_sub)).first()

    if not user:
        # Registrar nuevo usuario vía Google
        user = User(
            email=email_clean,
            nombre=google_name or 'Usuario Google',
            google_id=google_sub or f"gid_{email_clean}",
            avatar_url=avatar_url,
            rol='usuario',
            acepto_terminos=True
        )
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        flash(f'¡Bienvenido a Control de Faltas, {user.nombre}! Configura tu plan de estudios a continuación.', 'success')
        target_url = url_for('setup_estudio')
    else:
        # Actualizar datos si vinieron de Google
        if google_sub and not user.google_id:
            user.google_id = google_sub
        if avatar_url and not user.avatar_url:
            user.avatar_url = avatar_url
        db.session.commit()
        session['user_id'] = user.id
        flash(f'¡Bienvenido de nuevo, {user.nombre}!', 'success')
        target_url = url_for('admin_dashboard') if user.is_admin else url_for('dashboard')

    if request.is_json:
        return jsonify({'status': 'success', 'redirect': target_url})
    return redirect(target_url)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('logged_in', None)
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('login'))


# --- RUTAS DE ESTUDIOS Y ASIGNATURAS (USUARIO) ---

@app.route('/dashboard')
@login_required
def dashboard():
    estudio = g.user.estudio_activo
    if not estudio:
        flash('Primero debes configurar lo que estás estudiando.', 'info')
        return redirect(url_for('setup_estudio'))

    # Agrupar asignaturas por año/curso
    asignaturas_por_curso = {}
    for curso_num in range(1, estudio.duracion_anos + 1):
        asignaturas_por_curso[curso_num] = [
            a for a in estudio.asignaturas if a.curso == curso_num
        ]

    # Estadísticas generales del estudio
    total_asignaturas = len(estudio.asignaturas)
    total_faltas = estudio.total_horas_llevo
    total_limite = estudio.total_horas_limite
    porcentaje_global = round((total_faltas / total_limite * 100), 1) if total_limite > 0 else 0

    return render_template(
        'dashboard.html',
        estudio=estudio,
        asignaturas_por_curso=asignaturas_por_curso,
        total_asignaturas=total_asignaturas,
        total_faltas=total_faltas,
        total_limite=total_limite,
        porcentaje_global=porcentaje_global
    )


@app.route('/setup-estudio', methods=['GET', 'POST'])
@login_required
def setup_estudio():
    estudio = g.user.estudio_activo

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        duracion_anos = int(request.form.get('duracion_anos', 2))
        porcentaje_calculo = float(request.form.get('porcentaje_calculo', 25.0))

        if not nombre:
            flash('Por favor indica qué estás estudiando.', 'danger')
            return render_template('setup_study.html', estudio=estudio)

        if duracion_anos < 1 or duracion_anos > 10:
            flash('La duración debe ser entre 1 y 10 años.', 'warning')
            return render_template('setup_study.html', estudio=estudio)

        if porcentaje_calculo <= 0 or porcentaje_calculo > 100:
            flash('El porcentaje de cálculo debe estar entre 1% y 100%.', 'warning')
            return render_template('setup_study.html', estudio=estudio)

        if estudio:
            estudio.nombre = nombre
            estudio.duracion_anos = duracion_anos
            estudio.porcentaje_calculo = porcentaje_calculo
            flash('Plan de estudios actualizado correctamente.', 'success')
        else:
            estudio = Estudio(
                user_id=g.user.id,
                nombre=nombre,
                duracion_anos=duracion_anos,
                porcentaje_calculo=porcentaje_calculo,
                activo=True
            )
            db.session.add(estudio)
            flash('¡Estudio configurado! Ahora añade tus asignaturas.', 'success')

        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('setup_study.html', estudio=estudio)


@app.route('/asignaturas/nueva', methods=['POST'])
@login_required
def nueva_asignatura():
    estudio = g.user.estudio_activo
    if not estudio:
        flash('No tienes un estudio activo.', 'danger')
        return redirect(url_for('setup_estudio'))

    nombre = request.form.get('nombre', '').strip()
    curso = int(request.form.get('curso', 1))
    horas_totales = int(request.form.get('horas_totales', 0))
    porcentaje = request.form.get('porcentaje_calculo')

    if not nombre or horas_totales <= 0:
        flash('Nombre y horas totales válidas son obligatorios.', 'danger')
        return redirect(url_for('dashboard'))

    pct = float(porcentaje) if porcentaje else estudio.porcentaje_calculo
    horas_limite = int(horas_totales * (pct / 100.0))

    asig = Asignatura(
        estudio_id=estudio.id,
        nombre=nombre,
        curso=curso,
        horas_totales=horas_totales,
        porcentaje_calculo=pct,
        horas_limite=horas_limite,
        horas_llevo=0
    )
    db.session.add(asig)
    db.session.commit()

    flash(f'Asignatura "{nombre}" añadida para el curso {curso}º.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/asignaturas/editar/<int:id>', methods=['POST'])
@login_required
def editar_asignatura(id):
    asig = Asignatura.query.get_or_404(id)
    if asig.estudio.user_id != g.user.id and not g.user.is_admin:
        flash('No tienes permiso para modificar esta asignatura.', 'danger')
        return redirect(url_for('dashboard'))

    nombre = request.form.get('nombre', '').strip()
    curso = int(request.form.get('curso', asig.curso))
    horas_totales = int(request.form.get('horas_totales', asig.horas_totales))
    porcentaje = float(request.form.get('porcentaje_calculo', asig.porcentaje_calculo))

    if nombre and horas_totales > 0:
        asig.nombre = nombre
        asig.curso = curso
        asig.horas_totales = horas_totales
        asig.porcentaje_calculo = porcentaje
        asig.horas_limite = int(horas_totales * (porcentaje / 100.0))
        db.session.commit()
        flash(f'Asignatura "{nombre}" actualizada correctamente.', 'success')

    return redirect(url_for('dashboard'))


@app.route('/asignaturas/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_asignatura(id):
    asig = Asignatura.query.get_or_404(id)
    if asig.estudio.user_id != g.user.id and not g.user.is_admin:
        flash('No tienes permiso para eliminar esta asignatura.', 'danger')
        return redirect(url_for('dashboard'))

    db.session.delete(asig)
    db.session.commit()
    flash('Asignatura eliminada.', 'info')
    return redirect(url_for('dashboard'))


@app.route('/sumar/<int:id>', methods=['GET', 'POST'])
@login_required
def sumar(id):
    asig = Asignatura.query.get_or_404(id)
    if asig.estudio.user_id != g.user.id and not g.user.is_admin:
        flash('Acción no permitida.', 'danger')
        return redirect(url_for('dashboard'))

    asig.horas_llevo += 1
    db.session.commit()
    return redirect(url_for('dashboard'))


@app.route('/restar/<int:id>', methods=['GET', 'POST'])
@login_required
def restar(id):
    asig = Asignatura.query.get_or_404(id)
    if asig.estudio.user_id != g.user.id and not g.user.is_admin:
        flash('Acción no permitida.', 'danger')
        return redirect(url_for('dashboard'))

    if asig.horas_llevo > 0:
        asig.horas_llevo -= 1
        db.session.commit()

    return redirect(url_for('dashboard'))


# --- PANEL DE ADMINISTRACIÓN ---

@app.route('/admin')
@admin_required
def admin_dashboard():
    usuarios = User.query.order_by(User.creado_en.desc()).all()
    total_usuarios = len(usuarios)
    total_estudios = Estudio.query.count()
    total_asignaturas = Asignatura.query.count()
    total_faltas_registradas = sum(a.horas_llevo for a in Asignatura.query.all())

    return render_template(
        'admin/dashboard.html',
        usuarios=usuarios,
        total_usuarios=total_usuarios,
        total_estudios=total_estudios,
        total_asignaturas=total_asignaturas,
        total_faltas_registradas=total_faltas_registradas
    )


@app.route('/admin/usuario/<int:user_id>')
@admin_required
def admin_user_detail(user_id):
    usuario = User.query.get_or_404(user_id)
    return render_template('admin/user_detail.html', target_user=usuario)


@app.route('/admin/usuario/<int:user_id>/toggle-rol', methods=['POST'])
@admin_required
def admin_toggle_rol(user_id):
    usuario = User.query.get_or_404(user_id)
    if usuario.id == g.user.id:
        flash('No puedes cambiar tu propio rol de administrador.', 'warning')
        return redirect(url_for('admin_dashboard'))

    usuario.rol = 'usuario' if usuario.rol == 'admin' else 'admin'
    db.session.commit()
    flash(f'Rol de {usuario.nombre} cambiado a {usuario.rol}.', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/usuario/<int:user_id>/eliminar', methods=['POST'])
@admin_required
def admin_eliminar_usuario(user_id):
    usuario = User.query.get_or_404(user_id)
    if usuario.id == g.user.id:
        flash('No puedes eliminar tu propia cuenta de administrador.', 'danger')
        return redirect(url_for('admin_dashboard'))

    db.session.delete(usuario)
    db.session.commit()
    flash(f'Usuario {usuario.email} y todos sus datos han sido eliminados.', 'info')
    return redirect(url_for('admin_dashboard'))


# --- PÁGINAS LEGALES Y DE CUMPLIMIENTO (RGPD / LSSI-CE) ---

@app.route('/privacidad')
def politica_privacidad():
    return render_template('legal/privacidad.html')


@app.route('/terminos')
def terminos_condiciones():
    return render_template('legal/terminos.html')


@app.route('/aviso-legal')
def aviso_legal():
    return render_template('legal/aviso_legal.html')


@app.route('/cookies')
def politica_cookies():
    return render_template('legal/cookies.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)