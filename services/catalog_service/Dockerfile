FROM python:3.14-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /service
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd --create-home appuser && chown -R appuser:appuser /service
USER appuser
EXPOSE 5000
CMD ["flask", "--app", "app:app", "run", "--host=0.0.0.0", "--port=5000"]
