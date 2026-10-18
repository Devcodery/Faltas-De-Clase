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

# Exponemos el puerto
EXPOSE 5000

# Ejecutamos la app con Gunicorn (servidor WSGI de producción)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]