# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory in the container
WORKDIR /mindcare

# Copy the local requirements file to the container
COPY requirements.txt .
# RUN apt-get update && apt-get install -y tmux   # Install tmux
RUN pip install --no-cache-dir --upgrade setuptools wheel
RUN pip install --no-cache-dir celery==5.3.6
RUN pip install django
RUN python -m pip install --upgrade pip==21.3.1
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install agora-token-builder
COPY . /mindcare/
EXPOSE 80

# Define environment variable
ENV NAME World

# Start a new tmux session and run Django and Celery
CMD ["bash", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:80 & celery -A mindcare.celery worker --pool=solo -l info"]