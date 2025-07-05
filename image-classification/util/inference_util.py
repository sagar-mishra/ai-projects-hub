import torch
import config
import numpy as np
import matplotlib.pyplot as plt

def load_model(model, model_weights) :
  
    model.load_state_dict(model_weights)
    for parameter in model.parameters():
        parameter.requires_grad = False

    model.eval()
    return model

def process_image(img, height, width):

    img = np.resize(img,(height,width,3))
    img = np.array(img)/255
    mean = np.array([0.5, 0.5, 0.5]) #provided mean
    std = np.array([0.5, 0.5, 0.5]) #provided std
    img = (img - mean)/std

    # Move color channels to first dimension as expected by PyTorch
    img = img.transpose((2, 0, 1))

    return img

def predict(model, image, idx_to_class, height, width):
    #process input image
    img = process_image(image, height, width)

    # change numpy array to PyTorch tensor
    img = torch.from_numpy(img).type(torch.FloatTensor)

    # Add batch of size 1 to image i.e we have (channel, widht,height) and we convert it to (batch_size, channel, width , height) i.e (1, channel, width, height)
    img.unsqueeze_(0)

    outputs = model(img)
    _, preds = torch.max(outputs, 1)

    class_id = preds.item()
    class_name = idx_to_class[class_id]

    return class_name


def calculate_accuracy(model, data_loader, dataset_sizes, device=config.TRAIN_DEVICE):

    model.to(device)

    original_classes = []
    predicted_classes = []
    current_corrects = 0
    with torch.no_grad():

        for inputs, labels in data_loader:
            inputs = inputs.to(device)
            labels = labels.to(device)

            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)

            original_classes.extend(labels.tolist())
            predicted_classes.extend(preds.tolist())
            current_corrects += torch.sum(preds == labels.data)

    accuracy = 100*(current_corrects/dataset_sizes["test"])

    return accuracy, original_classes, predicted_classes