# Gunakan image Python sebagai base image
FROM python:3.12-slim

# Set working directory di dalam container
WORKDIR /app

# Salin requirements.txt dan install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua file Python ke dalam container
COPY . .

# Perintah untuk menjalankan aplikasi
CMD ["python", "main.py"]
