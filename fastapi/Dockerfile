FROM python:3.10

RUN apt update

RUN apt -y install nano

RUN apt -y install sqlite3

WORKDIR /code

RUN wget http://ftp.us.debian.org/debian/pool/main/libs/libseccomp/libseccomp2_2.5.1-1_armhf.deb

RUN dpkg -i libseccomp2_2.5.1-1_armhf.deb

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
