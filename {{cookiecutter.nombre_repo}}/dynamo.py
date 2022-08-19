# flake8: noqa

import os
import sys
import time
import datetime
import json
from operator import contains, truediv
from os import walk

import json
import uuid
import boto3
import pandas
import numpy as np
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

nombre_tabla_estructura = f"sia-gen-adm-estructura-catalogos{ambiente}"

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
    tabla-registros-prueba.csv -> tabla-registros-prueba-pre
    tabla-registros-prueba.json -> tabla-registros-prueba-pre
    '''

    separacion_tablas.lista_tablas_csv = [w.replace(".csv", ambiente) for w in separacion_tablas.lista_tablas_csv]
    separacion_tablas.lista_tablas_json = [w.replace(".json", ambiente) for w in separacion_tablas.lista_tablas_json]

def union_lista_tablas():
    '''
    Crea una lista de tablas que contiene todas las tablas, tanto provenientes de CSV o de JSON.

    En caso de que dentro de esta lista se encuentre el nombre de la tabla de estructura catálogos.
    Será ordenada al principio de la lista, para que pueda ser modificada su estructura antes de
    realizar inserciones por CSV.
    '''

    separacion_tablas.lista_tablas_todas = separacion_tablas.lista_tablas_csv + separacion_tablas.lista_tablas_json    
    # En caso de que esté el nombre de la tabla de estructura dentro de las listas se envía ese elemento
    # al principio de la lista.
    if nombre_tabla_estructura in separacion_tablas.lista_tablas_todas:
        separacion_tablas.lista_tablas_todas.insert(0, separacion_tablas.lista_tablas_todas.pop(separacion_tablas.lista_tablas_todas.index(nombre_tabla_estructura)))


def validacion_tablas_prohibidas():
    '''
    Valida que la tabla a la que se le vayan a insertar valores 
    no sea de auditoría ni de checklist ni tareas programadas.
    '''
    for tablas in separacion_tablas.lista_tablas_csv:
        if "-aud-" in tablas:
            print("No es posible insertar valores en tablas de auditoría.")
            exit(1)

def funcion_madre(nombre_tabla):
    """Controla el flujo de funciones que realizan la validación e inserción."""
    
    # Se declaran tablas sin ambiente para usos al momento de dirigirse a items o archivos csv o json.
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


    def existe_item(tablas_estructura):
        """Consulta la existencia de un valor en una tabla de dynamo."""

        print(
            "\n#-------------------------------------------------------------------------------#"
        )
        print(f"Validando existencia de item en: {tablas_estructura}")

        try:
            response = dynamo.query(
                ExpressionAttributeValues={
                    ":v1": {
                        "S": nombre_tabla_sin_ambiente,
                    },
                },
                KeyConditionExpression="NOMBRE = :v1",
                TableName=tablas_estructura,
            )

            query = response["Items"]

            if query != []:
                print(
                    f"Se encontró {nombre_tabla_sin_ambiente} listada en los items de la tabla: {tablas_estructura}"
                )
                existe_item.tablas_validadoras = dynamo.scan(
                    TableName=tablas_estructura
                )
                return True

            if query == []:
                print(
                    f"No se encontró {nombre_tabla_sin_ambiente} listada en los items de la tabla de estructura."
                )
                exit(1)

        except Exception as e:
            print(e)

    def conversion_csv():
        """Función que permite convertir archivos csv en diccionarios."""

        print("Conversión CSV")
        df = pandas.read_csv(ruta_tablas + "/" + nombre_tabla_sin_ambiente + ".csv")

        # Se eliminan los renglones y columnas en las que todos los campos sean NaN
        df.dropna(how="all")

        # Se reemplazan valores nan en dataframe.
        df = df.replace(to_replace=np.nan, value="")
        #df = df.reindex(sorted(df.columns), axis=1)
        print("Dataframe:")
        print(df)
        # Se convierte dataframe en diccionario.
        conversion_csv.diccionario_csv = df.to_dict()
        # Se ordena diccionario convertido:
        print("Conversión:")
        conversion_csv.diccionario_csv = dict(sorted(conversion_csv.diccionario_csv.items()))
        print(conversion_csv.diccionario_csv)
        print("Termina conversión CSV")
        
    def validador_estructura():
        """Crea un diccionario formado por la estructura a seguir de la tabla en cuestión."""

        validador_estructura.diccionarioValidador = {}
        result = None
        columnas_tipo_dato = 0

        while result is None:
            try:
                # Con esto obtenemos el tipo de dato dependiendo del nombre del campo

                validador_estructura.item_estructura = 0
                tabla = existe_item.tablas_validadoras["Items"][
                    validador_estructura.item_estructura
                ]["NOMBRE"]["S"]

                while tabla != nombre_tabla_sin_ambiente:
                    validador_estructura.item_estructura = (
                        validador_estructura.item_estructura + 1
                    )
                    tabla = existe_item.tablas_validadoras["Items"][
                        validador_estructura.item_estructura
                    ]["NOMBRE"]["S"]
                validador_estructura.item_estructura = (
                    validador_estructura.item_estructura
                )
                campo = existe_item.tablas_validadoras["Items"][
                    validador_estructura.item_estructura
                ]["ESTRUCTURA"]["L"][columnas_tipo_dato]["M"]["campo"]["S"]
                tipo_dato = existe_item.tablas_validadoras["Items"][
                    validador_estructura.item_estructura
                ]["ESTRUCTURA"]["L"][columnas_tipo_dato]["M"]["tipo"]["S"]
                # print(validador_estructura.diccionarioValidador)
                validador_estructura.diccionarioValidador.update({campo: tipo_dato})
                columnas_tipo_dato = columnas_tipo_dato + 1
            except Exception as e:
                # print(e)
                result = "OK"
                print("\n#-----------------------------#")
                print("Se concluyó captura de validación.")
                print("#-----------------------------#")

    def impresion_llaves():
        '''Se obtienen las llaves tanto del diccionario validador, como del CSV con la finalidad de logueo.'''
        print(
            "\n#-------------------------------------------------------------------------#"
        )
        print("Llaves de diccionario validador:")
        print(f"Total: {len(validador_estructura.diccionarioValidador.keys())}")
        print(validador_estructura.diccionarioValidador)
        print(
            "\n#-------------------------------------------------------------------------#"
        )
        print("Llaves de diccionario de CSV:")
        print(f"Total: {len(conversion_csv.diccionario_csv.keys())}")
        print(
            "----------------------------------------------------------------------------#"
        )

    def validador_numero_columnas():
        """
        Valida el número de columnas del diccionario de estructura vs el diccionario validador.
        En caso de no coincidir, detiene la ejecución del programa.
        """

        if len(conversion_csv.diccionario_csv.keys()) > len(
            validador_estructura.diccionarioValidador.keys()
        ):
            print("\nError...")
            print(
                """
                El número de columnas es MAYOR a la tabla de estructura.
                Actualizar tabla de estructura antes.
                """
            )
            exit(1)
        elif len(conversion_csv.diccionario_csv.keys()) < len(
            validador_estructura.diccionarioValidador.keys()
        ):
            print("\nError...")
            print(
                """
                El número de columnas es MENOR a la tabla de estructura.
                Actualizar tabla de estructura antes.
                """
            )
            exit(1)

    def lectura_diccionarios():
        """Convierte los diccionarios en listas para leer columnas, filas y profundidad de los csv."""

        # - - - - Lista de valores que se insertarán.
        lectura_diccionarios.encabezadosCSV = []
        lectura_diccionarios.filasCSV = []
        lectura_diccionarios.profundidad = []

        for encabezado, fila in conversion_csv.diccionario_csv.items():
            lectura_diccionarios.encabezadosCSV.append(encabezado)
            lectura_diccionarios.filasCSV.append(fila)
            for profundidad in fila:
                lectura_diccionarios.profundidad.append(profundidad)

        # - - - - Lista diccionario que validará.
        lectura_diccionarios.valoresValidadores = []
        lectura_diccionarios.llavesValidadores = []

        for llave, valores in validador_estructura.diccionarioValidador.items():
            lectura_diccionarios.llavesValidadores.append(llave)
            lectura_diccionarios.valoresValidadores.append(valores)

        # Se elimina duplicidad de lista Profundidad.
        lectura_diccionarios.profundidad = list(
            dict.fromkeys(lectura_diccionarios.profundidad)
        )

    def obtener_llave_primaria():
        """Se obtiene la llave primaria desde la tabla de estructura correspondiente."""

        columnas_tipo_dato = 0
        obtener_llave_primaria.llave_primaria = existe_item.tablas_validadoras["Items"][
            validador_estructura.item_estructura
        ]["ESTRUCTURA"]["L"][columnas_tipo_dato]["M"]["llavePrimaria"]["BOOL"]

        # print(f"El bool es: {type(obtener_llave_primaria.llave_primaria)}")

        while obtener_llave_primaria.llave_primaria == False:
            columnas_tipo_dato = columnas_tipo_dato + 1
            obtener_llave_primaria.llave_primaria = existe_item.tablas_validadoras[
                "Items"
            ][validador_estructura.item_estructura]["ESTRUCTURA"]["L"][
                columnas_tipo_dato
            ][
                "M"
            ][
                "llavePrimaria"
            ][
                "BOOL"
            ]

        obtener_llave_primaria.llave_primaria = existe_item.tablas_validadoras["Items"][
            validador_estructura.item_estructura
        ]["ESTRUCTURA"]["L"][columnas_tipo_dato]["M"]["campo"]["S"]
        
        obtener_llave_primaria.tipo_dato_llave_primaria = existe_item.tablas_validadoras["Items"][
            validador_estructura.item_estructura
        ]["ESTRUCTURA"]["L"][columnas_tipo_dato]["M"]["tipo"]["S"]
        
        print(f"La llave primaria es: {obtener_llave_primaria.llave_primaria}")

    def validador_nombre_columnas():
        """
        Valida que el nombre de las columnas coincida.

        Ordena las listas de los encabezados del csv y de la tabla de estructura
        y verifica que sus nombres coincidan. Caso contrario se detiene la ejecución
        del script.
        """

        # Se ordenan las listas antes de convertirse a string
        validador_nombre_columnas.llaves = sorted(
            lectura_diccionarios.llavesValidadores
        )
        validador_nombre_columnas.encabezados = sorted(
            lectura_diccionarios.encabezadosCSV
        )
        validador_nombre_columnas.llaves.insert(
            0,
            validador_nombre_columnas.llaves.pop(
                validador_nombre_columnas.llaves.index(
                    obtener_llave_primaria.llave_primaria
                )
            ),
        )
        validador_nombre_columnas.encabezados.insert(
            0,
            validador_nombre_columnas.encabezados.pop(
                validador_nombre_columnas.encabezados.index(
                    obtener_llave_primaria.llave_primaria
                )
            ),
        )
        print(validador_nombre_columnas.llaves)
        print(validador_nombre_columnas.encabezados)

        print(
            "\n---------------------------------------------------------------------------#"
        )
        print("Las llaves validadoras son: " + str(validador_nombre_columnas.llaves))
        print("----------------------------#")
        print(
            "Los encabezados del CSV son: " + str(validador_nombre_columnas.encabezados)
        )
        print("\n")

        if validador_nombre_columnas.llaves != validador_nombre_columnas.encabezados:
            print("Las llaves no coinciden")
            exit(1)
        print("Las llaves coinciden. Se continúa proceso.")
        print(
            "---------------------------------------------------------------------------#"
        )

    def conversion_json():
        '''En caso de que la tabla sea tipo JSON la convierte en diccionario para Python usando json loads.'''
        
        if nombre_tabla in separacion_tablas.lista_tablas_json:
            with open(f'{ruta_tablas}{nombre_tabla_sin_ambiente}.json', 'r') as myfile:
                data=myfile.read()
                conversion_json.archivo = json.loads(data)

    def crear_tabla(tablas_inexistentes, tabla_a_crear):
        """Crea la tabla si está en la lista de tablas inexistentes.
        
        Busca su estructura en la tabla de estructura correspondiente y basado en ello toma
        los tipos de dato para cada atributo.
        Al momento de su creación, revisa su estatus. La función termina hasta que el estatus
        de la tabla a crear sea ACTIVO.
        """


        # Dependiendo de la lista se usa la llave primaria y tipo de dato de llave primaria.
        if tabla_a_crear in separacion_tablas.lista_tablas_json:
        
            # Se toma la primera llave del diccionario a insertar como PK. Y el tipo de esa PK.
            diccionario = conversion_json.archivo['Actualizaciones'][0]
            llave_primaria = list(diccionario.keys())[0]
            tipo_dato_llave_primaria = list(diccionario[llave_primaria])[0]

        if tabla_a_crear in separacion_tablas.lista_tablas_csv:
            llave_primaria = obtener_llave_primaria.llave_primaria
            tipo_dato_llave_primaria = obtener_llave_primaria.tipo_dato_llave_primaria
            print(tabla_a_crear)


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
    
    def insercion_csv():
        """Crea el diccionario a insertarse y ejecuta la inserción.

        Forma un diccionario basado en los encabezados, filas y profundidad.
        A su vez se les asigna el tipo de dato correspondiente a cada columna.
        Al finalizar, utiliza el método put_item por cada fila del csv

        """

        item_a_insertar = {}

        longitud_encabezado = len(validador_nombre_columnas.encabezados)
        longitud_profundidad = len(lectura_diccionarios.profundidad)

        print(f"Total de elementos a insertarse: {longitud_profundidad}")
        print(
            "#--------------------------------------------------------------------------------#"
        )
        inserciones = 0
        print(
            "#------------------------COMENZANDO INSERCIÓN.-------------------------------#"
        )
        while inserciones != longitud_profundidad:

            contador_listas = 0

            while contador_listas != longitud_encabezado:
                atributo = validador_nombre_columnas.encabezados[contador_listas]

                valor = conversion_csv.diccionario_csv[atributo][inserciones]

                # Del diccionario validador se obtienen los tipos de dato correspondientes.
                
                # Validaciones para convertir valor a insertar dependiendo el tipo de dato.
                
                tipo_dato = validador_estructura.diccionarioValidador
                                        
                if tipo_dato[atributo] == "S":
                    valor = str(valor)
                if tipo_dato[atributo] == "L":
                    valor = str(valor)
                if tipo_dato[atributo] == "M":
                    valor = str(valor)
                if tipo_dato[atributo] == "N":
                    valor = str(valor)
                    if valor == "":
                        print("Error. DynamoDB no acepta valores numéricos vacíos.")
                        exit(1)

                
                item_a_insertar[atributo] = {tipo_dato[atributo]: valor}

                contador_listas = contador_listas + 1

                if contador_listas == longitud_encabezado:
                    print("Diccionario a insertar:")
                    print(item_a_insertar)

                    # ------------------Inserción de valores en DYNAMO
                    response = dynamo.put_item(
                        TableName=nombre_tabla, Item=item_a_insertar
                    )
                    response
                    print("Inserción #" + str(inserciones + 1) + " completada.")

            inserciones = inserciones + 1

        print(
            "#-------------------------FIN DE INSERCION.----------------------------------#"
        )
    
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
            

    def insercion(nombre_tabla):
        '''
        Dependiendo del origen de la tabla es su inserción.
        
        Si proviene desde la lista de tablas JSON o desde CSV.
        '''
        
        if nombre_tabla in separacion_tablas.lista_tablas_json:
            insercion_json(nombre_tabla)
        elif nombre_tabla in separacion_tablas.lista_tablas_csv:
            insercion_csv()

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
                                'RegionName': 'us-west-2',
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

    validar_existencia_tablas(separacion_tablas.lista_tablas_todas)

    if nombre_tabla not in separacion_tablas.lista_tablas_json:
        
        existe_item(nombre_tabla_estructura)

        conversion_csv()

        validador_estructura()

        impresion_llaves()

        validador_numero_columnas()

        lectura_diccionarios()

        obtener_llave_primaria()
    
        validador_nombre_columnas()

    conversion_json()

    crear_tabla(validar_existencia_tablas.lista_tablas_inexistentes, nombre_tabla)

    respaldos_tablas(nombre_tabla)

    # Se aplican eliminaciones sólo para archivos JSON.
    if nombre_tabla in separacion_tablas.lista_tablas_json:
        eliminaciones(nombre_tabla)

    insercion(nombre_tabla)

    tabla_tag(nombre_tabla)

    crear_tabla_global(nombre_tabla)

# Orden de funciones previas a la función madre.
lista_tablas()

separacion_tablas()

ambiente_por_extension()

union_lista_tablas()

validacion_tablas_prohibidas()

for nombres_tablas in separacion_tablas.lista_tablas_todas:

    print("!--------------------------------------------------!")
    print(f"Tabla en proceso: {nombres_tablas}")
    print("!--------------------------------------------------!")
    funcion_madre(nombres_tablas)
