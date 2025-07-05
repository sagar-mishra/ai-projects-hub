import torch.nn as nn
import torch.nn.functional as F

class BaseConvNet(nn.Module):
    def __init__(self,model_name="baseConvNet", num_classes = 2):
        super().__init__()

        self.model_name = model_name
        self.num_classes = num_classes
        # output size of convolution filter
        # ((w-k+2p)/s) + 1  => w -> image size, k -> kernel, p -> padding, s -> stride
        
        # input_shape = (16, 3, 224, 224)
        self.conv11 = nn.Conv2d(in_channels=3,out_channels=32,kernel_size=3,stride=1,padding=1)
        self.bn11 = nn.BatchNorm2d(num_features=32)
        self.conv12 = nn.Conv2d(in_channels=32, out_channels=32,kernel_size=3,padding=1,stride=1)
        self.bn12 = nn.BatchNorm2d(num_features=32)
        self.conv13 = nn.Conv2d(in_channels=32,out_channels=32,kernel_size=5, stride=2)
        self.bn13 = nn.BatchNorm2d(num_features=32)
        self.dropout1 = nn.Dropout(p=0.4)

        self.conv21 = nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, stride=1, padding=1)
        self.bn21 = nn.BatchNorm2d(num_features=64)
        self.conv22 = nn.Conv2d(in_channels=64,out_channels=64,kernel_size=3,stride=1,padding=1)
        self.bn22 = nn.BatchNorm2d(num_features=64)
        self.conv23 = nn.Conv2d(in_channels=64, out_channels=64, kernel_size=5, stride=2)
        self.bn23 = nn.BatchNorm2d(num_features=64)
        self.dropout2 = nn.Dropout(p=0.4)

        self.flat = nn.Flatten()
        self.fc1 = nn.Linear(64*53*53, 128)
        self.bn31 = nn.BatchNorm1d(num_features=128)
        self.dropout3 = nn.Dropout(0.4)
        self.fc2 = nn.Linear(in_features=128,out_features=2)
        

    # Feed forward function
    def forward(self,image):
        bs, c, h, w = image.size()
        output = F.relu(self.bn11(self.conv11(image)))  # shape = (bs, 32, 224, 224)
        output = F.relu(self.bn12(self.conv12(output))) # shape = (bs, 32, 224, 224)
        output = F.relu(self.bn13(self.conv13(output))) # shape = (bs, 32, 110, 110)
        output = self.dropout1(output) # shape = (bs, 32, 110, 110)

        output = F.relu(self.bn21(self.conv21(output))) # shape = (bs, 64, 110, 110)
        output = F.relu(self.bn22(self.conv22(output))) # shape = (16, 64, 110, 110)
        output = F.relu(self.bn23(self.conv23(output))) # shape = (16, 64, 53, 53)
        output = self.dropout2(output) # shape = (16, 64, 53, 53)

        # output = self.flat(output)
        # or we can directly use output = nn.Flatten()(output)
        output = output.view(bs,-1) # shape = (bs, 179776)
        output = self.bn31(self.fc1(output)) # shape (bs, 128)
        output = self.dropout3(output) # shape (bs, 128)
        output = self.fc2(output) # shape (bs, 2)
        return output