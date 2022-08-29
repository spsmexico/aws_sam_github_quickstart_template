import subprocess

subprocess.run(['git', 'init'])
subprocess.run(['git', 'add', '.'])
subprocess.run(['git', 'commit', '-m', '"Proyecto inicializado."'])
subprocess.run(['git', 'branch', '-M', 'main'])
subprocess.run(['git', 'remote', 'add', 'origin', 'https://github.com/{{cookiecutter.org_or_user_github}}/{{cookiecutter.nombre_repo}}.git'])
subprocess.run(['git', 'push', '-u', 'origin', 'main'])