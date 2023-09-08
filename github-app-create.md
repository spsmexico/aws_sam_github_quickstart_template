# Registro e instalación de una GitHub App a nivel organización

# Índice
1. [Introducción](#introduccion)
2. [Registro de GitHub App con permisos necesarios para acceder a contenido de otros repositorios](#registro-app-permisos)
    1. [Registrar una GitHub App](#registro-app)
    2. [Guardar ID de GitHub App en un secreto de GitHub Actions a nivel de la organización](#id-secreto-app)
    3. [Generar llave privada de GitHub App y guardarla como secreto a nivel de la organización](#generar-llave-privada)
    4. [Instalación de GitHub App en la organización](#instalar-app-org)
    5. [Generación de Token para peticiones a API de GitHub](#token-reusable)
3. [Probando GitHub App](#prueba-gh-app)
4. [Conclusiones y notas adicionales](#conclusiones)


## Introducción <a name="introduccion"></a>
Para utilizar una GitHub App para realizar solicitudes de API autenticadas, se debe registrar una GitHub App, almacenar las credenciales de la GitHub App e instalarse.
Una vez hecho esto, se puede usar la GitHub App para crear un token de acceso a la instalación, que puede usarse para realizar solicitudes de API autenticadas desde un workflow de GitHub Actions. También puede pasar el token de acceso a la instalación a una acción personalizada que requiera un token.


Fuente: https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/making-authenticated-api-requests-with-a-github-app-in-a-github-actions-workflow

Para nuestro caso de uso, la idea es desde un workflow de GitHub actions obtener un script ubicado en otro repositorio y ejecutarlo.

## I) Registro de GitHub App con permisos necesarios para acceder a contenido de otros repositorios <a name="registro-app-permisos"></a>

### Registrar una GitHub App: <a name="registro-app"></a>
Fuente: https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/registering-a-github-app

1) En la esquina superior derecha de cualquier página de GitHub, haz clic en tu foto de perfil.

![](./assets/github_app/1-uninstall.png)

2) Daremos clic en "Your organizations".

![](./assets/github_app/2-uninstall.png)

3) A la derecha de la organización, haremos clic en "Settings".

![](./assets/github_app/3-uninstall.png)

4) En la barra lateral izquierda, haga clic en "Developer settings". 
5) Luego en "GitHub Apps":

![](./assets/github_app/4-uninstall.png)

6) Daremos clic en "New GitHub App".

![](./assets/github_app/6-install.png)

7) En "GitHub App Name", ingresar un nombre para tu aplicación. Se debe elegir un nombre claro y corto. 
El nombre la GitHub App (convertido a minúsculas, con espacios reemplazados por - y con caracteres especiales reemplazados) se mostrará en la interfaz de usuario cuando su aplicación realice una acción. Por ejemplo, My APp Näme se mostraría como my-app-name.

El nombre debe ser único en GitHub. No puede utilizar el mismo nombre que una cuenta de GitHub existente, a menos que sea su propio nombre de usuario o de organización.

Opcionalmente, en "Descripción", escribiremos una descripción de su aplicación. Los usuarios y organizaciones verán esta descripción cuando instalen su aplicación.

![](./assets/github_app/7-install.png)

8) En "URL de la página de inicio", escribiremos la URL completa del sitio web de la GitHub App.
En este caso agregaremos la de SPS (la URL debe ser completa, en este caso https://spsolutions.com.mx/):

![](./assets/github_app/8-install.png)


9) Dejaremos marcada la expiración de tokens. 
10) Desactivaremos el uso de un webhook:

![](./assets/github_app/9-install.png)


10) En "Permisos", elegiremos los permisos necesarios para la GitHub App. Debemos seleccionar los permisos mínimos necesarios para tu aplicación. Para mayor información dar clic [aquí](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/choosing-permissions-for-a-github-app).
En nuestro caso solo necesitamos los siguientes:

```
Actions = Read and Write

Contents = Read and Write

Metadata = Read-only (este es obligatorio)
```

Por último, dejaremos marcado "Only on this account" para que nuestra GitHub App sea privada y daremos clic en el botón "Create GitHub App":

![](./assets/github_app/10-install.png)
---

## II) Usaremos el ID de la GitHub App para guardarla como un secreto de GitHub Actions. En este caso a nivel de la organización: <a name="id-secreto-app"></a>

![](./assets/github_app/11-install.png)

## III) Generamos una clave privada para la GitHub App. Guarde el contenido del archivo resultante como secreto. (Almacene todo el contenido del archivo, incluidos -----BEGIN RSA PRIVATE KEY----- y -----END RSA PRIVATE KEY-----.) Para obtener más información, consulte ["Administración de claves privadas"](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/managing-private-keys-for-github-apps). <a name="generar-llave-privada"></a>

Para ello, en la misma consola de la GitHub App, en el fondo de esa página daremos clic en el botón "Generate a private key":

![](./assets/github_app/12-install.png)

Esto nos descargará la llave privada. Copiaremos el contenido de la llave y lo pegaremos como secreto a nivel de la organización.

Después de haber creado este par de secretos los veremos de la siguiente manera:

![](./assets/github_app/13-install.png)

Nota: los nombres de los secretos pueden cambiar.

## IV) Instalación de GitHub App en la organización <a name="instalar-app-org"></a>
Para ello le concederemos acceso a repositorio al que desee que acceda su flujo de trabajo. Para obtener más información, consultar "[Instalar su propia aplicación GitHub](https://docs.github.com/en/apps/using-github-apps/installing-your-own-github-app#installing-your-private-github-app-on-your-repository)".

En sí, dentro de la consola de la GitHub App daremos clic en "Install App" y luego en "Install":

![](./assets/github_app/14-install.png)

Le daremos permiso a todos los repositorios, para que puedan hacer uso de la GitHub App:

![](./assets/github_app/15-install.png)


## V) Ahora, en el workflow reusable de GitHub Actions donde haremos uso de la GitHub App, crearemos un token de acceso a la instalación, que usaremos para realizar requests a la API de GitHub. Actualmente ya utlizamos una acción prefabricada. <a name="token-reusable"></a>

En este caso ya lo ajustamos para que use los secretos que previamente creamos a nivel de la organización:
```
      - name: Generate a token
        id: generate_token
        uses: tibdex/github-app-token@b62528385c34dbc9f38e5f4225ac829252d1ea92
        with:
          app_id: ${{ secrets.SPS_APP_ID }}
          private_key: ${{ secrets.SPS_APP_PRIVATE_KEY }}
```

En el repo de Devops_Master ya contamos con esta implementación:
https://github.com/spsdevops/DevOps_Master/blob/main/.github/workflows/reusable_get_file.yml



## Probando GitHub App <a name="prueba-gh-app"></a>

Actualmente tenemos:

```
1 repositorio "master", el cual contiene un workflow reusable.

2 repositorios "slaves", los cuales llaman el workflow reusable de master.
```
Si aplicamos un cambio en el workflow reusable ubicado en el repo de DevOps_master. Los repositorios que lo llaman, también verán ese cambio en el workflow.
Para este caso en particular. Si hacemos cambios en el script que se encuentra en el workflow de DevOps_master, los otros repositorios también verán reflejado ese cambio, puesto que están obteniendo el script de este repo. 

Demo:

![](./assets/github_app/devops_master.gif)



## Conclusiones y notas adicionales <a name="conclusiones"></a>

La fuente en la que está basada esta documentación es la siguiente:
https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/making-authenticated-api-requests-with-a-github-app-in-a-github-actions-workflow

1. La GitHub App se instala a nivel organizacional para que pueda ser utilizada por múltiples repositorios que estén en ella.
Si solo se le da acceso a algunos repositorios, cada que se agregue uno se le tendría que dar acceso para que pueda usar la GitHub App. En este caso a los repositorios "llamadores" que llaman al reusable.
2. Tiene que configurarse el APP_ID y el APP_SECRET_KEY de la app a nivel de la org.
Puede configurarse repositorio por repositorio. Pero eso sería más tedioso de administrar.
3. Se tuvo que habilitar permitir llamar los reusables en en el repositorio master:
https://stackoverflow.com/questions/72613210/error-parsing-called-workflow-in-github-workflow-was-not-found
Esto es un escenario normal cuando se utilizan workflows reusables.

Recursos adicionales:
GET file from repo REST API GitHub: 
https://docs.github.com/en/rest/repos/contents?apiVersion=2022-11-28#get-repository-content

https://docs.github.com/en/rest/overview/permissions-required-for-github-apps?apiVersion=2022-11-28

