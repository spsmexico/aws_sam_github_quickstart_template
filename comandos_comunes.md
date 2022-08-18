# SAM CLI

## Inicializar proyecto de SAM:

```bash
sam init
```

## Construir aplicación:

Usando Docker (No requiere que tengas Python instalado)

```bash
sam build --use-container
```

Usando Docker y una imagen en especifico (No requiere que tengas Python instalado)

```bash
sam build --use-container --build-image public.ecr.aws/sam/build-python3.8:1.32.0
```

## Generar un evento de ejemplo:

Si necesitas ver un ejemplo de la estructura del evento que recibe tu lambda puede utilizar estos comandos.

- Para SQS
  
  ```bash
  sam local generate-event sqs receive-message
  ```

- API Gateway:

```bash
sam local generate-event apigateway aws-proxy --method GET --path document --body "{"test": "1", "tests2": "2"}"
```

Para visualizar la lista de servicios de los que se pueden generar eventos favor de visitar: [sam local generate-event - AWS Serverless Application Model](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-local-generate-event.html)

## Desplegar API en ambiente local (localhost:3000):

```bash
sam local start-api
```

## Invocar lambda local:

Si necesitas validar el funcionamiento de tu lambda puede pasarle un evento en formato json si necesidad de desplegar. (Requiere Docker instalado)

```bash
sam local invoke -e events/event.json
```

Para mayor información de comandos de CLI de SAM: [AWS SAM CLI command reference - AWS Serverless Application Model](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-command-reference.html)

-----------------------------------------------

# Github CLI

## Autenticarse en cuenta Github:

```bash
gh auth login
```

## Configurar editor:

```bash
gh config set editor
```

Para VS Code

```bash
gh config set editor "code --wait"
```

## Crear nuevo Pull Request (PR):

```bash
gh pr create
```

## Crear nuevo PR como draft:

```bash
gh pr create -d
```

## Marcar PR como listo:

```bash
gh pr ready <# de PR>
```

## Regresar PR de listo a draft:

Instalamos la extensión:

```bash
gh extension install kyanny/gh-pr-draft
```

Una vez instala podemos ejecutar:

```bash
gh pr-draft <# de PR>
```

## Editar PR:

```bash
gh pr edit <# de PR>
```

## Listar PR's:

```bash
gh pr list
```

## Listar workflows:

```bash
gh workflow list
```

## Listar workflows en ejecución:

```bash
gh run list
```

Para mayor información de comandos del CLI de Github visitar: [Manual | GitHub CLI](https://cli.github.com/manual/)

---

# Commitizen

## Commit:

```bash
cz c
```

## Reintentar commit:

```bash
cz c --retry
```

---

# Git

## Configurar usuario para repo local:

Si quieres configurar el usuario y correo que aparecen al crear un commit, debes dirigirte a la carpeta del repositorio que quieres configurar y ejecutar lo siguiente:

```bash
git config --local user.name "user_name"
git config --local user.email "user_email@mail.com"
```

## Editar mensaje de commit anterior:

Siempre y cuando no se le haya hecho push.

```bash
git commit --amend -m "an updated commit message"
```

Si ya se hizo push se puede hacer un --force, pero solo si eres la única persona colaborando en esa rama. No se pueden editar los mensajes de la rama protegidas como develop.

## Cambiarnos de rama:

```bash
git checkout <nombre-de-rama>
```

## Crear nueva rama basada en una existente:

Primero es necesario estar en la rama a clonar. Después usar comando:

```bash
git checkout -b <nombre-de-la-nueva-rama>
```

## Crear nueva rama basada en una existente:

Primero es necesario estar en la rama a clonar. Después usar comando:

```bash
git checkout -b <nombre-de-la-nueva-rama>
```

---

# AWS CLI

## Configurar perfil:

1. Configurar perfil default.

```bash
aws configure
```

2. Configurar perfil especificando un nombre personalizado de perfil.

```bash
aws configure --profile profile-name
```

## Ejecutar comando con cierto perfil

Agregar el parametro

```bash
--profile <nombre-de-perfil>
```

Ejemplo:

```bash
aws ec2 describe-instances --profile sps-dev
```

## Cambiar de perfil por defecto:

```bash
setx AWS_PROFILE <nombre-de-perfil>
```

Es necesario reiniciar la terminal para que se apliquen los cambios.
