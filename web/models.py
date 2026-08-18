from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)
    google_id = db.Column(db.String(100), unique=True, nullable=True, index=True)
    avatar_url = db.Column(db.String(255), nullable=True)
    rol = db.Column(db.String(20), default='usuario', nullable=False)  # 'admin' o 'usuario'
    acepto_terminos = db.Column(db.Boolean, default=True, nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación 1-a-N con sus Estudios
    estudios = db.relationship('Estudio', backref='usuario', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.rol == 'admin'

    @property
    def estudio_activo(self):
        return next((e for e in self.estudios if e.activo), self.estudios[0] if self.estudios else None)


class Estudio(db.Model):
    __tablename__ = 'estudios'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    nombre = db.Column(db.String(150), nullable=False)  # Ej: DAM, DAW, Grado en Informática
    duracion_anos = db.Column(db.Integer, default=2, nullable=False)  # Cuántos años dura
    porcentaje_calculo = db.Column(db.Float, default=25.0, nullable=False)  # % de faltas límite (25% por defecto)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación 1-a-N con Asignaturas
    asignaturas = db.relationship('Asignatura', backref='estudio', lazy=True, cascade='all, delete-orphan')

    @property
    def total_horas_modulo(self):
        return sum(a.horas_totales for a in self.asignaturas)

    @property
    def total_horas_llevo(self):
        return sum(a.horas_llevo for a in self.asignaturas)

    @property
    def total_horas_limite(self):
        return sum(a.horas_limite for a in self.asignaturas)


class Asignatura(db.Model):
    __tablename__ = 'asignaturas'

    id = db.Column(db.Integer, primary_key=True)
    estudio_id = db.Column(db.Integer, db.ForeignKey('estudios.id'), nullable=False, index=True)
    nombre = db.Column(db.String(120), nullable=False)
    curso = db.Column(db.Integer, nullable=False, default=1)  # Año del estudio (1, 2, 3...)
    horas_totales = db.Column(db.Integer, nullable=False)
    porcentaje_calculo = db.Column(db.Float, default=25.0, nullable=False)
    horas_limite = db.Column(db.Float, nullable=False)
    horas_llevo = db.Column(db.Integer, default=0, nullable=False)

    @property
    def horas_restantes(self):
        rest = self.horas_limite - self.horas_llevo
        return max(0.0, round(rest, 1))

    @property
    def porcentaje_consumido(self):
        if not self.horas_limite or self.horas_limite <= 0:
            return 0.0
        return min(100.0, round((self.horas_llevo / self.horas_limite) * 100.0, 1))

    @property
    def estado_riesgo(self):
        pct = self.porcentaje_consumido
        if pct >= 80.0:
            return 'danger'
        elif pct >= 50.0:
            return 'warning'
        return 'safe'
