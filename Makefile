IMAGE_NAME = modular-scraper
CONTAINER_NAME = scraper-runner

# Docker commands
up:
	docker-compose up --build

down:
	docker-compose down

logs:
	docker-compose logs -f

restart:
	docker-compose down && docker-compose up --build


clean:
	docker image rm -f $(IMAGE_NAME) || true

init:
	python3 -m venv .venv && \
	. .venv/bin/activate && \
	pip install -r requirements.txt

install:
	python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

listen:
	. .venv/bin/activate && python3 -m app.main -l

run:
	. .venv/bin/activate && python3 -m app.main


dev-listen:
	. .venv/bin/activate && watchfiles 'python3 -m app.main -l'

dev:
	. .venv/bin/activate && watchfiles 'python3 -m app.main'
	

# Run all tests using the virtual environment
test:
	. .venv/bin/activate && python3 -m pytest

# Run tests in a specific directory
test-dir:
	. .venv/bin/activate && python3 -m pytest $(d)

# Run a specific test file
test-file:
	. .venv/bin/activate && python3 -m pytest $(f)

# Docker Compose commands for the bot system
bot-up:
	docker-compose up -d

bot-down:
	docker-compose down

bot-logs:
	docker-compose logs -f

bot-restart:
	docker-compose restart

bot-build:
	docker-compose build

bot-clean:
	docker-compose down -v
	docker image rm -f $(IMAGE_NAME) || true

# Development commands
dev-run:
	python app/main.py

dev-install:
	pip install -r requirements.txt