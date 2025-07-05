# Image-classifcation

## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)
* [Running](#running)

## General info
This project is a template for image classification. <br>
<p>This includes everything require for image classification like directory structure, training file, testing file and flask application, we just need to do some configuration changes in config.py and slight modifications in this project as per our requirement. </p>

## Technologies
* PyTorch
* Python
* Flask

## Setup

### Configuration 
* update config.py to do configuration

### Directory Structure
* models : All models present in this directory, as of now I have included one custom model(base_conv_net.py) and one transfer learning model(resnext_model.py).
* resources : resources like data, images can be placed in this directory
* trained_model_weights: Trained weights exported to this directory, inside this separate directories will create for each model
* util : utilities file present in this directory like engine.py, inference_util.py, visualization_util.py etc.
* notebooks : jupyter notebooks should place here.

### Installation 
* pip install requirements.txt


## Running

### Training
* To train a model use train.py file :  Do some changes like model, optimizer, scheduler as per your requirement. <br/>
    python train.py
    
### Testing
* To validate trained model on testing data use test.py file : here you just need to change model on which you are testing. <br/>
    python test.py
    
### Flask application
* To run this project as a flask application use app.py file : here you need to change model and write API as per your requirement.<br/>
    python app.py
    



