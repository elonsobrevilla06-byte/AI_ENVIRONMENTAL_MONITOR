
import torch
import torch.nn as nn
from torchvision import transforms, models
import os


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


transform = transforms.Compose([
    transforms.Resize((64, 64)), 
    transforms.CenterCrop(64), 
    transforms.ToTensor(), 
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])


model = models.resnet18(weights=None)
model.fc = nn.Linear(model.fc.in_features, 5)


model_path = "train_ai_model/torch_model_2.pth"
if os.path.exists(model_path):
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()
else:
    print(f"Warning: Model file not found at {model_path}")