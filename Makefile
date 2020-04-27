#!make
include .env
export $(shell sed 's/=.*//' .env)

.PHONY: run clean download-latest process-cdr-csv elasticsearch kibana es_load es_load_standard es_load_queue

run: clean download-latest process-cdr-csv es-load-standard es-load-queue

clean:
	rm -Rf $$CDR_FOLDER && `rm *.csv || true` && mkdir -p $$CDR_FOLDER

download-latest:
	python3 download_latest_cdr.py

process-cdr-csv:
	python3 process_cdr_csv.py

elasticsearch:
	docker run -d --name elasticsearch \
		-p 9200:9200 \
		-p 9300:9300 \
		--restart unless-stopped \
		-e "discovery.type=single-node" \
		elasticsearch:7.6.2

kibana:
	docker run -d --name kibana \
		--restart unless-stopped \
		--link elasticsearch:elasticsearch \
		-v '`pwd`/kibana.yml:/usr/share/kibana/config/kibana.yml'
		-p 5601:5601 \
		docker.elastic.co/kibana/kibana:7.6.2

es-load: es_load_standard es_load_queue

es-load-standard:
	elasticsearch_loader \
		--bulk-size 500 \
		--es-host http://localhost:9200 \
		--index standard \
		--index-settings-file ./es_standard_index.json \
		--delete \
		--progress \
		csv ./standard.csv

es-load-queue:
	elasticsearch_loader \
		--bulk-size 500 \
		--es-host http://localhost:9200 \
		--index-settings-file ./es_queue_index.json \
		--index queue \
		--delete \
		--progress \
		csv ./queue.csv

es-load-standard-calls-summary:
	elasticsearch_loader \
		--bulk-size 500 \
		--es-host http://localhost:9200 \
		--index-settings-file ./es_standard_calls_summary.json \
		--index std-calls-summary \
		--delete \
		--progress \
		csv ./standard_calls_summary.csv

