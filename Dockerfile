FROM python:3.12-slim

WORKDIR /app


COPY requirements.txt .
RUN pip install --upgrade pip --disable-pip-version-check && \
    pip install --no-cache-dir -r requirements.txt

COPY . .


CMD ["python", "-m", "src.main"]