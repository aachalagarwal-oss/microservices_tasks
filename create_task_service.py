import os

# Base folder

base_folder = "task_service"

# Folders inside task_service

folders = [
base_folder,
os.path.join(base_folder, "models"),
os.path.join(base_folder, "schemas"),
os.path.join(base_folder, "routers"),
os.path.join(base_folder, "services"),
os.path.join(base_folder, "core"),
os.path.join(base_folder, "dependencies"),
os.path.join(base_folder, "alembic"),
os.path.join(base_folder, "alembic", "versions"),
os.path.join(base_folder, "tests"),
]

# Create folders

for folder in folders:
    os.makedirs(folder, exist_ok=True)
    print(f"Created folder: {folder}")

# Create **init**.py in each python package

for folder in folders:
    if "alembic" not in folder and "tests" not in folder:
        init_file = os.path.join(folder, "__init__.py")
        open(init_file, "a").close()

print("\n✅ Task Service folder structure created successfully!")
