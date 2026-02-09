import os

# Base folder
base_folder = "user_service"

# Folders to create inside user_service
folders = [
    base_folder,
    os.path.join(base_folder, "models"),
    os.path.join(base_folder, "schemas"),
    os.path.join(base_folder, "core"),
    os.path.join(base_folder, "dependencies"),
    os.path.join(base_folder, "alembic"),
]

# Create folders
for folder in folders:
    os.makedirs(folder, exist_ok=True)
    print(f"Created folder: {folder}")

print("\n✅ User Service folder structure created successfully!")
