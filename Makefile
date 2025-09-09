up:
	docker-compose up -d

down:
	docker-compose down

install:
	pip install -r requirements.txt

update:
	python etl/extract_socrata.py && python etl/transform_clean.py && python etl/load_postgres.py

test:
	pytest

lint:
	ruff .

api:
	uvicorn api.main:app --reload
