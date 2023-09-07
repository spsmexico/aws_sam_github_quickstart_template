## Autenticar con una aplicación GitHub

Para utilizar una GitHub  App para realizar solicitudes de API autenticadas, se debe registrar una GitHub App, almacenar las credenciales de la GitHub App e instalarse.
Una vez hecho esto, puede usar su aplicación para crear un token de acceso a la instalación, que puede usarse para realizar solicitudes de API autenticadas en un workflow de GitHub Actions. También puede pasar el token de acceso a la instalación a una acción personalizada que requiera un token.

Pasos:
1) Registre una aplicación GitHub. Otorgue a su registro de aplicación GitHub los permisos necesarios para acceder a los recursos deseados. Para obtener más información, consulte "Registrar una aplicación GitHub" y "Elegir permisos para una aplicación GitHub".

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

## Permisos para GitHub App:
https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/choosing-permissions-for-a-github-app

Por último, dejaremos marcado "Only on this account" para que nuestra app sea privada y daremos clic en el botón "Create GitHub App":

![](./assets/github_app/10-install.png)


---



2) Guarde el ID de su aplicación GitHub como un secreto de GitHub Actions. Puede encontrar el ID de la aplicación en la página de configuración de su aplicación. El ID de la aplicación es diferente del ID del cliente. Para obtener más información sobre cómo navegar a la página de configuración de su aplicación GitHub, consulte "Modificar el registro de una aplicación GitHub". Para obtener más información sobre cómo almacenar secretos, consulta "Usar secretos en GitHub Actions".

3) Genera una clave privada para tu aplicación. Guarde el contenido del archivo resultante como secreto. (Almacene todo el contenido del archivo, incluidos -----BEGIN RSA PRIVATE KEY----- y -----END RSA PRIVATE KEY-----.) Para obtener más información, consulte "Administración de claves privadas". para aplicaciones GitHub."

4) Instale la aplicación GitHub en su cuenta de usuario u organización y concédale acceso a cualquier repositorio al que desee que acceda su flujo de trabajo. Para obtener más información, consulte "Instalar su propia aplicación GitHub".

5) En su flujo de trabajo de GitHub Actions, cree un token de acceso a la instalación, que puede usar para realizar solicitudes de API.

6) Para hacer esto, puede utilizar una acción prefabricada como se demuestra en el siguiente ejemplo. Si prefiere no utilizar una acción de terceros, puede bifurcar y modificar la acción tibdex/github-app-token, o puede escribir un script para que su flujo de trabajo cree un token de instalación manualmente. Para obtener más información, consulte "Autenticación como instalación de una aplicación GitHub".

7) El siguiente flujo de trabajo de ejemplo utiliza la acción tibdex/github-app-token para generar un token de acceso a la instalación. Luego, el flujo de trabajo utiliza el token para realizar una solicitud de API a través de la CLI de GitHub.

8) En el siguiente flujo de trabajo, reemplace APP_ID con el nombre del secreto donde almacenó su ID de aplicación. Reemplace APP_PRIVATE_KEY con el nombre del secreto donde almacenó la clave privada de su aplicación.