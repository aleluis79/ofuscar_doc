FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos de requerimientos (si existen)
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Descargar el modelo de spaCy necesario para scrubadub_spacy
RUN python -m spacy download en_core_web_trf

# Verificar que el modelo se puede cargar correctamente
RUN python -c "import spacy; spacy.load('en_core_web_trf')"

# Copiar el código fuente
COPY . .

# Exponer el puerto por defecto de Uvicorn
EXPOSE 8000

# Comando para ejecutar la API con Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
