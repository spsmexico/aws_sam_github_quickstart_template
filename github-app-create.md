# Autenticar con una aplicación GitHub

Para utilizar una GitHub App para realizar solicitudes de API autenticadas, se debe registrar una GitHub App, almacenar las credenciales de la GitHub App e instalarse.
Una vez hecho esto, puede usar su aplicación para crear un token de acceso a la instalación, que puede usarse para realizar solicitudes de API autenticadas en un workflow de GitHub Actions. También puede pasar el token de acceso a la instalación a una acción personalizada que requiera un token.

Pasos:
I) Registre una aplicación GitHub. Otorgue a su registro de aplicación GitHub los permisos necesarios para acceder a los recursos deseados. Para obtener más información, consulte "Registrar una aplicación GitHub" y "Elegir permisos para una aplicación GitHub".

## Registrar una GitHub App: 
Fuente: https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/registering-a-github-app

1) En la esquina superior derecha de cualquier página de GitHub, haz clic en tu foto de perfil.

![](./assets/github_app/1-uninstall.png)

2) Daremos clic en "Your organizations".

![](./assets/github_app/2-uninstall.png)

3) A la derecha de la organización, haga clic en "Settings".

![](./assets/github_app/3-uninstall.png)

4) En la barra lateral izquierda, haga clic en "Developer settings". Luego en "GitHub Apps":

![](./assets/github_app/4-uninstall.png)

5) Haga clic en Nueva aplicación GitHub.

![](./assets/github_app/6-install.png)

6) En "Nombre de la aplicación GitHub", ingresa un nombre para tu aplicación. Debes elegir un nombre claro y corto. 
El nombre de su aplicación (convertido a minúsculas, con espacios reemplazados por - y con caracteres especiales reemplazados) se mostrará en la interfaz de usuario cuando su aplicación realice una acción. Por ejemplo, My APp Näme se mostraría como my-app-name.

7) El nombre debe ser único en GitHub. No puede utilizar el mismo nombre que una cuenta de GitHub existente, a menos que sea su propio nombre de usuario o de organización.

Opcionalmente, en "Descripción", escriba una descripción de su aplicación. Los usuarios y organizaciones verán esta descripción cuando instalen su aplicación.

![](./assets/github_app/7-install.png)

8) En "URL de la página de inicio", escribiremos la URL completa del sitio web de su aplicación. Si no tiene una URL dedicada y el código de su aplicación está almacenado en un repositorio público, puede usar esa URL del repositorio. O puede utilizar la URL de la organización o usuario propietario de la aplicación.
En este caso agregaremos la de SPS (la URL debe ser completa, en este caso https://spsolutions.com.mx/):

![](./assets/github_app/8-install.png)


9) Dejaremos marcada la expiración de tokens y desactivaremos el uso de un webhook:

![](./assets/github_app/9-install.png)


10) En "Permisos", elija los permisos que necesita su aplicación. Para cada permiso, seleccione el menú desplegable y haga clic en Solo lectura, Lectura y escritura o Sin acceso. Debes seleccionar los permisos mínimos necesarios para tu aplicación. Para obtener más información, consulta "Elegir permisos para una aplicación GitHub".

Actions = Read and Write
Contents = Read and Write
Metadata = Read-only

### Permisos para GitHub App:
https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/choosing-permissions-for-a-github-app

Por último, dejaremos marcado "Only on this account" para que nuestra app sea privada y daremos clic en el botón "Create GitHub App":

![](./assets/github_app/10-install.png)
---

## II) Usaremos el ID de la GitHub App para guardarla como un secreto de GitHub Actions. En este caso a nivel de la organización:

![](./assets/github_app/11-install.png)

## III) Generamos una clave privada para la GitHub App. Guarde el contenido del archivo resultante como secreto. (Almacene todo el contenido del archivo, incluidos -----BEGIN RSA PRIVATE KEY----- y -----END RSA PRIVATE KEY-----.) Para obtener más información, consulte ["Administración de claves privadas"](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/managing-private-keys-for-github-apps).
Para ello, en la misma consola de la GitHub App, en el fondo de esa página daremos clic en el botón "Generate a private key":

![](./assets/github_app/12-install.png)

Esto nos descargará la llave privada. Copiaremos el contenido de la llave y lo pegaremos como secreto a nivel de la organización.

Después de haber creado este par de secretos los veremos de la siguiente manera:

![](./assets/github_app/13-install.png)


## IV) Instalación de GitHub App en la organización 
Para ello le conderemos acceso a repositorio al que desee que acceda su flujo de trabajo. Para obtener más información, consulte "[Instalar su propia aplicación GitHub](https://docs.github.com/en/apps/using-github-apps/installing-your-own-github-app#installing-your-private-github-app-on-your-repository)".

En sí, dentro de la consola de la GitHub App daremos clic en "Install App" y luego en "Install":

![](./assets/github_app/14-install.png)

Le daremos permiso a todos los repositorios, para que puedan hacer uso de la GitHub App:

![](./assets/github_app/15-install.png)


V) Ahora, en el workflow reusable de GitHub Actions donde haremos uso de la GitHub App, crearemos un token de acceso a la instalación, que usaremos para realizar requests a la API de GitHub. Actualmente ya utlizamos una acción prefabricada.

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



# Probando el escenario:

Actualmente tenemos:

1 repositorio "master", el cual contiene un workflow reusable.
2 repositorios "slaves", los cuales llaman el workflow reusable de master.
Si aplicamos un cambio en el workflow reusable ubicado en el repo de DevOps_master. Los repositorios que lo llaman, también verán ese cambio en el workflow.
Para este caso en particular. Si hacemos cambios en el script que se encuentra en el workflow de DevOps_master, los otros repositorios también verán reflejado ese cambio, puesto que están obteniendo el script de este repo. 

Demo:

![](./assets/github_app/devops_master.gif)