import pickle
import time
import os
import copy
import torch
import config
import pickle
import torch.optim as optim
import torch.nn as nn
from models.resnext_model import ResNextModel
from sklearn import metrics
from util.train_util import train_loop,eval_loop,loss_function
from util.model_ready_data_creator import ModelReadyDataCreator
from util.early_stopping import EarlyStopping
from util.scheduler import LRScheduler


def training(model, loss_function, optimizer, model_ready_data_creator, scheduler=None, early_stopping = None, num_epochs = 50, start_epoch = 1):

    since = time.time()
    data_loader = model_ready_data_creator.data_loaders
    dataset_sizes = model_ready_data_creator.dataset_sizes
    model_weights_path = model_ready_data_creator.model_weights_path
    idx_to_class = model_ready_data_creator.idx_to_class
    class_to_idx = model_ready_data_creator.class_to_idx

    current_model_weight_path = os.path.join(model_weights_path, model.model_name)
    if not os.path.exists(current_model_weight_path):
        os.mkdir(current_model_weight_path)

    train_loss_values = []
    val_loss_values = []

    train_accuracy_values = []
    val_accuracy_values = []

    best_model_weights = copy.deepcopy(model.state_dict())
    best_acc = 0.0

    for epoch in range(start_epoch, num_epochs+1) : 
        print('Epoch {}/{}'.format(epoch,num_epochs))
        print('-'*100)

        train_loss, train_corrects = train_loop(model, data_loader['train'], optimizer, loss_function, scheduler, config.TRAIN_DEVICE)

        # here we are taking running loss and divide it by whole dataset_size to get the average/mean loss
        train_epoch_loss = train_loss/dataset_sizes['train']
        # calculating accuracy by dividing total_corrects/dataset_size
        train_epoch_accuracy = 100* (train_corrects.double()/dataset_sizes['train'])
        print(f'Loss: {train_epoch_loss:.4f} Accuracy : {train_epoch_accuracy:.4f}')
        print('-'*50)

        train_loss_values.append(train_epoch_loss)
        train_accuracy_values.append(train_epoch_accuracy)

        validation_loss, validation_corrects, valid_targets, predictions = eval_loop(model, data_loader['val'], loss_function, config.TRAIN_DEVICE)
        validation_epoch_loss = validation_loss/dataset_sizes['val']
        validation_epoch_accuracy = 100*(validation_corrects.double()/dataset_sizes['val'])
        
        print(f'Loss : {validation_epoch_loss:.4f} Accuracy : {validation_epoch_accuracy:.4f}')

        val_loss_values.append(validation_epoch_loss)
        val_accuracy_values.append(validation_epoch_accuracy)

        if scheduler:
            scheduler(validation_epoch_loss)

        if early_stopping:
            early_stopping(validation_epoch_loss)
            if early_stopping.early_stop:
                best_model_weights = copy.deepcopy(model.state_dict())
                break

        if validation_epoch_accuracy > best_acc : 
            best_model_weights = copy.deepcopy(model.state_dict())
            best_acc = validation_epoch_accuracy
            print(f'Saving weights for {epoch} epoch')
            checkpoint_name = f"weight_{epoch}.tar"
            PATH = os.path.join(current_model_weight_path, checkpoint_name)
            torch.save({'state_dict': model.state_dict(),
                        'class_to_idx': class_to_idx,
                        'idx_to_class': idx_to_class
                        }, 
                        PATH)
            
        print()

    checkpoint_name = f"best_weight.tar"
    PATH = os.path.join(current_model_weight_path, checkpoint_name)
    torch.save({'state_dict': best_model_weights,   
                'class_to_idx': class_to_idx,
                'idx_to_class': idx_to_class
                }, 
                PATH)

    time_since = time.time() - since
    print(f'Training complete in {time_since // 60:.0f}m {time_since % 60:.0f}s')
    print(f'Best validation Accuracy: {best_acc:4f}')
    # Now we'll load in the best model weights and return it
    model.load_state_dict(best_model_weights)
    return model, train_loss_values, train_accuracy_values, val_loss_values, val_accuracy_values

def train():
    model_ready_data_creator = ModelReadyDataCreator(config.TRAIN_PATH, config.VAL_PATH, config.TEST_PATH, config.DATA_PATH, config.MODEL_PATH, height=config.IMAGE_SIZE[0], width=config.IMAGE_SIZE[1], batch_size=config.BATCH_SIZE)
    files = os.listdir(config.TRAIN_PATH)
    
    model = ResNextModel(num_of_classes=config.NUM_OF_CLASSES)
    model = model.to(config.TRAIN_DEVICE)

    
    num_steps = len(model_ready_data_creator.data_loaders['train'])

    lr = 1e-4
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    # reduce learning rate when we reach a plateau on loss
    scheduler = LRScheduler(optimizer)
    
    early_stopping = EarlyStopping(patience=5)

    # one_cycle_scheduler = OneCycleLR(optimizer, max_lr=lr, epochs=config.EPOCHS, steps_per_epoch=num_steps)
    
    best_model, train_loss_values, train_accuracy_values, val_loss_values, val_accuracy_values = training(model, loss_function, optimizer, model_ready_data_creator, scheduler=scheduler, early_stopping = early_stopping, num_epochs = config.EPOCHS)
    model_loss_acc = {
        "train_loss_values" : train_loss_values,
        "train_accuracy_values" : train_accuracy_values,
        "val_loss_values" : val_loss_values,
        "val_accuracy_values" : val_accuracy_values
    }
    model_loss_acc_file = open("resources/model_loss_acc_file.pickle","wb")
    pickle.dump(model_loss_acc, model_loss_acc_file)

if __name__ == "__main__":
    train()