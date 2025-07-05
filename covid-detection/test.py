import config
import os
import torch
from models.base_conv_net_model import BaseConvNet
from util.model_ready_data_creator import ModelReadyDataCreator
from util.inference_util import load_model, calculate_accuracy

def test():
    """
    function to calculate accuracy over test data
    """
    print("Calculating Accuracy...")
    # setting path for testing
    model_ready_data_creator = ModelReadyDataCreator(config.TEST_PATH, config.VAL_PATH, config.TEST_PATH, config.DATA_PATH, config.MODEL_PATH)
    current_model_weight_path = os.path.join(config.MODEL_PATH, config.MODEL_NAME)
    check_point_path = os.path.join(current_model_weight_path, config.CHECKPOINT_NAME)
    check_point = torch.load(check_point_path)
    
    model = BaseConvNet(num_classes=config.NUM_OF_CLASSES)
    model = model.to(config.TRAIN_DEVICE)
    model = load_model(model, check_point["state_dict"])
    class_to_idx = check_point["class_to_idx"]
    idx_to_class = check_point['idx_to_class']

    data_loader = model_ready_data_creator.data_loaders
    dataset_sizes = model_ready_data_creator.dataset_sizes
    accuracy, original_classes, predicted_classes = calculate_accuracy(model, data_loader['test'], dataset_sizes, device=config.TRAIN_DEVICE)

    print(f"Test accuracy : {accuracy}")


if __name__ == "__main__":
    test()