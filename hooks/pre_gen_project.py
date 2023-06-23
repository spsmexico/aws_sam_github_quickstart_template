import subprocess

subprocess.run(['mkdir', '{{cookiecutter.nombre_repo}}'])
subprocess.run(['cd', '{{cookiecutter.nombre_repo}}'])