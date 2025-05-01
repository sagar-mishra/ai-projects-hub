# LLM-OCR-SUMMARIZER App

## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup).
* [Directory Structure](#directory-structure)

## General info
This project leverages LLM models (llava, gemma3, llama3.2-vision) capabilities and Streamlit to create a 100% locally running computer vision app that can perform OCR, extract structured text from the image and summzarize extracted text.

## Technologies
* GenAI
* Natural languge processing(NLP)
* Python

## Setup
### Installation 
* Download and install Ollama from https://ollama.com/
* run commands: 
    ollama pull llama3.2-vision
    ollama pull llava
    ollama pull gemma3:4b
* pip install -r requirements.txt

## Directory structure
* app.py : contains complete application (ocr + summarizer with UI) code .
