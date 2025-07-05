# effective-date-parser

## Table of contents
* [General info](#general-info)
* [Data Sources](#data-sources)
* [Technologies](#technologies)
* [Setup](#setup)
* [Directory Structure](#directory-structure)
* [Model Training Steps](#model-training-steps)

## General info
Effective Date parser is a natural languaage processing based project. In this project we need to extract effective date from contracts. To solve this problem I have used QuestionAnsweringModel https://simpletransformers.ai/docs/qa-model/ of Simple Transformers https://simpletransformers.ai/

## Data Sources 
https://drive.google.com/file/d/10j02yfn14_p3E67yEhb5EIAb4kRrumU8/view?usp=sharing

## Technologies
* Python
* PyTorch
* Deep learning
* SimpleTransformers

## Setup

### Installation 
* pip install requirements.txt

## Directory structure
* config.py : contains all the configurations, you need to change directory paths and model_name and model_type if you wants to.
* util :
   * data_creator.py : Create train, eval and test data which can be passed to simple transformers QuestionAnsweringModel
   * model_output_post_processing.py : post process model prediction to get final output values
* notebooks :
   * training.ipynb : I have trained model over google colab, you can use same notebook just some directory structure needs to be changed.


## Model Training steps 
* Update configurations like directory paths and model details in config.py
* Create data which can be passed to QuestionAnsweringModel by running python file util/data_creator.py
* Train model over google colab using notebooks/training.ipynb
* Post process model predictions to generate final output

