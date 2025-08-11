# Usa una imagen ligera de Python
FROM python:3.10-slim

# Configura el directorio de trabajo
WORKDIR /app

# Copia los archivos necesarios
COPY . .

# Instala dependencias
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -e './google-analytics-mcp[dev]'


# Comando de arranque
CMD ["python", "main.py"]

