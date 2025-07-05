import argparse
import torch
import config
import os
import cv2
import sys
from models.base_conv_net_model import BaseConvNet
from util.inference_util import load_model, predict
from util.model_ready_data_creator import ModelReadyDataCreator

def main():
    parser = argparse.ArgumentParser(description='Covid Prediction')
    parser.add_argument("--image", help="Absolute path of image to predict", required=True)
    args = parser.parse_args()
    image_path = args.image

    if not os.path.exists(image_path):
        print("Provide the correct image path")
        sys.exit()

    inference(image_path)


def inference(image_path):
    
    current_model_weight_path = os.path.join(config.MODEL_PATH, config.MODEL_NAME)
    check_point_path = os.path.join(current_model_weight_path, config.CHECKPOINT_NAME)
    check_point = torch.load(check_point_path, map_location = torch.device(config.INFERENCE_DEVICE))
    model = BaseConvNet(num_classes=config.NUM_OF_CLASSES)
    model = load_model(model, check_point["state_dict"])
    class_to_idx = check_point["class_to_idx"]
    idx_to_class = check_point['idx_to_class']

    image = cv2.imread(image_path)

    prediction = predict(model, image, idx_to_class, height=config.IMAGE_SIZE[0], width=config.IMAGE_SIZE[1])

    print(f"Prediction : {prediction}")

if __name__ == "__main__":
    main()