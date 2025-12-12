from app import app, db, Asignatura

PORCENTAJE_LIMITE = 0.25

DATOS_ASIGNATURAS = [
    # --- PRIMERO DE DAM ---
    {"nombre": "Lenguajes de Marca", "horas": 116, "curso": 1},
    {"nombre": "Sistemas Informaticos", "horas": 163, "curso": 1},
    {"nombre": "Base de Datos", "horas": 163, "curso": 1},
    {"nombre": "Programacion", "horas": 186, "curso": 1},
    {"nombre": "Entorno de Desarrollo", "horas": 81, "curso": 1},
    {"nombre": "Ingles Tecnico", "horas": 60, "curso": 1},
    {"nombre": "Digitalizacion", "horas": 50, "curso": 1},
    {"nombre": "Sostenibilidad", "horas": 40, "curso": 1},
    #{"nombre": "Itinerario I", "horas": 80, "curso": 1},
    {"nombre": "Proyecto I", "horas": 22, "curso": 1},

    # --- SEGUNDO DE DAM ---
    {"nombre": "Acceso a Datos", "horas": 233, "curso": 2},
    {"nombre": "Desarrollo de Interfaces", "horas": 233, "curso": 2},
    {"nombre": "Programacion Multimedia", "horas": 158, "curso": 2},
    {"nombre": "Programacion Servicios y Procesos", "horas": 84, "curso": 2},
    {"nombre": "Sistemas de Gestion", "horas": 158, "curso": 2},
    {"nombre": "Optatividad", "horas": 80, "curso": 2},
    #{"nombre": "Itinerario II", "horas": 60, "curso": 2},
    {"nombre": "Proyecto II", "horas": 22, "curso": 2},
]

def cargar_datos():
    with app.app_context():
        print(f"Ingresando los datos...")
        
        for dato in DATOS_ASIGNATURAS:
            nombre = dato["nombre"]
            horas_totales = dato["horas"]
            curso = dato["curso"]
            
            horas_limite = int(horas_totales * PORCENTAJE_LIMITE)
            
            asig = Asignatura.query.filter_by(nombre=nombre).first()
            
            if asig:
                if asig.horas_totales != horas_totales or asig.horas_limite != horas_limite:
                    asig.horas_totales = horas_totales
                    asig.horas_limite = horas_limite
                    asig.curso = curso
                    print(f"> Actualizado (DAM {curso}): {nombre}")
                else:
                    print(f"✔ Sin cambios: {nombre}")
            else:
                nueva = Asignatura(
                    nombre=nombre, 
                    horas_totales=horas_totales, 
                    horas_limite=horas_limite, 
                    horas_llevo=0,
                    curso=curso
                )
                db.session.add(nueva)
                print(f"✨ Creado (DAM {curso}): {nombre}")
        
        db.session.commit()
        print("🚀 Base de datos actualizada por cursos.")

if __name__ == "__main__":
    cargar_datos()