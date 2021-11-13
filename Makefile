install:
	pip install --upgrade pip
	pip install -r requirements.txt

run-frontend:
	uvicorn --app-dir application/ app:app --reload --host 0.0.0.0 --port 8080

docker-build:
	cp requirements.txt ./scripts/scrape-tweets/requirements.txt
	docker build -t datacollector -f ./scripts/scrape-tweets/Dockerfile ./scripts/scrape-tweets/
	rm ./scripts/scrape-tweets/requirements.txt

docker-run:
	docker run -d --name datacollector -e API_TOKEN=${API_TOKEN} datacollector

docker-run-debug:
	docker run -it --name datacollector -e API_TOKEN=${API_TOKEN} datacollector
	docker cp datacollector:/app/twint_out.csv ~/AWSCloud-TweetGenerator/twint_out.csv
	
docker-clean:
	docker rm -f datacollector
	