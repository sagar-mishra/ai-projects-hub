import numpy as np
import config
import os
import torch
import cv2
from PIL import Image
from models.base_conv_net_model import BaseConvNet
from util.inference_util import load_model, predict
from flask import Flask
from flask import request
from flask import jsonify

app = Flask(__name__)

Model = None
IDX_TO_CLASS = None
CLASS_TO_IDX = None
Device = config.INFERENCE_DEVICE

@app.route("/")
def welcome():
    return "hello"

@app.route("/predict", methods=["POST"])
def do_prediction():
    image_path = request.files['image']

    image = Image.open(image_path.stream)
    opencvImage = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    if opencvImage is None : 
        response_data = {
            "message" : "Provide valid image path"
        }
        status_code = 400
    else:
        prediction = predict(MODEL, image, IDX_TO_CLASS, height=config.IMAGE_SIZE[0], width=config.IMAGE_SIZE[1])
        response_data = {
            "message" : prediction
        }
        status_code = 200
    return jsonify(response_data), status_code

if __name__ == "__main__":

    current_model_weight_path = os.path.join(config.MODEL_PATH, config.MODEL_NAME)
    check_point_path = os.path.join(current_model_weight_path, config.CHECKPOINT_NAME)
    check_point = torch.load(check_point_path, map_location = torch.device(config.INFERENCE_DEVICE))
    model = BaseConvNet(num_classes=config.NUM_OF_CLASSES)
    MODEL = load_model(model, check_point["state_dict"])
    CLASS_TO_IDX = check_point["class_to_idx"]
    IDX_TO_CLASS = check_point['idx_to_class']

    app.run(host='0.0.0.0', port=5000)