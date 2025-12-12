from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'tu_secreto_aqui'  # Cambia esto por un secreto seguro

# Configuración DB
uri = os.getenv('DATABASE_URL')
if not uri:
    # Fallback para local si no usas Docker
    uri = 'postgresql://admin:secreto123@localhost:5433/asistencia_db'
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELO ---
class Asignatura(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    horas_totales = db.Column(db.Integer)
    horas_limite = db.Column(db.Float)
    horas_llevo = db.Column(db.Integer, default=0)
    curso = db.Column(db.Integer, nullable=False, default=1)

    @property
    def horas_restantes(self):
        return self.horas_limite - self.horas_llevo

# Crear tablas
with app.app_context():
    db.create_all()

# --- RUTAS ---

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    asignaturas = Asignatura.query.order_by(Asignatura.curso, Asignatura.nombre).all()
    return render_template('dashboard.html', asignaturas=asignaturas)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
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

# --- NUEVAS RUTAS MANUALES ---

@app.route('/sumar/<int:id>')
def sumar(id):
    if not session.get('logged_in'): return redirect(url_for('login'))
    
    # Buscamos la asignatura por ID
    asig = Asignatura.query.get(id)
    if asig:
        asig.horas_llevo += 1 # Sumamos 1 falta
        db.session.commit()
        
    return redirect(url_for('index'))

@app.route('/restar/<int:id>')
def restar(id):
    if not session.get('logged_in'): return redirect(url_for('login'))
    
    asig = Asignatura.query.get(id)
    if asig and asig.horas_llevo > 0: # Evitamos números negativos
        asig.horas_llevo -= 1
        db.session.commit()
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)