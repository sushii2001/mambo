# Project commands

# launch
start:
	python3 ./src/main.py

test:
	pytest tests/ -v

# docker commands:
docker_build:
	docker-compose up -d --build

# replace `local` with the tag used in `image: mambo:local` from docker-compose
docker_stop:
	docker-compose down --rmi local --volumes --remove-orphans