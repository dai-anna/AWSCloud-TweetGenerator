install:
	pip install --upgrade pip
	pip install -r requirements.txt

run-frontend:
	uvicorn --app-dir application/ app:app --reload --host 0.0.0.0 --port 8080