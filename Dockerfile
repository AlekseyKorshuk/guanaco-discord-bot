FROM selenium/standalone-chrome

ARG GIT_TOKEN
ARG GIT_USERNAME

USER root

RUN apt update && \
    apt-get install -y python3-pip git && \
    apt-get install -y software-properties-common && \
    apt-add-repository ppa:git-core/ppa && \
    apt-get update && \
    apt-get install -y git-lfs

# Initialize Git LFS
RUN git lfs install

COPY . /app
WORKDIR /app

RUN git clone https://${GIT_USERNAME}:${GIT_TOKEN}@gitlab.com/c2480/chai_guanaco.git
RUN python3 -m pip install -r ./chai_guanaco/guanaco_services/requirements.txt

RUN python3 -m pip install -r requirements.txt


ENV PYTHONPATH "${PYTHONPATH}:/app/chai_guanaco/guanaco_database/src"

CMD python3 bot.py
