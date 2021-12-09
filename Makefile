#-------------------------------------------------------------------------------------------------------------------------------------------------
# Variables
#-------------------------------------------------------------------------------------------------------------------------------------------------
# Define Docker contexts
HASHTAGCOLLECTOR_CONTEXT=./scripts/scrape_hashtags
DATACOLLECTOR_CONTEXT=./scripts/scrape_tweets
FRONTEND_CONTEXT=./scripts/application
TRAIN_CONTEXT=./scripts/text_generator

# Define DockerHub locations
DOCKERHUB_LOCATION_HASHTAGCOLLECTOR=moritzwilksch/dukerepo:hashtagcollector
DOCKERHUB_LOCATION_DATACOLLECTOR=moritzwilksch/dukerepo:datacollector
DOCKERHUB_LOCATION_FRONTEND=moritzwilksch/dukerepo:frontend
DOCKERHUB_LOCATION_MODELTRAIN=moritzwilksch/dukerepo:modeltrain


#-------------------------------------------------------------------------------------------------------------------------------------------------
# Normal Targets
#-------------------------------------------------------------------------------------------------------------------------------------------------
install:
	pip install --upgrade pip
	pip install -r requirements.txt

run-frontend:
	uvicorn --app-dir scripts/application/ app:app --reload --host 0.0.0.0 --port 8080

test:
	pytest tests/


############################################### DOCKER ######################################################
#-------------------------------------------------------------------------------------------------------------------------------------------------
# Hashtag Data Collection
#-------------------------------------------------------------------------------------------------------------------------------------------------
docker/build-hashtags: docker/clean-hashtags
	docker build --rm -t hashtagcollector -f Dockerfiles/Dockerfile.scrapehashtags $(HASHTAGCOLLECTOR_CONTEXT)/ 

docker/build-push-hashtags: docker/clean-hashtags
	docker build --rm -t $(DOCKERHUB_LOCATION_HASHTAGCOLLECTOR) -f Dockerfiles/Dockerfile.scrapehashtags $(HASHTAGCOLLECTOR_CONTEXT)/ 
	docker push $(DOCKERHUB_LOCATION_HASHTAGCOLLECTOR)

docker/run-hashtags: docker/clean-hashtags
	docker run -it --name hashtagcollector --env-file Dockerfiles/env.list hashtagcollector
	
docker/clean-hashtags:
	docker rm -f hashtagcollector


#-------------------------------------------------------------------------------------------------------------------------------------------------
# Tweet Data Collection
#-------------------------------------------------------------------------------------------------------------------------------------------------
docker/build:
	docker build --rm -t datacollector -f Dockerfiles/Dockerfile.scrapetweets $(DATACOLLECTOR_CONTEXT)/ 

docker/build-push:
	docker build --rm -t $(DOCKERHUB_LOCATION_DATACOLLECTOR) -f Dockerfiles/Dockerfile.scrapetweets $(DATACOLLECTOR_CONTEXT)/
	docker push $(DOCKERHUB_LOCATION_DATACOLLECTOR)

docker/run: docker/clean
	docker run -it --name datacollector --env-file Dockerfiles/env.list datacollector

docker/clean:
	docker rm -f datacollector

#-------------------------------------------------------------------------------------------------------------------------------------------------
# Frontend 
#-------------------------------------------------------------------------------------------------------------------------------------------------
docker/build-frontend: docker/clean-frontend
	docker build --rm -t frontend -f Dockerfiles/Dockerfile.frontend ./scripts/

docker/build-push-frontend:
	docker build --rm -t $(DOCKERHUB_LOCATION_FRONTEND) -f Dockerfiles/Dockerfile.frontend ./scripts/
	docker push $(DOCKERHUB_LOCATION_FRONTEND)

docker/run-frontend: docker/clean-frontend
	docker run -it --name frontend --env-file Dockerfiles/env.list -p 8080:8080 frontend

docker/clean-frontend:
	docker rm -f frontend


#-------------------------------------------------------------------------------------------------------------------------------------------------
# Training
#-------------------------------------------------------------------------------------------------------------------------------------------------
docker/build-modeltraining: docker/clean-modeltraining
	docker build --rm -t modeltraining -f Dockerfiles/Dockerfile.training ./scripts/text_generator

docker/run-modeltraining: docker/clean-modeltraining
	docker run -i --name modeltraining --env-file Dockerfiles/env.list modeltraining

docker/clean-modeltraining:
	docker rm -f modeltraining

docker/build-push-modeltrain:
	docker build --rm -t $(DOCKERHUB_LOCATION_MODELTRAIN) -f Dockerfiles/Dockerfile.training ./scripts/text_generator
	docker push $(DOCKERHUB_LOCATION_MODELTRAIN)