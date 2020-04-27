#!/bin/bash

echo "[[ Running update cdr task for: $(date) ]]"
echo
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
echo "[Process CDR to calls summary CSV]"
python3 process_cdr_calls_summary.py
echo "[Moving new standard data into elasticsearch]"
elasticsearch_loader \
		--bulk-size 500 \
		--es-host http://localhost:9200 \
		--index standard \
		--progress \
		csv ./standard.csv
echo
echo "[Moving new queue data into elasticsearch]"
elasticsearch_loader \
		--bulk-size 500 \
		--es-host http://localhost:9200 \
		--index queue \
		--progress \
		csv ./queue.csv
echo "[Moving new standard call summary data into elasticsearch]"
elasticsearch_loader \
		--bulk-size 500 \
		--es-host http://localhost:9200 \
		--index std-calls-summary \
		--progress \
		csv ./standard_calls_summary.csv
echo
echo "[Deleting CDR_FOLDER]"
rm -Rf $CDR_FOLDER
rm *.csv || true
echo
echo "[DONE]"
