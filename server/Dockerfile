FROM python:3.12

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
COPY ./*.py /code
COPY ./model /code/model

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

#COPY . /code

CMD ["fastapi", "run", "main.py", "--port", "8000"]

# If running behind a proxy like Nginx or Traefik add --proxy-headers
# CMD ["fastapi", "run", "main.py", "--port", "8000", "--proxy-headers"]
