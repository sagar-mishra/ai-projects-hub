# covid-detection

## Table of contents
* [General info](#general-info)
* [Data Sources](#data-sources)
* [Technologies](#technologies)
* [Setup](#setup)
* [Running](#running)
* [Sample Cases](#sample-cases)
* [Kubernetes Deployment](#kubernetes-deployment)

## General info
Covid detection using CNN deep learning architecture, here we are considering two classes i.e Covid and Normal therefore it is a binary image classification problem. This is a simple project to learn deployment techniques (docker, kubernetes). It is not recommended to deploy on real time environment.

## Data Sources 
Covid data : https://github.com/ieee8023/covid-chestxray-dataset <br/>
Normal data : https://www.kaggle.com/paultimothymooney/chest-xray-pneumonia <br/>


## Technologies
* PyTorch
* Python
* Flask

## Setup

### Installation 
* pip install requirements.txt

## Running

* Pull the docker image from docker hub : <br/>
docker pull mishrasagar25/covid-detection-api:latest

* Then use docker run command to create a container : <br/>
docker run -p 5000:5000 -ti mishrasagar25/covid-detection-api /bin/bash

* Now open postman to hit flask API:
Use this end point for covid prediction : <br/>
http://localhost:5000/predict

NOTE : Use POST method and set content-type to multipart/form-data in header and in body select form-data and in key enter **image** and set type as file and then select file.


## Sample Cases

* Covid detected patient case : 
![Covid example](resources/images/covid_example.PNG)

* Normal patient case : 
![Normal example](resources/images/normal_example.PNG)


## Kubernetes Deployment

I have also deployed this project on **Google Kubernetes Engine** .

**Steps for Kubernetes deployment**

1. Create new project in GCP console: <br/>
   Sign in to your GCP console --> click on IAM & Admin --> click on Manage Resources --> click on CREATE PROJECT
  
2. Push our docker image to GCP container registry: <br/>
  
    1. Enable container registry : <br/>
      click on container --> Images
      
    2. Authenticate to container registry : Run following command in terminal <br/>
      gcloud auth configure-docker
      
    3. Tag our docker image : For this we need project ID which we have created in GCP, you will directly get this by click on project on dashboard <br/>
      docker tag mishrasagar25/covid-detection-api gcr.io/{PROJECT-ID}/mishrasagar25/covid-detection-api:latest
      
    4. Push docker image to GCP Container Registry using tag name : <br/>
      docker push gcr.io/{PROJECT-ID}/mishrasagar25/covid-detection-api:latest
      
3. Create Cluster : <br />
  
    1. Set your project ID and Compute Engine zone options for the gcloud tool : <br/>
       gcloud config set project $PROJECT_ID  <br/>
       gcloud config set compute/zone us-central1
       
    2. Create a cluster by executing the following command : <br/>
       gcloud container clusters create covid-detection-cluster --num-nodes=1
       
4. Deploy Application : <br/>
    
    1. Run following command to deploy application : <br/>
       kubectl create deployment covid-detection-app --image=gcr.io/{PROJECT-ID}/mishrasagar25/covid-detection-api:latest
      
    2. Run following command to expose our application(container) as a (load balanced) service to the outside world:<br/>
       kubectl expose deployment covid-detection-app --port 5000 --type=LoadBalancer
        
    3. Now our application is accessible to everyone, now to test this we need web IP adress, for this run following command:<br/>
       kubectl get service
       
       Now after running this you will see EXTERNAL-IP associated to our application, use this IP and port 5000 to test our application
      
      


