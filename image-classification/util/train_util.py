import torch
import torch.nn as nn

loss_function = nn.CrossEntropyLoss()

def train_loop(model, data_loader, optimizer, loss_function, scheduler = None,device=torch.device("cuda")):
    """
    function to train model
    :param model : model to train
    :data_loader : data_loader of training phase
    :scheduler : scheduler
    :loss_function : loss function
    :device : device on which we need to train
    :return: tuple(running loss, current currect prediction)
    """
    print('Train mode')
    # set training mode : It changed the behaviour of some layers like batch normalization use batch data not saved statistics(it happens in val & test phase), droupout is enabled
    model.train()

    current_loss = 0.0
    current_corrects = 0

    # The torch.set_grad_enabled line of code makes sure to clear the intermediate values for evaluation, which are needed to backpropagate during training
    with torch.set_grad_enabled(True):

        # print("Iterating through data")
        for inputs, labels in data_loader :
            # moving the inputs and labels to device passed in function
            inputs = inputs.to(device)
            labels = labels.to(device)

            # setting zero to all gradients before gradient calculation/backpropogation
            optimizer.zero_grad() 

            outputs = model(inputs)
            max_element,preds = torch.max(outputs,1)
            loss = loss_function(outputs, labels)

            # Do backpropagation/calculate gradient
            # Backward pass: compute gradient of the loss with respect to model
            loss.backward()

            # update weights/parameters
            optimizer.step()

            # if we have a scheduler, you either need to step it here or you have to step it after the epoch
            # If you don’t call it, the learning rate won’t be changed and stays at the initial value.
            # should call scheduler.step() after the optimizer.step() 
            # we will be stepping it after epoch using val loss
            # if scheduler:
            #     scheduler.step()

            # It's because the loss given by CrossEntropy or other loss functions is divided by the number of elements i.e. the reduction parameter is mean by default. 
            # torch.nn.CrossEntropyLoss(weight=None, size_average=None, ignore_index=-100, reduce=None, reduction='mean')
            # Hence, loss.item() contains the loss of entire mini-batch, but divided by the batch size. That's why loss.item() is multiplied with batch size, given by inputs.size(0), while calculating running_loss.
            # here we'll get mean of loss of entire batch using loss.item() that's why we are multiplying it with batch_ size to get current loss.
            current_loss += loss.item() * inputs.size(0)
            current_corrects += torch.sum(preds == labels.data)

    return current_loss, current_corrects


def eval_loop(model, data_loader, loss_function, device=torch.device("cuda")):
    """
    function to validate model
    :param model : model to train
    :data_loader : data_loader of training phase
    :scheduler : scheduler
    :loss_function : loss function
    :device : device on which we need to train
    :return: tuple(running loss, current currect prediction)
    """
    print('Validation mode')
    # dropout is disabled and so is replaced with a no op. Similarly, bn should use saved statistics instead of batch data 
    model.eval()

    current_loss = 0.0
    current_corrects = 0

    final_targets = []
    final_outputs = []    

    # impacts the autograd engine and deactivate it. It will reduce memory usage and speed up computations but you won’t be able to backprop (which you don’t want in an eval script).
    # it is same as with torch.set_grad_enabled(False):
    with torch.no_grad():

        # print("Iterating through data")
        for inputs, labels in data_loader :

            # moving the inputs and labels to device passed in function
            inputs = inputs.to(device)
            labels = labels.to(device)

            outputs = model(inputs)
            _,preds = torch.max(outputs,1)
            loss = loss_function(outputs, labels)

            current_loss += loss.item() * inputs.size(0)
            current_corrects += torch.sum(preds == labels.data)

            # convert targets and outputs to lists
            labels = labels.detach().cpu().numpy().tolist()
            preds = preds.detach().cpu().numpy().tolist()
            
            # extend the original list
            final_targets.extend(labels)
            final_outputs.extend(preds)

    return current_loss, current_corrects, final_targets, final_outputs


