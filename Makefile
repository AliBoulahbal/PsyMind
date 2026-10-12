up:
	cp -n .env.example .env || true
	docker compose up --build
down:
	docker compose down
reset:
	docker compose down -v
	docker compose up --build
test:
	docker compose exec api pytest -q
logs:
	docker compose logs -f api web
