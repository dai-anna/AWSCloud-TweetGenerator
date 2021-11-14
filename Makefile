install:
	pip install --upgrade pip
	pip install -r requirements.txt

run-frontend:
	uvicorn --app-dir application/ app:app --reload --host 0.0.0.0 --port 8080

docker-build:
	cp requirements.txt ./scripts/scrape-tweets/requirements.txt
	docker build -t datacollector -f ./scripts/scrape-tweets/Dockerfile ./scripts/scrape-tweets/ --no-cache
	rm ./scripts/scrape-tweets/requirements.txt

docker-run:
	docker run -d --name datacollector --env-file scripts/scrape-tweets/env.list datacollector

docker-run-debug:
	docker run -it --name datacollector --env-file scripts/scrape-tweets/env.list datacollector
	
docker-clean:
	docker rm -f datacollector
	