import logging

def actualizar_datos_desde_web(db, AsignaturaModel):
    logging.info("Iniciando scraping...")
    
    # 1. AQUÍ VA TU CÓDIGO DE SELENIUM (Loguearse, ir a la tabla)
    # datos_extraidos = {"PROG": 5, "BBDD": 2, ...}
    
    # DATOS DUMMY DE EJEMPLO (Borra esto cuando tengamos el scraper real)
    datos_extraidos = {
        "Programacion": 10,
        "Base de Datos": 4,
        "Lenguajes de Marca": 2
    }

    for nombre, faltas in datos_extraidos.items():
        asignatura = AsignaturaModel.query.filter_by(nombre=nombre).first()
        
        if asignatura:
            asignatura.horas_llevo = faltas
        else:
            nueva = AsignaturaModel(nombre=nombre, horas_totales=100, horas_limite=25, horas_llevo=faltas)
            db.session.add(nueva)
    
    db.session.commit()
    logging.info("Base de datos actualizada.")