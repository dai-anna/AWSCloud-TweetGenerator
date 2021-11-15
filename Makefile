# Define Docker contexts
HASHTAGCOLLECTOR_CONTEXT=./scripts/scrape-hashtags
DATACOLLECTOR_CONTEXT=./scripts/scrape-tweets
FRONTEND_CONTEXT=./scripts/application

# Define DockerHub locations
DOCKERHUB_LOCATION_DATACOLLECTOR=moritzwilksch/dukerepo:datacollector
DOCKERHUB_LOCATION_FRONTEND=moritzwilksch/dukerepo:frontend


install:
	pip install --upgrade pip
	pip install -r requirements.txt

run-frontend:
	uvicorn --app-dir application/ app:app --reload --host 0.0.0.0 --port 8080

test:
	pytest tests/

################################ DOCKER #######################################
# Hashtag Data Collection
docker-build-hashtags: docker-clean-hashtags
	docker build --rm -t hashtagcollector -f $(HASHTAGCOLLECTOR_CONTEXT)/Dockerfile $(HASHTAGCOLLECTOR_CONTEXT)/ 

docker-run-hashtags:
	docker run -it --name hashtagcollector --env-file $(HASHTAGCOLLECTOR_CONTEXT)/env.list hashtagcollector
	
docker-clean-hashtags:
	docker rm -f datacollector


# Tweet Data Collection

docker-build:
	docker build --rm -t datacollector -f $(DATACOLLECTOR_CONTEXT)/Dockerfile $(DATACOLLECTOR_CONTEXT)/ 

docker-build-push:
	docker build --rm -t $(DOCKERHUB_LOCATION_DATACOLLECTOR) -f $(DATACOLLECTOR_CONTEXT)/Dockerfile $(DATACOLLECTOR_CONTEXT)/ --no-cache
	docker push $(DOCKERHUB_LOCATION_DATACOLLECTOR)

docker-run:
	docker run -d --name datacollector --env-file $(DATACOLLECTOR_CONTEXT)/env.list datacollector

docker-run-debug:
	docker run -it --name datacollector --env-file $(DATACOLLECTOR_CONTEXT)/env.list datacollector
	
docker-clean:
	docker rm -f datacollector

# Frontend
docker-build-frontend: docker-clean-frontend
	docker build --rm -t frontend -f $(FRONTEND_CONTEXT)/Dockerfile ./scripts/

docker-run-frontend:
	docker run -d --name frontend --env-file $(DATACOLLECTOR_CONTEXT)/env.list -p 8080:8080 frontend

docker-clean-frontend:
	docker stop frontend
	docker rm -f frontend

docker-build-push-frontend:
	docker build --rm -t $(DOCKERHUB_LOCATION_FRONTEND) -f $(FRONTEND_CONTEXT)/Dockerfile ./scripts/ --no-cache
	docker push $(DOCKERHUB_LOCATION_FRONTEND)