"""Script para cambiar región activa.

Este script habilita la región que reciba como secundaria y desactiva la región primaria. En el
siguiente orden:
1.- Desactiva el trail "{{cookiecutter.project}}-cloudtrail" en la región primaria y lo habilita en la secundaria.
2.- Desactiva todas las reglas de EventBridge que inician con "{{cookiecutter.project}}-" en la región primaria y las habilita en la secundaria.
3.- Modifica la autorización del API Gateway de la región primaria para esperar un valor distinto de "audience" 
en el token de Cognito (deja de recibir peticiones) y coloca el valor correcto para el API Gateway de la región secundaria
(acepta peticiones).
4.- Se modifica la autorización de Appsync en la región primaria para utilizar IAM (dejar de recibir peticiones con token 
de Cognito) y modifica la autorización en la región secundaria para permitir peticiones usando el token de Cognito.
5.- Modifica el dominio del Frontend en la región primaria para apuntar a la rama dr/{ambiente}/{region}-apagado que
contiene una página estatica con la URL de la región secundaria. Modifica el dominio en la región secundaria para dejar
de apuntar a la rama dr/{ambiente}/{region}-apagado y mostrar {{cookiecutter.project|upper}}.

El script es idempotente, esto significa que se puede ejecutar multiples veces con los mismos argumentos y siempre se obtendrá
el mismo resultado.

Example:
    Examples can be given using either the ``Example`` or ``Examples``
    sections. Sections support any reStructuredText formatting, including
    literal blocks::

        $ python example_google.py

Todo:
    * For module TODOs
    * You have to also use ``sphinx.ext.todo`` extension
"""

import pprint
import logging
import sys
import argparse

import boto3
import jmespath

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

global args
parser = argparse.ArgumentParser()

parser.add_argument(
    "-p",
    "--region_primaria",
    required=True,
    action="store",
    dest="region_primaria",
    help="Región de AWS primaria (A apagar)",
    default=None,
)
parser.add_argument(
    "-s",
    "--region_secundaria",
    required=True,
    action="store",
    dest="region_secundaria",
    help="Región de AWS secundaria (A encender)",
    default=None,
)

parser.add_argument(
    "-a",
    "--ambiente",
    required=True,
    action="store",
    dest="ambiente",
    help="Ambiente en el que se está realizando el cambio ",
    default=None,
)

args = parser.parse_args()

REGION_PRIMARIA = args.region_primaria
REGION_SECUNDARIA = args.region_secundaria
AMBIENTE = args.ambiente


#Se crean sesiones con las diferentes regiones
session = boto3.Session(region_name=REGION_PRIMARIA)
session_dr = boto3.Session(region_name=REGION_SECUNDARIA)


# Se crea uno de 
cloudtrail_primario = session.client('cloudtrail')
cloudtrail_secundario = session_dr.client('cloudtrail')
eventbridge_primario = session.client('events')
eventbridge_secundario = session_dr.client('events')
apigateway_primario = session.client('apigatewayv2')
apigateway_secundario = session_dr.client('apigatewayv2')
appsync_primario = session.client('appsync')
appsync_secundario = session_dr.client('appsync')
amplify_primario = client = session.client('amplify')
amplify_secundario = client = session_dr.client('amplify')
ssm_primario = client = session.client('ssm')
ssm_secundario = client = session_dr.client('ssm')


def obtener_parametro(sesion_ssm, nombre_parametro, tipo_salida):
    '''
    Devuelve el valor del nombre del parámetro (de Parameter Store) recibido.
    Lo puede devolver como lista (esto para el client_id del API Gateway) en caso de que
    reciba un tercer parámetro.

    Parámetros
    ----------
    sesion_ssm : variable
        Es la sesión utilizada para conectarse a parameter store vía API de AWS.
        Se entiende como sesión, la región que se esté utilizando. Pudiera ser primaria o secundaria.
    nombre_parametro : string
        Nombre del parametro en Parameter Store.
    tipo_salida : string
        Si es requerido que esta función devuelva el valor encontrado como una lista, especificar 
        la palabra "lista" en el tercer parámetro de esta función.
    '''    

    response = sesion_ssm.get_parameter(
        Name=nombre_parametro,
        WithDecryption=False
    )
    valor_parametro = response['Parameter']['Value']

    if tipo_salida == "list":    
        parametro_lista = []
        parametro_lista += [valor_parametro]
        return parametro_lista
    else:
        return valor_parametro

def intercambiar_trail():
    logging.info("----------- Intercambiando trails ------------")
    
    ## Primario ##
    try:
        trail_primario_arn = cloudtrail_primario.list_trails()
        trail_primario_arn = jmespath.search("Trails[?starts_with(Name,'{{cookiecutter.project}}-cloudtrail')].TrailARN", trail_primario_arn)
        if len(trail_primario_arn) != 1:
            logging.error(trail_primario_arn)
            raise Exception("Hay dos trails que cumplen el nombrado")
        else:
            trail_primario_arn = trail_primario_arn[0]
            logging.info(f"Trail primario{trail_primario_arn}")
    except:
        logging.warning(f"Ocurrió un problema al intentar obtener valores del trail en {REGION_PRIMARIA}")

    ## Secundario ##
    trail_secundario_arn = cloudtrail_secundario.list_trails()
    trail_secundario_arn = jmespath.search("Trails[?starts_with(Name,'{{cookiecutter.project}}-cloudtrail')].TrailARN", trail_secundario_arn)
    if len(trail_secundario_arn) != 1:
        logging.error(trail_secundario_arn)
        raise Exception("Hay dos trails que cumplen el nombrado")
    else:
        trail_secundario_arn = trail_secundario_arn[0]
        logging.info(f"Trail secundario: {trail_secundario_arn}")
    try:
        ## Intercambio ##
        logging.info(f">> Apagando trail en región {REGION_PRIMARIA}")
        response = cloudtrail_primario.stop_logging(
            Name=trail_primario_arn
        )
        pprint.pprint(response)
    except:
        logging.warning(f"No fue posible apagar el trail en {REGION_PRIMARIA}")

    logging.info(f">> Encendiendo trail en región {REGION_SECUNDARIA}")
    response = cloudtrail_secundario.start_logging(
        Name=trail_secundario_arn
    )
    pprint.pprint(response)


def intercambiar_reglas_eventbridge():
    logging.info("------ Intercambiando reglas de eventbridge -----")
    
    ## Primario ##
    try:
        reglas = eventbridge_primario.list_rules()
        nombres_reglas = jmespath.search("Rules[?starts_with(Name,'{{cookiecutter.project}}-')].Name", reglas)
    except:
        logging.warning(f"Ocurrió un problema al obtener variables Eventbridge de {REGION_PRIMARIA}")        

    ## Secundario ##
    reglas_encender = eventbridge_secundario.list_rules()
    nombres_reglas_encender = jmespath.search("Rules[?starts_with(Name,'{{cookiecutter.project}}-')].Name", reglas_encender)

    ## Intercambio ##
    try:
        print(f">> Reglas a encender: {len(nombres_reglas_encender)}")
        print(f">> Reglas a apagar: {len(nombres_reglas)}")        
        if len(nombres_reglas) != len(nombres_reglas_encender):
            logging.warning("El número de reglas no es igual en ambas regiones")
    
        print(f">> Apagando {len(nombres_reglas)} reglas de EventBridge en región {REGION_PRIMARIA}")
        for regla in nombres_reglas:
            response = eventbridge_primario.disable_rule(Name=regla, EventBusName='default')
            print(f"  - Apagando {regla}: HTTP Status {response['ResponseMetadata']['HTTPStatusCode']}")
    except:
        logging.warning(f"No fue posible apagar reglas de {REGION_PRIMARIA}")

    print(f"Encendiendo {len(nombres_reglas_encender)} reglas de EventBridge en región {REGION_SECUNDARIA}")
    for regla in nombres_reglas_encender:
        response = eventbridge_secundario.enable_rule(Name=regla, EventBusName='default')
        print(f"  - Encendiendo {regla}: HTTP Status {response['ResponseMetadata']['HTTPStatusCode']}")


def intercambiar_apigateway():
    logging.info("------- Intercambiando API Gateway ---------")
    
    ## PRIMARIO ##
    try:
        response = apigateway_primario.get_apis(
            MaxResults='5',
        )
        api_id = jmespath.search("Items[?Name == '{{cookiecutter.project}}-apigateway'].ApiId", response)
        
        if len(api_id) != 1:
            logging.error(api_id)
            raise Exception(f"Se esperaba 1 API Gateways en {REGION_PRIMARIA}")
        else:
            api_id = api_id[0]
        logging.info(f">> API ID en {REGION_PRIMARIA}: {api_id}")
        
        auth = apigateway_primario.get_authorizers(
            ApiId=api_id,
            MaxResults='5',
            )['Items'][0]
        logging.info(f"  - Authorizer en {REGION_PRIMARIA}:")
        pprint.pprint(auth)
    except:
        logging.warning(f"No fue obtener variables de API Gateway en {REGION_PRIMARIA}")            

    ## SECUNDARIO ##
    response = apigateway_secundario.get_apis(
        MaxResults='5',
    )
    pprint.pprint(response)
    api_id_secundario = jmespath.search("Items[?Name == '{{cookiecutter.project}}-apigateway'].ApiId", response)
    if len(api_id_secundario) != 1:
        logging.error(api_id_secundario)
        raise Exception(f"Se esperaba 1 API Gateways en {REGION_SECUNDARIA}")
    else:
        api_id_secundario = api_id_secundario[0]
    logging.info(f">> API ID en {REGION_SECUNDARIA}: {api_id_secundario}")
    
    auth_secundario = apigateway_secundario.get_authorizers(
        ApiId=api_id_secundario,
        MaxResults='5',
        )['Items'][0]
    logging.info(f"  - Authorizer en {REGION_SECUNDARIA}:")
    pprint.pprint(auth_secundario)

    ## INTERCAMBIO ##
    logging.info(f">> Se habilita API Gateway en {REGION_SECUNDARIA}")
    try:    
        audience = obtener_parametro(ssm_secundario, '{{cookiecutter.project}}-user-pool-client-id-frontend', 'list')
        response = apigateway_secundario.update_authorizer(
            ApiId=api_id_secundario,
            AuthorizerId=auth_secundario['AuthorizerId'],
            AuthorizerType='JWT',
            IdentitySource=auth['IdentitySource'],
            JwtConfiguration={'Audience': audience, 'Issuer': auth_secundario['JwtConfiguration']['Issuer']}, 
            Name=auth_secundario['Name']
        )
        pprint.pprint(response)
    except Exception as e:
        print(e)        
        logging.warning(f"No fue posible activar el API Gateway en la región secundaria ({REGION_SECUNDARIA}).")

    logging.info(f">> Se desactiva API Gateway en {REGION_PRIMARIA}")
    try:
        response = apigateway_primario.update_authorizer(
            ApiId=api_id,
            AuthorizerId=auth['AuthorizerId'],
            AuthorizerType='JWT',
            IdentitySource=auth['IdentitySource'],
            JwtConfiguration={'Audience': ["DESACTIVADO"], 'Issuer': auth['JwtConfiguration']['Issuer']},
            Name=auth['Name']
        )
        pprint.pprint(response)
    except Exception as e:
        print(e)
        logging.warning(f"No fue posible desactivar el API Gateway en la región primaria ({REGION_PRIMARIA}).")


def intercambiar_appsync():
    logging.info("-------- Intercambiando AppSync -----------")

    ## PRIMARIO ##
    try:
        appsync_apis = appsync_primario.list_graphql_apis(
            maxResults=5
        )
        api_primario = jmespath.search("graphqlApis[?starts_with(name,'{{cookiecutter.project}}-frontend-appsync-api-')]", appsync_apis)
        if len(api_primario) != 1:
            logging.error(api_primario)
            raise Exception("Se esperaba 1 API Gateway")
        else:
            api_primario = api_primario[0]
        logging.info(f">> AppSync API {api_primario} en {REGION_PRIMARIA}")
    except Exception as e:
        logging.warning(f"No fue posible obtener variables para Appsync de la región primaria ({REGION_PRIMARIA}).")
        print(e)

    ## SECUNDARIO ##
    try:
        appsync_apis_secundario = appsync_secundario.list_graphql_apis(
            maxResults=5
        )
        api_secundario = jmespath.search("graphqlApis[?starts_with(name,'{{cookiecutter.project}}-frontend-appsync-api-')]", appsync_apis_secundario)
        if len(api_secundario) != 1:
            logging.error(api_secundario)
            raise Exception("Se esperaba 1 API Gateway")
        else:
            api_secundario = api_secundario[0]
        logging.info(f">> AppSync API {api_secundario} en {REGION_SECUNDARIA}")
    except Exception as e:
        logging.warning(f"No fue posible obtener variables para Appsync de la región secundaria ({REGION_PRIMARIA}).")
        print(e)

    ## INTERCAMBIO ##
    # Si no ha sido intercambiado antes ejecutar el intercambio (idempotencia)
    logging.info(f">> Activando Appsync {REGION_SECUNDARIA}")
    try:
        user_pool_id = obtener_parametro(ssm_secundario, "{{cookiecutter.project}}-user-pool-id", "string")
        response = appsync_secundario.update_graphql_api(
            apiId=api_secundario['apiId'],
            name=api_secundario['name'],
            authenticationType="AMAZON_COGNITO_USER_POOLS",
            userPoolConfig={
                'userPoolId': user_pool_id,
                'awsRegion': REGION_SECUNDARIA,
                'defaultAction': 'ALLOW'},
            logConfig=api_secundario['logConfig'],
        )  
        pprint.pprint(response)

    except Exception as e:
        print(e)
        logging.warning(f"No fue posible activar Appsynnc en ({REGION_SECUNDARIA}).")
    
    logging.info(f">> Desactivando Appsync {REGION_PRIMARIA}")
    try:    
        response = appsync_primario.update_graphql_api(
            apiId=api_primario['apiId'],
            name=api_primario['name'],
            authenticationType="AWS_IAM",
            logConfig=api_primario['logConfig'],
        )
        pprint.pprint(response)

    except Exception as e:
        print(e)        
        logging.warning((f">> No fue posible desactivar Appsync en {REGION_PRIMARIA}"))



def intercambiar_frontend():
    logging.info("------- Intercambiando Amplify -----------")

    ## PRIMARIO ##
    try:
        app_id = amplify_primario.list_apps()['apps']
        if len(app_id) != 1:
            logging.error(app_id)
            raise Exception("Hay más de una aplicación de amplify")
        else:
            app_id = app_id[0]['appId']
        logging.info(f">> Amplify {app_id} en región {REGION_PRIMARIA}")
        domain_association = amplify_primario.list_domain_associations(appId=app_id,maxResults=5)['domainAssociations']
        if len(domain_association) != 1:
            logging.error(domain_association)
            raise Exception("Hay más de un dominio en amplify")
        else:
            domain_association = domain_association[0]
        logging.info(f"  - Dominio:")
        pprint.pprint(domain_association)
   
    except Exception as e:
        print(e)
        logging.warning(f"No fue posible obtener variables de Amplify en la región primaria ({REGION_PRIMARIA}).")

    ## SECUNDARIO ##
    try:
        app_id_secundario = amplify_secundario.list_apps()['apps']
        if len(app_id_secundario) != 1:
            raise Exception("Hay más de una aplicación de amplify")
        else:
            app_id_secundario = app_id_secundario[0]['appId']
        logging.info(f">> Amplify {app_id_secundario} en región {REGION_SECUNDARIA}")
        domain_association_secundario = amplify_secundario.list_domain_associations(appId=app_id_secundario,maxResults=5)['domainAssociations']
        if len(domain_association_secundario) != 1:
            logging.error(app_id_secundario)
            raise Exception("Hay más de un dominio en amplify")
        else:
            domain_association_secundario = domain_association_secundario[0]
        logging.info(f"  - Dominio:")
        pprint.pprint(domain_association_secundario)  

    except Exception as e:
        print(e)
        logging.warning(f"No fue posible obtener variables de Amplify en la región secundaria ({REGION_SECUNDARIA}).")

    ## INTERCAMBIO ##
    # Si no ha sido intercambiado antes ejecutar el intercambio (idempotencia)
    logging.info(f">> Desactivando Amplify {app_id} en región {REGION_PRIMARIA}")
    try:
        response = amplify_primario.update_domain_association(
            appId=app_id,
            domainName=domain_association['domainName'],
            enableAutoSubDomain=domain_association['enableAutoSubDomain'],
            subDomainSettings=[{
                'branchName': f"dr/{AMBIENTE}/{REGION_PRIMARIA}-apagado",
                'prefix': ''}]
        )
        pprint.pprint(response)
    except Exception as e:
        print(e)
        logging.warning(f"Ocurrió un problema al desactivar Amplify en {REGION_PRIMARIA}")

    try:
        logging.info(f">> Activando Amplify {app_id_secundario} en región {REGION_SECUNDARIA}")
        release_frontend = obtener_parametro(ssm_secundario, "release-frontend", "string")
        response = amplify_secundario.update_domain_association(
            appId=app_id_secundario,
            domainName=domain_association_secundario['domainName'],
            enableAutoSubDomain=domain_association_secundario['enableAutoSubDomain'],
            subDomainSettings=[{
                'branchName': release_frontend,
                'prefix': ''}]
        )
        pprint.pprint(response)
    except Exception as e:
        print(e)
        logging.warning(f"Ocurrió un problema al activar Amplify en ({REGION_SECUNDARIA}).")    


if __name__ == "__main__":

    try:
        intercambiar_trail()
    except Exception as e:
        logging.error("**** Error al cambiar trail de región ****")
        logging.exception(e)

    try:
        intercambiar_reglas_eventbridge()
    except Exception as e:
        logging.error("**** Error al cambiar reglas de eventbridge de región ****")
        logging.exception(e)


    try:
        intercambiar_apigateway()
    except Exception as e:
        logging.error("**** Error al cambiar API Gateway de región ****")
        logging.exception(e)

        logging.error("**** Error al cambiar Frontend de región ****")
        logging.exception(e)

    try:
        intercambiar_appsync()
    except Exception as e:
        logging.error("**** Error al cambiar AppSync de región ****")
        logging.exception(e)

    try:
        intercambiar_frontend()
    except Exception as e:
        logging.error("**** Error al cambiar Frontend de región ****")
        logging.exception(e)        