FROM python:3.11-slim

# Install ADB
RUN apt-get update && apt-get install -y android-tools-adb

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .

CMD ["python", "app.py"]