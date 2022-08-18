from http import client
import boto3
import jmespath
from loguru import logger
REGION = 'us-west-2'
PROFILE = 'principal-dev'
session = boto3.Session(region_name=REGION, profile_name=PROFILE)
client = session.client("lambda")
response = client.list_functions(
    FunctionVersion='ALL',
    MaxItems=500
)

lista_funciones = response["Functions"]
next_marker = response['NextMarker']

while 'NextMarker' in response:
    response = client.list_functions(
    FunctionVersion='ALL',
    MaxItems=500,
    Marker=response['NextMarker'])
    lista_funciones = lista_funciones + response["Functions"]



for funcion in lista_funciones:
    if len(funcion['FunctionName'].replace("-dev-dr", "-prod-dr")) > 64:
        print(funcion['FunctionName'].replace("-dev-dr", "-prod-dr"))

print(len(lista_funciones))
