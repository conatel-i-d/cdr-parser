.PHONY: elasticsearch kibana es_load es_load_standard es_load_queue

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
		-p 5601:5601 \
		docker.elastic.co/kibana/kibana:7.6.2

es_load: es_load_standard es_load_queue

es_load_standard:
	elasticsearch_loader \
		--bulk-size 500 \
		--es-host http://localhost:9200 \
		--index standard \
		--index-settings-file ./es_standard_index.json \
		--delete \
		--progress \
		csv ./standard.csv

es_load_queue:
	elasticsearch_loader \
		--bulk-size 500 \
		--es-host http://localhost:9200 \
		--index-settings-file ./es_queue_index.json \
		--index queue \
		--delete \
		--progress \
		csv ./queue.csv

