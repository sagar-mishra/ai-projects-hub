from torch import nn
from torchvision import models

class InceptionV3(nn.Module):

  def __init__(self, num_of_classes, model_name="inception_v3"):
    super(InceptionV3, self).__init__()
    self.model_name = model_name
    if self.model_name == "inception_v3":
      self.model = models.inception_v3(pretrained=True)
    
    for param in self.model.parameters():
        param.requires_grad = False   

    fc_inputs = self.model.fc.in_features
    self.model.fc = nn.Sequential(
        nn.Linear(fc_inputs, 512),
        nn.ReLU(),
        nn.BatchNorm1d(512),
        nn.Dropout(0.4),
        nn.Linear(512, 256),
        nn.ReLU(),
        nn.BatchNorm1d(num_features=256),
        nn.Dropout(0.4),
        nn.Linear(256, 128),
        nn.ReLU(),
        nn.BatchNorm1d(num_features=128),
        nn.Dropout(0.4),
        nn.Linear(128, num_of_classes), 
    )
   
  def forward(self, x):
     return self.model(x)