import subprocess
import os

# Étape 1: Exécuter pipreqs pour générer requirements.txt
subprocess.run(["../venv_claiton/bin/pipreqs", ".", "--force"])

# Étape 2: Modifier le fichier requirements.txt
modifications = [
    ('/^Pillow==10.0.0/d', 'requirements.txt'),
    ('/^pywinauto==/d', 'requirements.txt'),
    ('/^picamera==/d', 'requirements.txt'),
    ('/^pycuda==/d', 'requirements.txt'),
    ('s/^docx==.*/python-docx/', 'requirements.txt'),
    ('s/^pylink==.*/pylink-square/', 'requirements.txt'),
    ('/^pyppeteer==/d', 'requirements.txt'),
    ('s/^scikit-image0.0/scikit-image/', 'requirements.txt'),
    ('s/^skimage==0.0/scikit-image/', 'requirements.txt'),
]

for pattern, file_path in modifications:
    subprocess.run(["sed", "-i", pattern, file_path])

# Étape 3: Lire les requirements et les ajouter dans le setup.py
with open('requirements.txt', 'r') as f:
    requirements = [line.strip() for line in f.readlines()]

# Ajouter ces requirements dans le setup.py
setup_content = open('setup.py', 'r').read()
setup_content = setup_content.replace('install_requires=["numpy>=1.21.0"],', f'install_requires={requirements},')

with open('setup.py', 'w') as f:
    f.write(setup_content)

# Étape 4: Construire la wheel
subprocess.run(["python", "setup.py", "sdist", "bdist_wheel"])

print("Terminé!")