from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from scraper import actualizar_datos_desde_web # Importaremos tu scraper

app = Flask(__name__)
app.secret_key = 'clave_super_secreta_para_cookies' # Cambia esto

# Configuración DB
# Si no encuentra la variable (porque estás en local), usa la de fallback
uri = os.getenv('DATABASE_URL')
if not uri:
    # OJO: Aquí asumo que usaste el puerto 5433 o 5432. 
    # Si seguiste mi consejo de cambiar el puerto en docker-compose, usa 5433.
    uri = 'postgresql://admin:secreto123@localhost:5433/asistencia_db'

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELO DE LA BASE DE DATOS ---
class Asignatura(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    horas_totales = db.Column(db.Integer)
    horas_limite = db.Column(db.Integer) # El 25%
    horas_llevo = db.Column(db.Integer, default=0)

    @property
    def horas_restantes(self):
        return self.horas_limite - self.horas_llevo

# Crear tablas si no existen al iniciar
with app.app_context():
    db.create_all()
    # Aquí podríamos crear las asignaturas iniciales si está vacío

# --- RUTAS ---

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # Obtenemos datos de la DB ordenados
    asignaturas = Asignatura.query.order_by(Asignatura.nombre).all()
    return render_template('dashboard.html', asignaturas=asignaturas)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        # Verificamos contra la variable de entorno
        if request.form['password'] == os.getenv('APP_PASSWORD'):
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            error = 'Contraseña incorrecta'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/actualizar')
def actualizar():
    if not session.get('logged_in'): return redirect(url_for('login'))
    
    # Llamamos a tu scraper
    try:
        # Pasamos la instancia 'db' y la clase 'Asignatura' al scraper para que guarde
        actualizar_datos_desde_web(db, Asignatura)
        mensaje = "Datos actualizados correctamente"
    except Exception as e:
        mensaje = f"Error al actualizar: {e}"
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)