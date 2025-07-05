import os

TRAIN_DEVICE = "cuda"
INFERENCE_DEVICE = "cpu"
BATCH_SIZE = 2
EPOCHS = 50
BASE_PATH = "" # PATH where your all classification data present
DATA_PATH = os.path.join(BASE_PATH, "dataset") # PATH where we store train-val-test splitted data
TRAIN_PATH = os.path.join(DATA_PATH, "train")
VAL_PATH = os.path.join(DATA_PATH, "val")
TEST_PATH = os.path.join(DATA_PATH, "test")
MODEL_PATH = "trained_model_weights" # PATH where we store trained model weights
MODEL_NAME = "baseConvNet"
CHECKPOINT_NAME = "best_weight.tar"
NUM_OF_CLASSES = 7
IMAGE_SIZE = (512,512)