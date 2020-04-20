#!/bin/bash
echo "[Loading environment variables]"
export $(cat .env | sed 's/#.*//g' | xargs)
echo
echo "[Creating CDR_FOLDER]"
mkdir -p $CDR_FOLDER
echo "[Download latest CDR]"
python3 download_latest_cdr.py
echo
echo "[Process CDR to CSV]"
python3 process_cdr_csv.py
echo
echo "[Moving new standard data into elasticsearch]"
elasticsearch_loader \
		--bulk-size 500 \
		--es-host http://localhost:9200 \
		--index standard \
		--index-settings-file ./es_standard_index.json \
		--delete \
		--progress \
		csv ./standard.csv
echo
echo "[Moving new queue data into elasticsearch]"
elasticsearch_loader \
		--bulk-size 500 \
		--es-host http://localhost:9200 \
		--index-settings-file ./es_queue_index.json \
		--index queue \
		--delete \
		--progress \
		csv ./queue.csv
echo
echo "[Deleting CDR_FOLDER]"
rm -Rf $CDR_FOLDER
echo
echo "[DONE]"