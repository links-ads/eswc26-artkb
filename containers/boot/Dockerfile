FROM python:3.10

WORKDIR /home

# Copy the current directory contents into the container at /app
COPY ./containers/boot/requirements.txt ./requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

ARG ENV_FILE
COPY ${ENV_FILE} .env

COPY ./containers/boot/configure.py ./configure.py
COPY ./containers/boot/repo-config.ttl ./repo-config.ttl

CMD ["python", "configure.py"]