# Usa una imagen base de Python oficial, que es ligera y adecuada
FROM python:3.11-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de requisitos
COPY requirements.txt /app

# Instala las dependencias del proyecto, incluyendo gunicorn
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copia el archivo de requisitos
COPY requirements.txt /app

#EXPOSE 8000
#CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]

# Define la variable de entorno para el puerto
ENV PORT 8000

# Expone el puerto que la aplicación Gunicorn usará
EXPOSE $PORT

# Comando por defecto para iniciar el servidor de Gunicorn
# Cambia `nombre_proyecto` por el nombre de tu proyecto principal de Django
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "core.wsgi:application"]
