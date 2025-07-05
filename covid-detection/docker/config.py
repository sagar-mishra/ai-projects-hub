import os

TRAIN_DEVICE = "cuda"
INFERENCE_DEVICE = "cpu"
BATCH_SIZE = 16
EPOCHS = 50
BASE_PATH = "/usr/src/covid_detection"
DATA_PATH = os.path.join(BASE_PATH, "dataset")
TRAIN_PATH = os.path.join(DATA_PATH, "train")
VAL_PATH = os.path.join(DATA_PATH, "val")
TEST_PATH = os.path.join(DATA_PATH, "test")
MODEL_PATH = "/usr/src/covid_detection/trained_model_weights"
MODEL_NAME = "baseConvNet"
CHECKPOINT_NAME = "best_weight.tar"
NUM_OF_CLASSES = 2
IMAGE_SIZE = (224,224)