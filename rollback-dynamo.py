# flake8: noqa

import os
import sys
import time
import datetime
from operator import truediv
from os import walk

import uuid
import boto3
import argparse
global args

parser = argparse.ArgumentParser()

parser.add_argument(
    "-r",
    "--region",
    required=True,
    action="store",
    dest="region",
    help="Region adonde se insertaran los valores",
    default=None,
)
parser.add_argument(
    "-rdr",
    "--regiondr",
    required=True,
    action="store",
    dest="region_dr",
    help="Ambiente DR",
    default=None,
)
parser.add_argument(
    "-a",
    "--ambiente",
    required=True,
    action="store",
    dest="ambiente",
    help="Ambiente donde se realizará rollback",
    default=None,
)

args = parser.parse_args()

# Variables de argumentos recibidos.
ambiente = args.ambiente
ambiente = "-" + ambiente
region = args.region
region_dr = args.region_dr

session = boto3.Session(
    region_name=region
)

session_dr = boto3.Session(
    region_name=region_dr
)


dynamo = session.client("dynamodb")
dynamo_dr = session_dr.client("dynamodb")

ruta_tablas = "tablas/"


def lista_tablas():
    """Crea una lista de todos los archivos dentro de la carpeta tablas/."""

    lista_tablas.lista_tablas = next(walk(ruta_tablas), (None, None, []))[2]
        
def separacion_tablas():
    '''Separa las tablas en listas dependiendo de su extensión ya sea .json o .csv'''
    
    # Se declaran las 2 listas de csv y json.
    separacion_tablas.lista_tablas_csv = []
    separacion_tablas.lista_tablas_json = []

    # Se itera en la lista de tablas para agregar a la lista de CSV las tablas que contengan esa extensión en su nombre.
    for tablas in lista_tablas.lista_tablas:
        if ".csv" in tablas:
            separacion_tablas.lista_tablas_csv.append(tablas)
            
    # Se itera en la lista de tablas para agregar a la lista de JSON las tablas que contengan esa extensión en su nombre.
        if ".json" in tablas:        
            separacion_tablas.lista_tablas_json.append(tablas)

def ambiente_por_extension():
    '''
    Reemplaza la extensión por el ambiente a cada elemento de cada una de las tablas de las listas de CSV y JSON.

    Ejemplos (antes y después):
    sia-cat-afore-infact24.csv -> sia-cat-afore-infact24-pre
    sia-gen-adm-permisos.json -> sia-gen-adm-permisos-pre
    '''

    separacion_tablas.lista_tablas_csv = [w.replace(".csv", ambiente) for w in separacion_tablas.lista_tablas_csv]
    separacion_tablas.lista_tablas_json = [w.replace(".json", ambiente) for w in separacion_tablas.lista_tablas_json]

def union_lista_tablas():
    '''Crea una lista de tablas que contiene todas las tablas, tanto provenientes de CSV o de JSON.'''

    separacion_tablas.union_lista = separacion_tablas.lista_tablas_csv + separacion_tablas.lista_tablas_json    
    separacion_tablas.lista_tablas_todas = sorted(separacion_tablas.union_lista)

lista_tablas()

separacion_tablas()

ambiente_por_extension()

union_lista_tablas()


def funcion_madre(nombre_tabla):
    """Controla el flujo de funciones que restauran el último respaldo de la tabla."""

    def lista_respaldos(nombre_tabla):
        ''' Lista respaldos de la tabla que se ingrese.'''
               
        print(f'Se listarán los respaldos de la tabla: {nombre_tabla}')
        # Se utiliza para el while.
        backup_reciente = False
        numero_backup = 0
        while backup_reciente == False:
            try:
                response = dynamo.list_backups(
                    TableName=nombre_tabla
                )
                print("Fecha de creación del backup: ", 
                response["BackupSummaries"][numero_backup]["BackupCreationDateTime"],
                response["BackupSummaries"][numero_backup]["BackupName"])
                numero_backup = numero_backup + 1
            except:
                try:
                    backup_reciente == True
                    numero_backup = numero_backup - 1
                    backup_a_restaurar = response["BackupSummaries"][numero_backup]["BackupName"]
                    # Se obtiene el último respaldo que comienza con despliegue_
                    while backup_a_restaurar.startswith('despliegue_') == False:
                        response = dynamo.list_backups(TableName=nombre_tabla) 
                        backup_a_restaurar = response["BackupSummaries"][numero_backup]["BackupName"]
                        numero_backup = numero_backup - 1
                        if numero_backup < 0:
                            print("Ha ocurrido un error al encontrar el último respaldo realizado por despliegue.")
                            exit(1)
                        
                    print("#------------------------------------------------#")
                    print("Fecha de creación del respaldo a restaurar: ", 
                    response["BackupSummaries"][numero_backup]["BackupCreationDateTime"])
                    print("#------------------------------------------------#")
                    print(f'El respaldo a restaurar es: {backup_a_restaurar}')
                    print("#------------------------------------------------#")
                    lista_respaldos.backup_arn = response["BackupSummaries"][numero_backup]["BackupArn"]
                    break
                except:
                    print("Error al restaurar tabla. La tabla no cuenta con respaldos.")
                    print("Por seguridad se detendrá el rollback. Favor de verificar en DynamoDB.")
                    exit(1)
  
    def borrar_tabla(nombre_tabla, dynamo):
        ''' 
        Elimina la tabla a la que se le hará rollback.
        
        (Función inspirada en movimiento de tablas.)

        args:
        nombre_tabla = nombre de la tabla recibida.

        dynamo = sesión que se estará utilizando para esta operación. Se vio esta necesidad 
        debido a que las tablas globales usan el mismo nombre pero cambia la región.

        '''
        # Obtener ARN de la tabla para poder crear el tag en la tabla cuando sea restaurada
        response = dynamo.describe_table(TableName=nombre_tabla)
        borrar_tabla.ARN_tabla = response['Table']['TableArn']

        try:
            dynamo.delete_table(TableName=nombre_tabla)
            waiter = dynamo.get_waiter("table_not_exists")
            waiter.wait(TableName=nombre_tabla)
            #print("Tabla eliminada.")
        except dynamo.exceptions.ResourceNotFoundException:
            print("La tabla no existe.")
    
    def valida_replica_eliminada(nombre_tabla):
        '''Valida que la réplica tenga un estado diferente a activo o eliminando.'''


        
        ###VALIDACION. En caso de error saltar.
        try:
            response = dynamo.describe_table(TableName=nombre_tabla)
            print("Eliminando tabla global. Un momento, por favor...")
            estado_replica = response['Table']['Replicas'][0]
            while estado_replica == "ACTIVE":
                time.sleep(3)
                estado_replica = response['Table']['Replicas'][0]
                print(estado_replica)
                print("La tabla global aún se encuentra activa.")

            while estado_replica == "DELETING":
                time.sleep(3)
                estado_replica = response['Table']['Replicas'][0]
                print(estado_replica)
                print("La tabla global se está eliminando.")

            while estado_replica == "UPDATING":
                time.sleep(3)
                estado_replica = response['Table']['Replicas'][0]
                print(estado_replica)
                print("La tabla global se está actualizando.")

        except Exception as e:
            print(e)
            print(f"Error al intentar eliminar tabla {nombre_tabla}. Puede que no exista.")

    def restaurar_tabla(nombre_tabla, backup_arn):
        '''Restaura el respaldo definido en el ARN en la tabla mencionada'''

        dynamo.restore_table_from_backup(
            TargetTableName=nombre_tabla,
            BackupArn=backup_arn,
            BillingModeOverride='PAY_PER_REQUEST'
        )
        
        response = dynamo.describe_table(TableName=nombre_tabla)
        estado_tabla = response['Table']['TableStatus']
        while estado_tabla != 'ACTIVE':
            response = dynamo.describe_table(TableName=nombre_tabla)
            estado_tabla = response['Table']['TableStatus']            
            print("Restaurando tabla. Espere un momento, por favor...")
            print(f"Estado de la tabla: {estado_tabla}")
            time.sleep(10)
        
        # Se crea tag en tabla restaurada.
        response = dynamo.tag_resource(
        ResourceArn=borrar_tabla.ARN_tabla ,
        Tags=[{'Key': 'Auditoria', 'Value': 'No'},{"Key": "Proyecto", "Value": "SIA"},])

        print("Restauración de tabla de origen completada.")

    def crear_tabla_global(nombre_tabla):
        '''Crea tabla global a partir del nombre de la tabla mencionada.'''
        try:    
            print("Se comienza creación tabla global de tabla de origen.")
            response = dynamo.update_table(
                TableName=nombre_tabla,
                ReplicaUpdates=[
                        {
                            'Create': {
                                'RegionName': region_dr,
                            },
                        },
                    ]
                    )
            response
            print(f"La petición para convertir la tabla {nombre_tabla} ha sido enviada correctamente. Favor de validar en DynamoDB")
        except Exception as e:
            print(e)
            print("La tabla ya cuenta con una tabla global.")

    # Orden de funciones:
    lista_respaldos(nombre_tabla)
    
    # Borrar tabla global.
    if "-dev" in nombre_tabla:
        print("Se eliminará tabla global...")
        try:
            borrar_tabla(nombre_tabla, dynamo_dr)   

            # Validar que tabla global haya sido eliminada
            valida_replica_eliminada(nombre_tabla)
        except:
            print("La tabla no cuenta con tablas globales.")
    
    # Borrar tabla de origen.
    for retry in range(0,5):
        time.sleep(60)
        print("Este proceso durará algunos minutos.")
        print("Intentando eliminar tabla origen...")
        while True:
            try:
                borrar_tabla(nombre_tabla, dynamo)
            except:
                print("Se está terminando de sincronizar tabla de origen y tabla global.")
                print("Terminando la sincronización se eliminará tabla de origen.")
                time.sleep(15)
                continue
            break
        break
    
    
    # Restaurar último respaldo de tabla de origen.
    restaurar_tabla(nombre_tabla, lista_respaldos.backup_arn)
    
    # Crear tabla global de tabla de origen.
    if "-dev" in nombre_tabla:
        crear_tabla_global(nombre_tabla)    

# Ejecución uno por uno del proceso de tablas.
for nombres_tablas in separacion_tablas.lista_tablas_todas:

    print("!--------------------------------------------------!")
    print(f"Tabla en proceso de rollback: {nombres_tablas}")
    print("!--------------------------------------------------!")
    time.sleep(3)
    funcion_madre(nombres_tablas)