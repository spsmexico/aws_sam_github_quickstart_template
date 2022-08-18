# Insumos

| Tipo    | Archivos de entrada                       | Origen        |
| ------- | ----------------------------------------- | ------------- |
| Archivo | Ofutprincipal_YYYYMMDD_Cash_Principal.csv | Contabiilidad |
| API     | API de Trades                             | Aladdin       |

# 

# Salidas

| Tipo    | Archivos de entrada                       | Origen        |
| ------- | ----------------------------------------- | ------------- |
| Archivo | Ofutprincipal_YYYYMMDD_Cash_Principal.csv | Contabiilidad |
|         |                                           |               |



# Componentes principales

Normalmente son componentes que se crean en la plantilla del proceso, pero también hay casos en los que se crean fuera de la plantilla

Ejemplo: tablas que únicamente son usadas por este proceso o parametros en _Parameter Store_ 

| Tipo   | Nombre                                  | Función                      |
| ------ | --------------------------------------- | ---------------------------- |
| Lambda | sia-afore-citivarmar-notificaciones     |                              |
|        | sia-afore-citivarmar-procesamiento      |                              |
|        | sia-afore-citivarmar-start              | Iniciar el proceso           |
|        | sia-afore-citivarmar-validacion         | Validad las entradas/insumos |
|        | sia-afore-citivarmar-validacion-fallida |                              |



# Componentes transversales

Son componentes que utiliza el proceso pero también son utilizados por más procesos

Ejemplo: catalogos, checklist, SQS.

| Tipo     | Nombre                              | Función                          |
| -------- | ----------------------------------- | -------------------------------- |
| DynamoDB | sia-afore-aims-cat-contrapartes-dev | Obtener las contrapartes para... |
|          |                                     |                                  |
|          |                                     |                                  |
|          |                                     |                                  |
|          |                                     |                                  |

# Impacto a otros procesos

Si tu proceso modifica componentes usados por otros proceso ¿cómo se verían afectados en caso de un mal funcionamiento de este proceso?

Esto normalmente aplica solo para utilerias/procesos transversales.

| Mal funcionamiento                                         | Procesos afectados | Afectación                                                                                |
| ---------------------------------------------------------- | ------------------ | ----------------------------------------------------------------------------------------- |
| Los archivos de entrada no son eliminados del bucket de S3 | Todos              | Al siguiente todos los proceso tomarían el archivo de ayer como el insumo del día de hoy. |



# Roles

| Nombre                                           | Políticas                          | Acciones                                                                                               |
| ------------------------------------------------ | ---------------------------------- | ------------------------------------------------------------------------------------------------------ |
| sia-afore-factor-in-dev-LambdaStartExecutionRole | sia-afore-factor-in-dynamo-policy- | "dynamodb:Getitem" "dynamodb:BatchGetItem" "dynamodb:Query" "dynamodb:Scan"                            |
|                                                  | sia-afore-factor-in-sqs-policy-    | "sqs:GetQueueAttributes",<br/>                "sqs:SendMessage",<br/>                "sqs:GetQueueUrl" |



# ¿Qué pasos manuales necesitan ejecutarse para su funcionamiento?

- Registro de sia-afore-citivarmar en la tabla de permisos de PRE y PROD.


