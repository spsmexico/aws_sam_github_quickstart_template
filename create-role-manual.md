# Creación de rol de despliegue

## Creando identity provider:
Para crear un identity provider es necesario ingresar a **IAM**, daremos clic en la opción de la barra lateral izquierda en **identity providers** 
![](assets/workshop/GRD_01.PNG)

damos clic en el botón de "Add provider".
![](assets/workshop/GRD_02.PNG)

Para comenzar a configurarlo damos:
1. clic en **OpenID Connect**, 
2. en **provider URL** escribimos: ```https://token.actions.githubusercontent.com```
3. y clic en **Get thumbprint**
![](assets/workshop/GRD_03a.PNG)

En **Audience** debemos agregar ```sts.amazonaws.com```
![](assets/workshop/GRD_05.PNG)

Se puede agregar de forma opcional un tag en **Add tags** y por último damos clic en **Add provider**:
![](assets/workshop/GRD_04.PNG)

Una ves creado debería de verse de la siguiente forma:
![](assets/workshop/GRD_06.PNG)

## Creando rol
En esta sección se sugiere nombrar el rol con *identificador-del-proyecto*-github-actions-role (sin agregarle el sufijo de ambiente. 
Para crear el rol, nos iremos en la sección de IAM > Roles 
![](assets/workshop/CR_01.PNG)

y daremos clic en "**Create role**", 
![](assets/workshop/CR_02.PNG)

Aquí los pasos a seguir son:

1. Seleccionamos **Web identity**,
2. en *_Identity povider_* seleccionamos ```https://token.actions.githubusercontent.com```, 
3. en *_Audience_* seleccionamos ```sts.amazonaws.com``` y
4. damos clic en **Next**
![](assets/workshop/CR_03.PNG)


#### Agregar las políticas necesarias:
En este punto es indispensable que el rol que desplegará, cuente con acceso a Cloudformation y los servicios que estará
desplegando:
![](assets/policies.PNG)

#### Permisos sugeridos:
Estos permisos se sugieren habilitar para poder realizar su despliegue. Salvo que haya alguno que sobre o alguno que falte deberá ser agregado/eliminado:
```
AmazonAPIGatewayAdministrator
AmazonS3FullAccess
AWSCloudFormationFullAccess
AWSLambda_FullAccess
```
![](assets/workshop/CR_05.gif)

Y damos clic en siguiente
![](assets/workshop/CR_04.PNG)

Le asignamos un nombre al rol
![](assets/workshop/CR_06.PNG)

De manera opcional también podemos asignar un tag, y damos clic en **Create role**:
![](assets/workshop/CR_07.PNG)

Para verificar que el rol esta creado, podemos buscarlo:
![](assets/workshop/CR_08.PNG)

Le damos clic a nuestro rol y en **Add permissions**, sale un menú desplegable y damos clic en **Create inline policy**:
![](assets/workshop/CR_09.PNG)

Lo cambiamos a formato *_JSON_*:
![](assets/workshop/CR_10.PNG)

Insertamos directamente al rol para poder desplegar y damos clic en siguiente:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "iam:UntagRole",
                "iam:TagRole",
                "iam:UpdateRoleDescription",
                "iam:CreateRole",
                "iam:DeleteRole",
                "iam:AttachRolePolicy",
                "iam:PutRolePolicy",
                "iam:TagPolicy",
                "iam:CreatePolicy",
                "iam:DetachRolePolicy",
                "iam:DeleteRolePolicy",
                "iam:UntagPolicy",
                "iam:UpdateRole"
            ],
            "Resource": "*"
        }
    ]
}
```

Le damos un nombre en **Policy name** y para terminar, clic en **Create policy**:
![](assets/workshop/CR_11.PNG)

Ahora damos clic en la pestaña de **Trust relationships** y en **Edit trust policy**:
![](assets/workshop/CR_12a.PNG)

En este bloque agregaremos lo siguiente sustituyendo los siguientes valores: 

```
{
   "Version": "2012-10-17",
   "Statement": [
       {
           "Effect": "Allow",
           "Principal": {
               "Federated": "arn:aws:iam::<NUMERO_CUENTA_AWS>:oidc-provider/token.actions.githubusercontent.com"
           },
           "Action": "sts:AssumeRoleWithWebIdentity",
           "Condition": {
               "StringEquals": {
                   "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
               },
               "StringLike": {
                   "token.actions.githubusercontent.com:sub": "repo:<ORGANIZACION_GITHUB>/<NOMBRE_REPOSITORIO>:*"
               }
           }
       }
   ]
}
```
NUMERO_CUENTA_AWS = Número de cuenta de la cuenta AWS donde se estará desplegando, en este caso podemos obtenerla en la parte superior derecha de la consola AWS.

ORGANIZACION_GITHUB = Organización o usuario de GitHub a la que pertenece el repositorio. 

NOMBRE_REPOSITORIO = Nombre del repositorio.

Por último daremos clic en **Update Policy**. -->
