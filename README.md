# Sistema BDI con algoritmos genéticos

## Resumen

En este repositorio se ha guardado un trabajo académico de sistemas multiagente mejorados y optimizados con algoritmos genéticos. Este sistema multiagente esta inspirado en un entorno parecido al juego de XCOM. El repositorio tiene cuatro carpetas principales:
* __/data__: Aqui se guardan los datos de los experimentos según el nombre del fichero que se le haya dado al programa
* __/server__: Aqui se guardan todos los archivos relacionados con el servidor
* __/src__: Aqui se encuentra el modulo principal xcomagents que es el que ejecuta todo el codigo
* __/tests__: Aqui se encuentran los unittest con respecto a la libreria de geneticos
## Requisitos

En primer lugar hace falta tener instalado docker para poder correr el servidor de prosody. El repositorio esta pensado para ser usado en linux, por lo que es recomendable tenerlo. Además de esto hace falta un entorno de python que se puede construir a partir del requirements.txt proporcionado. Por último hacen falta un par de certificados para la comunicacion TLS de los agentes y el servidor prosody.

## Instalacion y ejecucion

### Creacion de los certificados
Primero se crean los certificados para ello primero se crea la clave privada
```
openssl genrsa -out localhost.key 2048

```
a partir de esta key se genera un certificado autofirmado

```
openssl req -new -x509 -key localhost.key -out localhost.crt -days 365

```
Tras haber creado estos dos items, deberán guardarse dentro de __/server/certs__ si no esta creada la carpeta, deberá crearse. Ambos tienen que tener el nombre de localhost (localhost.crt, localhost.key)

### Creacion de server prosody

Para ello solo es necesario acceder a __/server__ y ejecutar 
```
docker compose up -d
```
Esto, si se han metido correctamente los certificados, creara el servidor prosody con todas las cuentas creadas ya dentro. Si no, se facilita un script "create_users.sh" para crear todas las cuentas de los agentes.

### Ejecucion del script

En primer lugar debe crearse un entorno de ejecucion a través del requirements.txt proporcionado. Para ello
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
Con esto activado, se puede ir dentro de **/src/xcomagents** y entrar en el archivo __main. Aqui puedes cambiar los parametros del algoritmo genetico. Una vez elijas los deseados solo tienes que situarte en la carpeta __/src__ y ejecutar
```
python3 -m xcomagents
```

## Correr los tests

Por último si se desean correr los test, solo hay que situarse en la raiz del proyecto y ejecutar 
```
pytest
```
Esto proporcionara el resultado de los tests