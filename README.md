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

## Kibana scripted fields

```painless
if (doc.containsKey('end_time') || !doc['end_time'].empty) {
    return doc['end_time'].value.millis - doc['start_time'].value.millis
}
```

```json
2914: unable to parse date [time]
{"id":"id","time":"time","queue_id":"queue_id","start_time":"start_time","end_time":"end_time","abandon":"abandon","destination":"destination"}
18842: failed to parse field [start_time] of type [date] in document with id 'VQhklXEBpbPnjzp2IfDt'. Preview of field's value: 'None'
{"id":"00000000000000000000000000000000","time":"2020-04-03 20:24:31","start_time":"None","end_time":"2020-04-04 05:41:55","abandon":"0","destination":"59820303700"}
18843: failed to parse field [start_time] of type [date] in document with id 'VghklXEBpbPnjzp2IfDt'. Preview of field's value: 'None'
{"id":"00000000000000000000000000000000","time":"2020-04-03 20:24:40","start_time":"None","end_time":"2020-04-04 05:44:19","abandon":"0","destination":"59820303700"}
24995: failed to parse field [start_time] of type [date] in document with id 'XglklXEBpbPnjzp2Jgi5'. Preview of field's value: 'None'
{"id":"00000000000000000000000000000000","time":"2020-04-03 20:29:43","start_time":"None","end_time":"2020-04-03 20:31:43","abandon":"1"}
24996: failed to parse field [start_time] of type [date] in document with id 'XwlklXEBpbPnjzp2Jgi5'. Preview of field's value: 'None'
{"id":"00000000000000000000000000000000","time":"2020-04-03 20:29:43","start_time":"None","end_time":"2020-04-03 20:31:43","abandon":"1"}
25002: failed to parse field [start_time] of type [date] in document with id 'ZQlklXEBpbPnjzp2Kgi7'. Preview of field's value: 'None'
{"id":"00000000000000000000000000000000","time":"2020-04-03 20:29:31","start_time":"None","end_time":"2020-04-03 20:31:52","abandon":"1"}
26045: unable to parse date [time]
{"id":"id","time":"time","queue_id":"queue_id","start_time":"start_time","end_time":"end_time","abandon":"abandon","destination":"destination"}
41973: failed to parse field [start_time] of type [date] in document with id 'rwlklXEBpbPnjzp2N0rr'. Preview of field's value: 'None'
{"id":"00000000000000000000000000000000","time":"2020-04-03 20:24:31","start_time":"None","end_time":"2020-04-04 05:41:55","abandon":"0","destination":"59820303700"}
41974: failed to parse field [start_time] of type [date] in document with id 'sAlklXEBpbPnjzp2N0rr'. Preview of field's value: 'None'
{"id":"00000000000000000000000000000000","time":"2020-04-03 20:24:40","start_time":"None","end_time":"2020-04-04 05:44:19","abandon":"0","destination":"59820303700"}
48126: failed to parse field [start_time] of type [date] in document with id 'uAlklXEBpbPnjzp2PGIo'. Preview of field's value: 'None'
{"id":"00000000000000000000000000000000","time":"2020-04-03 20:29:43","start_time":"None","end_time":"2020-04-03 20:31:43","abandon":"1"}
48127: failed to parse field [start_time] of type [date] in document with id 'uQlklXEBpbPnjzp2PGIo'. Preview of field's value: 'None'
{"id":"00000000000000000000000000000000","time":"2020-04-03 20:29:43","start_time":"None","end_time":"2020-04-03 20:31:43","abandon":"1"}
48133: failed to parse field [start_time] of type [date] in document with id 'vwlklXEBpbPnjzp2PGIp'. Preview of field's value: 'None'
{"id":"00000000000000000000000000000000","time":"2020-04-03 20:29:31","start_time":"None","end_time":"2020-04-03 20:31:52","abandon":"1"}
```