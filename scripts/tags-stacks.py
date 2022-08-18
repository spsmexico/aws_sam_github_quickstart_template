import pytz
import argparse
import jmespath
import boto3

global args

parser = argparse.ArgumentParser()

parser.add_argument(
    "-p",
    "--region_primaria",
    required=False,
    action="store",
    dest="region_primaria",
    help="Región de AWS primaria (A apagar)",
    default=None,
)
parser.add_argument(
    "-s",
    "--region_secundaria",
    required=False,
    action="store",
    dest="region_secundaria",
    help="Región de AWS secundaria (A encender)",
    default=None,
)
parser.add_argument(
    "-a",
    "--ambiente",
    required=False,
    action="store",
    dest="ambiente",
    help="Sufijo de ambiente principal.",
    default=None,
)

parser.add_argument(
    "-adr",
    "--ambiente-dr",
    required=False,
    action="store",
    dest="ambientedr",
    help="Sufijo de ambiente para DR.",
    default=None,
)

parser.add_argument(
    "-st",
    "--stack",
    required=False,
    action="store",
    dest="stack",
    help="Nombre del stack",
    default=None,
)

parser.add_argument(
    "-stdr",
    "--stack-dr",
    required=False,
    action="store",
    dest="stackdr",
    help="Nombre del stack DR",
    default=None,
)

args = parser.parse_args()

REGION_PRIMARIA = args.region_primaria
REGION_SECUNDARIA = args.region_secundaria
AMBIENTE = args.ambiente
AMBIENTE_DR = args.ambiente
NOMBRE_STACK = args.stack
NOMBRE_STACK_DR = args.stackdr

#Se crean sesiones con las diferentes regiones
session = boto3.Session(region_name=REGION_PRIMARIA)
session_dr = boto3.Session(region_name=REGION_SECUNDARIA)

cloudformation_primario = client = session.client('cloudformation')
cloudformation_secundario = client = session_dr.client('cloudformation')


def obtener_version(session_ambiente, stack):
    '''Función que obtiene Tags de Cloudformation.'''

    nombre_stack = stack
    response = session_ambiente.describe_stacks(
        StackName=nombre_stack
    )

    tags = response["Stacks"][0]

    tag = jmespath.search("Tags[?Key == `version`].Value", tags)

    return tag[0]

def obtener_ultima_actualizacion(session_ambiente, stack):
    '''Función que obtiene última actualización del stack de Cloudformation.'''

    nombre_stack = stack
    response = session_ambiente.describe_stacks(StackName=nombre_stack)
    try:
        fecha_actualizacion = response["Stacks"][0]["LastUpdatedTime"]
        fecha_actualizacion = fecha_actualizacion.astimezone(pytz.timezone('America/Mexico_City'))
    except:
        fecha_actualizacion = "No se pudo obtener fecha de última actualización. Posiblemente acaba de ser creado."
    return fecha_actualizacion

version_primaria = obtener_version(cloudformation_primario, NOMBRE_STACK)
version_secundaria = obtener_version(cloudformation_secundario, NOMBRE_STACK_DR)

actualizacion_primaria = obtener_ultima_actualizacion(cloudformation_primario, NOMBRE_STACK)
actualizacion_secundaria = obtener_ultima_actualizacion(cloudformation_secundario, NOMBRE_STACK_DR)

if version_primaria == version_secundaria:
    print("OK. Las versiones coinciden.\n")
    print(f"Nombre de Stack: {NOMBRE_STACK}")
    print(f"La versión de Virginia es: {version_primaria}")
    print(f"Fecha de última actualización Stack Virginia: {actualizacion_primaria}\n")

    print(f"Nombre de Stack DR: {NOMBRE_STACK_DR}")
    print(f"La versión de Oregón es: {version_secundaria}")
    print(f"Fecha de última actualización Stack Oregón: {actualizacion_secundaria}")

else:
    print("Las versiones no coinciden.")
    print(f"Nombre de Stack: {NOMBRE_STACK}")
    print(f"La versión de Virginia es: {version_primaria}")
    print(f"Fecha de última actualización Stack Virginia: {actualizacion_primaria}\n")

    print(f"Nombre de Stack DR: {NOMBRE_STACK_DR}")
    print(f"La versión de Oregón es: {version_secundaria}")    
    print(f"Fecha de última actualización Stack Oregón: {actualizacion_secundaria}")
    exit(1)
    