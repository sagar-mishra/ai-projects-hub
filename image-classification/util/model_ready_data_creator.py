from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader
from torchvision.transforms import transforms, InterpolationMode

class ModelReadyDataCreator:

  def __init__(self, train_path, val_path, test_path, data_path=None, model_weights_path=None, project_path=None,height=224, width=224, batch_size=4):
    self.height = height
    self.width = width
    self.project_path = project_path
    self.data_path = data_path
    self.model_weights_path = model_weights_path
    self.batch_size = batch_size
    self.phases = ['train','val','test']
    self.dirs = {}
    for phase in self.phases:
        if phase == 'train':
            self. dirs[phase] = train_path
        elif phase == 'val' :
            self.dirs[phase] = val_path
        elif phase == 'test':
            self.dirs[phase] = test_path
    

    self.image_datasets = {phase : ImageFolder(self.dirs[phase], transform = self.get_transforms()) for phase in self.phases}

    self.data_loaders = {phase : DataLoader(self.image_datasets[phase], batch_size=self.batch_size, shuffle=True, num_workers=0) for phase in self.phases}

    self.dataset_sizes = {x : len(self.image_datasets[x]) for x in self.phases}

    self.class_names = self.image_datasets[self.phases[0]].classes

    self.num_of_classes = len(self.class_names)

    self.class_to_idx = self.image_datasets[self.phases[0]].class_to_idx

    self.idx_to_class = {val : key for key, val in self.class_to_idx.items()}

  def get_transforms(self, grayscale=False, interpolation_method=InterpolationMode.NEAREST):
    """
    function to return transforms object with all the transformations
    param 0 : resize height
    param 1 : resize width
    param 2 : grayscale image flag
    param 3 : Interpolation method used while resizing
    """

    transformation_list = []

    if grayscale : 
      transformation_list.append(transforms.Grayscale(1))

    transformation_list.append(transforms.Resize((self.height,self.width), interpolation=interpolation_method))
    transformation_list.append(transforms.RandomHorizontalFlip())
    transformation_list.append(transforms.ToTensor())

    if grayscale :
      transformation_list.append(transforms.Normalize(mean=[0.5], std=[0.5]))
    else:
      transformation_list.append(transforms.Normalize(mean=(0.5,0.5,0.5), std=(0.5,0.5,0.5)))
      
    return transforms.Compose(transformation_list)
