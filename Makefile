.PHONY: elasticsearch

elasticsearch:
	docker run -d --name elasticsearch \
		-p 9200:9200 \
		-p 9300:9300 \
		--restart unless-stopped \
		-e "discovery.type=single-node"\
		 elasticsearch:7.6.2

kibana:
	docker run -d --name kibana \
		--restart unless-stopped \
		--link elasticsearch:elasticsearch \
		-p 5601:5601 \
		docker.elastic.co/kibana/kibana:7.6.2