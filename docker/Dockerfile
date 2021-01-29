FROM python:3.7.5-buster

# Install python dependencies
RUN apt-get update && apt-get -y install sudo
RUN sudo apt-get -y install libspatialindex-dev
RUN sudo apt-get -y install sox
RUN apt-get update && apt-get -y install ffmpeg
COPY app/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN mkdir home/app
WORKDIR home/app
COPY app .

EXPOSE 5001
# EXPOSE 5555