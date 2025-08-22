FROM python:3.10-slim

# Instalar dependencias del sistema en una sola capa
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar solo requirements para aprovechar cache
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

# Copiar todo el código fuente
COPY . .
RUN pip install -e './google-analytics-mcp[dev]'

# Copiar el código principal
COPY main.py .

# Comando por defecto
CMD ["python", "main.py"]
