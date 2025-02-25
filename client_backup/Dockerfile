FROM python:3.9

WORKDIR /app

# Install system dependencies for pdfkit
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
COPY .env .

# Install Python dependencies
RUN pip install -r requirements.txt
RUN pip install pdfkit

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]