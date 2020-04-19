# cdr-parser
Parseador de archivos CDR generados por centrales teléfonicas

## Uso rápido para descargar los CDR desde S3

Crear un archivo `.env` con las siguientes variables:

```ini
BUCKET_NAME=my-s3-bucket
FOLDER_PREFIX=my-s3-bucket-folder-prefix
CDR_FOLDER=my-cdr-dump-folder
```
Esta es una lista de todas las variables que se pueden configurar:

| Nombre | Descripción 
| --- | --- |
| `BUCKET_NAME` | Nombre del bucket de S3 desde donde descargar los CBR. |
| `FOLDER_PREFIX` | Carpeta dentro del bucket de S3 donde se encuentran los CBR. |
| `CDR_FOLDER` | Carpeta donde se almacenarán los CDR descargados. |
| `MARKER` | Objeto de S3 desde donde comenzar el listado de CBR. |

Se incluyen una serie de scripts escritos en `python` para parsear rápidamente los CDR y descargar los CDR desde S3.
El script `download_latest_cbr.py` hace exacamente eso, descarga los últimos CBR. Toma como punto de partida el último
objeto descargado de S3. También se puede llamar al script pasandole un prefijo de objeto para utilizar. Por ejemplo:

```bash
python download_latests_cdr.py osv2-20200417
```

## Elasticsearch y Kibana

Se incluyen un par de tareas para levantar `elasticsearch` y `kibana` en contenedores.
