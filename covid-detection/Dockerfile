FROM continuumio/anaconda3:latest

ENV COVID_DETECTION_SOURCE /usr/src/covid_detection

COPY . $COVID_DETECTION_SOURCE

WORKDIR $COVID_DETECTION_SOURCE/

EXPOSE 5000

RUN pip install -r $COVID_DETECTION_SOURCE/requirements.txt

ENTRYPOINT ["/usr/src/covid_detection/docker/entry_point.sh"] 

