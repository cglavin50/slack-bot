FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt --no-cache-dir
# saves us the need for a virtualenv

COPY . .
# copy everything else over into code subdirectory

# CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]
# test if can run without module mode