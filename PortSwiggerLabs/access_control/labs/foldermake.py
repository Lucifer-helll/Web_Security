import os

for i in range(1, 14):
    folder_name = f"lab{i:02d}"
    os.makedirs(folder_name, exist_ok=True)
    print(f"Created: {folder_name}")
