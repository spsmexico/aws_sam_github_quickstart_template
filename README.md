# Prerequisitos:
## 1. Creación de llaves KMS
Como prerequisito es importante crear 2 llaves KMS "multiregión", una para SSM y otra para DynamoDB.
La región de creación de la llave será la región principal. Y la secundaría será la destinada para DR.

El nombrado debe seguir el siguiente estándar:

#### identificador_del_proyecto-servicio_de_aws-ambiente
--------------
Ejemplo de llave SSM:\

Identificador = proyectonuevo\
Servicio = ssm\
Ambiente = dev

#### Nombre de la nueva llave a crear: proyectonuevo-ssm-dev
Ejemplo de llave DynamoDB:

Identificador = proyectonuevo\
Servicio = dynamo\
Ambiente = dev

#### Nombre de la nueva llave a crear: proyectonuevo-dynamodb-dev

NOTA: Cuando iniciemos la creación de nuestra plantilla quickstart Cookiecutter nos solicitará los ARN's 
de ambas llaves.
-------------------


