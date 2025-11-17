.PHONY: dev-up dev-down api tui

dev-up:
	docker compose up -d

dev-down:
	docker compose down

api:
	cd backend && uvicorn api.main:app --reload

tui:
	cd tui/cmd/retail-sleuth-tui && go run main.go
