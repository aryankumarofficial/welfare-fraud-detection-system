# ==============================
# Welfare Fraud Detection System
# Makefile
# ==============================

.PHONY: setup dev api admin ml docker-up docker-down install train db-generate db-migrate db-studio

# Install all dependencies
setup:
	bun install
	cd services/ml && python -m venv venv
	cd services/ml && venv/Scripts/pip install -r requirements.txt

# Start frontend
admin:
	bun --filter admin dev

# Start API
api:
	bun --filter api dev

# Start ML service
ml:
	cd services/ml && venv/Scripts/uvicorn app.main:app --reload

# Run everything locally
dev:
	bun run dev & bun run api & bun run ml

# Docker start (postgres -> migrate -> apps; no manual migrate step required)
docker-up:
	docker compose up --build

# Docker stop
docker-down:
	docker compose down

# Train ML model
train:
	cd services/ml && venv/Scripts/python training/train_model.py

# Database migrations
db-generate:
	bun run db:generate

db-migrate:
	bun run db:migrate

db-studio:
	bun run db:studio
