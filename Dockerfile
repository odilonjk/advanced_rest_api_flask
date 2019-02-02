FROM python:3.7-alpine
COPY . /app
WORKDIR /app
RUN pip install pipenv
RUN pipenv install
CMD ["gunicorn", "-b 0.0.0.0:8000", "-w 4", "main:app"]