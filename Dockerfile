FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn==23.0.0
COPY core.py quantum.py app.py ./
COPY models/ ./models/
COPY reports/ ./reports/
COPY templates/ ./templates/
COPY static/ ./static/
RUN useradd --uid 10001 --create-home labuser
USER 10001:10001
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "2", "--timeout", "120", "--worker-tmp-dir", "/tmp", "app:app"]
