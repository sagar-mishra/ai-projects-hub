from torch import nn
from torchvision import models

class ResNextModel(nn.Module):

  def __init__(self, num_of_classes, model_name="resnext50_32x4d"):
    super(ResNextModel, self).__init__()
    self.model_name = model_name
    if self.model_name == "resnext50_32x4d":
      self.model = models.resnext50_32x4d(pretrained=True)
    
    self.num_output_features = num_of_classes
    self.num_input_features = self.model.fc.in_features
    self.model.fc = nn.Linear(self.num_input_features, self.num_output_features)

  def forward(self, x):
     return self.model(x)