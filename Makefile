help:
	@echo "Available targets:"
	@echo "  help    - Show this help message."
	@echo "  build   - Build the docker image."
	@echo "  run     - Run the docker container."
	@echo "  admin   - Create an admin user."
	@echo "  migrate   - Migrate Database"
	@echo "  stop    - Stop the docker container."


build:
	docker compose build

migrate:
	docker exec -it pos-backend alembic upgrade head

run:
ifeq ($(DETACHED),true)
	docker compose up -d
else
	docker compose up
endif

deploy:
	docker compose -f docker-compose.yml up -d

admin:
	docker exec -it pos-backend python src/create_admin.py

stop:
	docker compose down
