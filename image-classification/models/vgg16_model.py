from torch import nn
from torchvision import models

class VGG16Model(nn.Module):

  def __init__(self, num_of_classes, model_name="vgg16"):
    super(VGG16Model, self).__init__()
    self.model_name = model_name
    if self.model_name == "vgg16":
      self.model = models.vgg16(pretrained=True)
    
    fc_inputs = self.model.classifier[6].in_features
    features = list(self.model.classifier.children())[:-1]
    features.extend([nn.Linear(fc_inputs, num_of_classes)])
    self.model.classifier = nn.Sequential(*features)
    
  def forward(self, x):
     return self.model(x)