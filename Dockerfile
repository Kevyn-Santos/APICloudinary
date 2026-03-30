FROM python:3.12-alpine3.22
LABEL authors="kevyn"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY ./UploadCode .

RUN adduser -D cloudinaryusr
USER cloudinaryusr

EXPOSE 8001

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "main:app"]