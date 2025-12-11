from app import app, db, Asignatura

# --- CONFIGURACIÓN ---
PORCENTAJE_LIMITE = 0.25  # El 25% que me has dicho

# Diccionario simple: "Nombre": Horas_Totales_Curso
DATOS_ASIGNATURAS = {
    "Lenguajes de Marca": 116,
    "Sistemas Informaticos": 163,
    "Base de Datos": 163,
    "Programacion": 186,
    "Entornos de Desarrollos": 81,
    "Ingles": 60,
    "Digitalizacion": 50,
    "Sostenibilidad": 40,
    "Itinerario": 80,
    # 2º Curso
    "Acceso a Datos": 233,
    "Desarrollo de Inter": 233,
    "Programacion multimedia": 158,
    "Programacion de servicios": 84,
    "Sistemas de gestion": 158,
    "Itinerario II": 60,
    "Optativa": 80,
    "Proyecto": 55
}

def cargar_datos():
    with app.app_context():
        print(f"Calculando límites al {PORCENTAJE_LIMITE*100}%...")
        
        for nombre, horas_totales in DATOS_ASIGNATURAS.items():
            
            horas_limite = int(horas_totales * PORCENTAJE_LIMITE)
            
            # Buscamos si ya existe la asignatura
            asig = Asignatura.query.filter_by(nombre=nombre).first()
            
            if asig:
                # Actualizamos los valores
                if asig.horas_totales != horas_totales or asig.horas_limite != horas_limite:
                    asig.horas_totales = horas_totales
                    asig.horas_limite = horas_limite
                    print(f"🔄 Actualizado: {nombre} -> Total: {horas_totales}h | Límite: {horas_limite}h")
                else:
                    print(f"✔ Sin cambios: {nombre}")
            else:
                # Creamos desde cero
                nueva = Asignatura(
                    nombre=nombre, 
                    horas_totales=horas_totales, 
                    horas_limite=horas_limite, # Aquí guardamos el cálculo
                    horas_llevo=0
                )
                db.session.add(nueva)
                print(f"✨ Creado: {nombre}")
        
        db.session.commit()

if __name__ == "__main__":
    cargar_datos()