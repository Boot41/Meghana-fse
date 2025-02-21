FROM python:3.9

WORKDIR /app

COPY requirements.txt .
COPY .env .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

# Create a script to run migrations and start server
RUN echo '#!/bin/bash\n\
set -ex\n\
echo "Current directory:"\n\
pwd\n\
echo "Directory contents:"\n\
ls -la\n\
echo "Making migrations..."\n\
python manage.py makemigrations core\n\
echo "Running migrations..."\n\
python manage.py migrate\n\
echo "Starting server with gunicorn..."\n\
exec gunicorn myproject.wsgi:application --bind 0.0.0.0:8000 --log-level debug\n'\
> /app/start.sh

RUN chmod +x /app/start.sh

CMD ["/bin/bash", "/app/start.sh"]