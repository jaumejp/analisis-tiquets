import torch
import time
from ultralytics import YOLO

inici = time.time()

# Especifica CUDA
device = torch.device("cuda")

# Importa el modelo YOLO i crear una instància
model = YOLO('./models/raw/yolov8n.pt' ).to(device)

# Fine tuning amb les nostres dades
model.train(data='./models/config/config.yaml', epochs=18, batch=4, device=device)

# Calcular el temps d'entrenament
fi = time.time()
total = fi - inici
print("=====================================")
print("Entrenament acabat correctament.")
h = int(total // 3600)
m = int((total % 3600) // 60)
s = int(total % 60)
print()
print("=====================================")
print()
print(f"Temps total: {h}h - {m}min - {s}seg")

