install:
	pip install --upgrade pip
	pip install -r requirements.txt

run-frontend:
	uvicorn --app-dir application/ app:app --reload --host 0.0.0.0 --port 8080

test: install
	pytest tests/

################################ DOCKER #######################################
# Data Collection
docker-build:
	cp requirements.txt ./scripts/scrape-tweets/requirements.txt
	docker build -t datacollector -f ./scripts/scrape-tweets/Dockerfile ./scripts/scrape-tweets/ 
	rm ./scripts/scrape-tweets/requirements.txt

docker-build-push:
	cp requirements.txt ./scripts/scrape-tweets/requirements.txt
	docker build -t moritzwilksch/dukerepo:datacollector -f ./scripts/scrape-tweets/Dockerfile ./scripts/scrape-tweets/ --no-cache
	rm ./scripts/scrape-tweets/requirements.txt
	docker push moritzwilksch/dukerepo:datacollector

docker-run:
	docker run -d --name datacollector --env-file scripts/scrape-tweets/env.list datacollector

docker-run-debug:
	docker run -it --name datacollector --env-file scripts/scrape-tweets/env.list datacollector
	
docker-clean:
	docker rm -f datacollector

# Frontend
docker-build-frontend: docker-clean-frontend
	docker build -t frontend -f ./scripts/application/Dockerfile ./scripts/


docker-run-frontend:
	docker run -it --name frontend --env-file ./scripts/scrape-tweets/env.list -p 8080:8080 frontend

docker-clean-frontend:
	docker stop frontend
	docker rm -f frontend