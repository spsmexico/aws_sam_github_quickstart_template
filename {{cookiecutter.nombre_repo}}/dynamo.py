# flake8: noqa

import time
import json
from os import walk

import json
import uuid
import boto3
import argparse
global args

parser = argparse.ArgumentParser()

parser.add_argument(
    "-a",
    "--ambiente",
    required=True,
    action="store",
    dest="ambiente",
    help="Ambiente hacia donde se insertran los valores",
    default=None,
)
parser.add_argument(
    "-r",
    "--region",
    required=True,
    action="store",
    dest="region",
    help="Region adonde se insertaran los valores",
    default=None,
)

args = parser.parse_args()

# Variables de argumentos recibidos.
ambiente = args.ambiente
ambiente = "-" + ambiente
region = args.region


print("Argumentos recibidos:")
print("ambiente", ambiente)
print("region", region)

session = boto3.Session(
    region_name=region,
)

dynamo = session.client("dynamodb")

ruta_tablas = "tablas/"


def lista_tablas():
    """Crea una lista de todos los archivos dentro de la carpeta tablas/."""
    
    lista_tablas.lista_tablas = next(walk(ruta_tablas), (None, None, []))[2]
    
    lista_tablas.lista_tablas_json = []
    # Se itera en la lista de tablas para agregar a la lista de JSON las tablas que contengan esa extensión en su nombre.
    for tablas in lista_tablas.lista_tablas:
        if ".json" in tablas:        
            lista_tablas.lista_tablas_json.append(tablas)    


def ambiente_por_extension():
    '''
    Reemplaza la extensión por el ambiente a cada elemento de la lista de tablas.

    Ejemplo (antes y después):
    tabla-registros-prueba.json -> tabla-registros-prueba-pre
    '''

    lista_tablas.lista_tablas_json = [w.replace(".json", ambiente) for w in lista_tablas.lista_tablas_json]


def funcion_madre(nombre_tabla):
    """Controla el flujo de funciones que realizan la validación e inserción."""
    
    # Se declaran tablas sin ambiente para usos al momento de dirigirse a items o archivos json.
    nombre_tabla_sin_ambiente = nombre_tabla
    nombre_tabla_sin_ambiente = nombre_tabla_sin_ambiente.replace(ambiente, "")

    def validar_existencia_tablas(tablas):
        """
        Valida la existencia o inexistencia de las tablas.

        Durante la validación se separan las tablas en diferentes listas. Existentes e inexistentes.        
        """

        lista_tablas_existentes = []
        lista_tablas_no_existentes = []
        
        for tabla in tablas:
            try:
                response = dynamo.describe_table(TableName=tabla)
                response
                lista_tablas_existentes.append(tabla)
            except:
                # Se separan tablas inexistentes
                lista_tablas_no_existentes.append(tabla)
        validar_existencia_tablas.lista_tablas_inexistentes = lista_tablas_no_existentes
                        

        if lista_tablas_existentes != []:
            print(
                "\n#------------------------------------------------------------------------#"
            )
            print("Tablas existentes: " + ", ".join(lista_tablas_existentes))
            print(
                "#---------------------------------------------------------------------------#"
            )

        if validar_existencia_tablas.lista_tablas_inexistentes != []:
            print(
                "\n#-------------------------------------------------------------------------#"
            )
            print("Tablas inexistentes: " + ", ".join(validar_existencia_tablas.lista_tablas_inexistentes))
            print(
                "#---------------------------------------------------------------------------#"
            )

    def conversion_json():
        '''En caso de que la tabla sea tipo JSON la convierte en diccionario para Python usando json loads.'''
        
        if nombre_tabla in lista_tablas.lista_tablas_json:
            with open(f'{ruta_tablas}{nombre_tabla_sin_ambiente}.json', 'r') as myfile:
                data=myfile.read()
                conversion_json.archivo = json.loads(data)

    def crear_tabla(tablas_inexistentes, tabla_a_crear):
        """Crea la tabla si está en la lista de tablas inexistentes.
        
        Al momento de su creación, revisa su estatus. La función termina hasta que el estatus
        de la tabla a crear sea ACTIVO.
        """


        # Dependiendo de la lista se usa la llave primaria y tipo de dato de llave primaria.
        if tabla_a_crear in lista_tablas.lista_tablas_json:
        
            # Se toma la primera llave del diccionario a insertar como PK. Y el tipo de esa PK.
            diccionario = conversion_json.archivo['Actualizaciones'][0]
            llave_primaria = list(diccionario.keys())[0]
            tipo_dato_llave_primaria = list(diccionario[llave_primaria])[0]

        if tabla_a_crear in tablas_inexistentes:
            try:
                print("Creando tabla.. " + tabla_a_crear)
                print(f"Llave primaria:{llave_primaria}")
                print(f"Tipo dato:{tipo_dato_llave_primaria}")

                response = dynamo.create_table(
                    AttributeDefinitions=[
                        {"AttributeName": llave_primaria, "AttributeType": tipo_dato_llave_primaria},
                    ],
                    TableName=tabla_a_crear,
                    KeySchema=[
                        {"AttributeName": llave_primaria, "KeyType": "HASH"},
                    ],
                    BillingMode="PAY_PER_REQUEST",
                    Tags=[
                        {"Key": "Proyecto", "Value": "{{cookiecutter.project|upper}}"},
                    ],
                )

                response = dynamo.describe_table(TableName=tabla_a_crear)

                estado_tabla = response["Table"]["TableStatus"]
                while estado_tabla != "ACTIVE":
                    time.sleep(3)
                    response = dynamo.describe_table(TableName=tabla_a_crear)
                    estado_tabla = response["Table"]["TableStatus"]
                    print(estado_tabla)
                print(f"Tabla {tabla_a_crear} creada exitosamente")
            except Exception as e:
                print("Error al intentar crear tabla.")
                exit(1)

    def respaldos_tablas(nombre_tabla):
        ''' Crea respaldos de la tabla a la que se le insertarán los datos.
        
        Esto ocurre justo antes de la inserción. Después de haber aprobado 
        todas las validaciones previas.
        
        Las tablas que se encuentran listadas en la lista de "inexistentes" no son aptas 
        para respaldo, ya que son tablas vacías. Sólo se considera realizar respaldos
        a tablas previamente creadas (existentes).
        
        (Función inspirada en script de movimiento de tablas anterior.)
        '''
        
        if nombre_tabla in validar_existencia_tablas.lista_tablas_inexistentes:
            return "La tabla acaba de ser creada, no es necesario crear respaldos."
        UUID = uuid.uuid4()
        UUID_String = str(UUID)
        nombre_respaldo = (
        
        "despliegue_" + nombre_tabla + UUID_String
        
        )
        
        print(f'Se respaldará la tabla: {nombre_tabla}')
        print(f'Nombre del respaldo: {nombre_respaldo}')

        response = dynamo.create_backup(
            TableName=nombre_tabla, BackupName=nombre_respaldo
        )
        print("ARN de respaldo =", response["BackupDetails"]["BackupArn"])  

    def insercion_json(nombre_tabla):                
        """Inserta los items declarados en los archivos JSON de la carpeta tablas/ en Dynamo."""
        
        try:    
            # Obtenemos la cantidad de items a insertar desde el archivo json.
            longitud = len(conversion_json.archivo['Actualizaciones'])

            item = 0
            while item != longitud:
                # Se comienza inserción json.
                response = dynamo.put_item(
                    TableName=nombre_tabla, Item=conversion_json.archivo['Actualizaciones'][item]
                )
                response
                print("Inserción #" + str(item + 1) + " completada.")
                item = item + 1
        except:
            print(f"Error al insertar desde {nombre_tabla}.json. Validar que no esté vacío y tenga estructura de JSON DynamoDB")
            exit(1)            
    def eliminaciones(nombre_tabla):                
        """
        Elimina los items declarados en los archivos JSON de la carpeta tablas/ en Dynamo.
        Dentro de la lista de eliminaciones de los archivos JSON.
        """
        
        if conversion_json.archivo['Eliminaciones'] == []:
            print("No se realizaran eliminaciones.")
        else: 
            try:    
                # Obtenemos la cantidad de items a eliminar desde el archivo json.
                longitud = len(conversion_json.archivo['Eliminaciones'])
                
                item = 0
                while item != longitud:
                    # Se comienza eliminación.
                    response = dynamo.delete_item(
                        TableName=nombre_tabla, Key=conversion_json.archivo['Eliminaciones'][item]
                    )
                    response
                    print("Eliminación #" + str(item + 1) + " completada.")
                    item = item + 1

            except Exception as e:
                print(f"Ocurrió un error al eliminar registros en la tabla {nombre_tabla}. Favor de validar que el formato JSON de DynamoDB válido y la Partition Key exista.")
            

    def tabla_tag(nombre_tabla):
        '''Agrega tags predefinidos a la tabla.'''
        
        # Obtener ARN de la tabla
        response = dynamo.describe_table(TableName=nombre_tabla)
        ARN_tabla = response['Table']['TableArn']
        
        # Se agregan tags a la tabla
        response = dynamo.tag_resource(
            ResourceArn=ARN_tabla,
            Tags=[{"Key": "Proyecto", "Value": "{{cookiecutter.project|upper}}"},])
                                 
    def crear_tabla_global(nombre_tabla):
        '''Crea tabla global a partir del nombre de la tabla mencionada.'''
        try:    
            print("Se comienza creación tabla global de tabla de origen.")
            response = dynamo.update_table(
                TableName=nombre_tabla,
                ReplicaUpdates=[
                        {
                            'Create': {
                                'RegionName': '{{cookiecutter.region_secundaria}}',
                            },
                        },
                    ]
                    )
            response
            print(f"La petición para convertir la tabla {nombre_tabla} ha sido enviada correctamente. Favor de validar en DynamoDB")
        except Exception as e:
            print(e)
            print("La tabla ya cuenta con una tabla global.")

    # Orden de funciones

    validar_existencia_tablas(lista_tablas.lista_tablas_json)

    conversion_json()

    crear_tabla(validar_existencia_tablas.lista_tablas_inexistentes, nombre_tabla)

    respaldos_tablas(nombre_tabla)

    insercion_json(nombre_tabla)

    if nombre_tabla in lista_tablas.lista_tablas_json:
        eliminaciones(nombre_tabla)

    tabla_tag(nombre_tabla)

    crear_tabla_global(nombre_tabla)

# Orden de funciones previas a la función madre.
lista_tablas()

ambiente_por_extension()

for nombres_tablas in lista_tablas.lista_tablas_json:

    print("!--------------------------------------------------!")
    print(f"Tabla en proceso: {nombres_tablas}")
    print("!--------------------------------------------------!")
    funcion_madre(nombres_tablas)
