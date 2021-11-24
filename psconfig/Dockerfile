FROM python:3.10

RUN apt update

RUN apt -y install nano

RUN mkdir /code

WORKDIR /code/app

RUN wget http://ftp.us.debian.org/debian/pool/main/libs/libseccomp/libseccomp2_2.5.1-1_armhf.deb

RUN dpkg -i libseccomp2_2.5.1-1_armhf.deb

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY /app /code

VOLUME /hostpipe

#CMD [./code/app/flask.sh]
ENTRYPOINT ["tail", "-f", "/dev/null"]
#ENTRYPOINT ["/code/app/flask.sh"]