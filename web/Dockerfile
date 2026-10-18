# Usamos una imagen base de Python oficial ligera
FROM python:3.9-slim

# Instalamos solo lo necesario para PostgreSQL
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Directorio de trabajo
WORKDIR /app

# Copiamos requerimientos e instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código
COPY . .

# Variables de entorno para Python y logs en tiempo real sin buffer
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Exponemos el puerto
EXPOSE 5000

# Ejecutamos la app con Gunicorn (con logs de acceso y errores dirigidos a stdout/stderr para Docker/Portainer)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--access-logfile", "-", "--error-logfile", "-", "--capture-output", "--enable-stdio-inheritance", "app:app"]