DEV_COMPOSE = docker compose -f docker/development/docker-compose.yml
PROD_COMPOSE = docker compose -f docker/production/docker-compose.yml

# Development Commands
dev-build:
	@echo "🔨 Building development..."
	$(DEV_COMPOSE) up -d db redis || true
	$(DEV_COMPOSE) build

dev-up:
	@echo "🚀 Starting development..."
	$(DEV_COMPOSE) up -d db redis || true
	@sleep 3
	@echo "⏳ Running database migrations..."
	$(DEV_COMPOSE) run --rm web python manage.py migrate
	@echo "⏳ Running django-celery-beat migrations..."
	$(DEV_COMPOSE) run --rm web python manage.py migrate django_celery_beat
	@echo "🚀 Starting all services..."
	$(DEV_COMPOSE) up -d web bot celery_worker celery_beat
	@echo "✅ All services started!"
	@echo "📋 Check status: make dev-status"

dev-down:
	@echo "🛑 Stopping all services..."
	$(DEV_COMPOSE) down

dev-restart:
	@echo "🔄 Restarting services..."
	$(DEV_COMPOSE) restart web bot celery_worker celery_beat

dev-makemigrations:
	$(DEV_COMPOSE) exec web python manage.py makemigrations

dev-migrate:
	$(DEV_COMPOSE) exec web python manage.py migrate

dev-superuser:
	$(DEV_COMPOSE) exec web python manage.py createsuperuser

dev-logs:
	@echo "📋 Showing logs (press Ctrl+C to exit)..."
	$(DEV_COMPOSE) logs -f web bot celery_worker celery_beat

dev-logs-celery:
	@echo "📋 Showing Celery logs only..."
	$(DEV_COMPOSE) logs -f celery_worker celery_beat

dev-status:
	@echo "📊 Service status:"
	$(DEV_COMPOSE) ps

dev-shell:
	$(DEV_COMPOSE) exec web bash

dev-celery-inspect:
	@echo "🔍 Checking registered Celery tasks..."
	$(DEV_COMPOSE) exec celery_worker celery -A src.settings.config.celery inspect registered

dev-celery-purge:
	@echo "🗑️  Purging all Celery tasks..."
	$(DEV_COMPOSE) exec celery_worker celery -A src.settings.config.celery purge -f

dev-redis-cli:
	$(DEV_COMPOSE) exec redis redis-cli

dev-db-shell:
	$(DEV_COMPOSE) exec db psql -U djangogram_user -d djangogram_db

dev-clean:
	@echo "🧹 Cleaning up..."
	$(DEV_COMPOSE) down -v
	@echo "✅ Cleaned!"


# Production Commands
prod-build:
	@echo "🏗️  Building production images with cache..."
	$(PROD_COMPOSE) build

prod-up:
	@echo "🚀 Starting development..."
	$(PROD_COMPOSE) up -d db redis || true
	@sleep 3
	@echo "⏳ Running database migrations..."
	$(PROD_COMPOSE) run --rm web python manage.py migrate
	@echo "⏳ Running django-celery-beat migrations..."
	$(PROD_COMPOSE) run --rm web python manage.py migrate django_celery_beat
	@echo "🚀 Starting all services..."
	$(PROD_COMPOSE) up -d web bot celery_worker celery_beat
	@echo "✅ All services started!"
	@echo "📋 Check status: make dev-status"

prod-down:
	@echo "🛑 Stopping production..."
	$(PROD_COMPOSE) down

prod-restart:
	@echo "🔄 Restarting production..."
	$(PROD_COMPOSE) restart

prod-logs:
	@echo "📋 Showing production logs..."
	$(PROD_COMPOSE) logs -f web bot ngrok nginx celery_worker celery_beat

prod-status:
	@echo "📊 Production service status:"
	$(PROD_COMPOSE) ps

prod-shell:
	$(PROD_COMPOSE) exec web bash

prod-update:
	@echo "🚀 Starting zero-downtime update..."
	
	# 1. Build new images (with cache, memory efficient)
	@echo "📦 Building new images..."
	$(PROD_COMPOSE) build
	
	# 2. Update services one by one (rolling update)
	@echo "🔄 Updating web service..."
	$(PROD_COMPOSE) up -d --no-deps --force-recreate web
	@sleep 3
	
	@echo "🔄 Running migrations..."
	$(PROD_COMPOSE) exec web python manage.py migrate
	
	@echo "🔄 Updating bot..."
	$(PROD_COMPOSE) up -d --no-deps --force-recreate bot
	@sleep 2
	
	@echo "🔄 Updating celery workers..."
	$(PROD_COMPOSE) up -d --no-deps --force-recreate celery_worker celery_beat
	@sleep 2
	
	@echo "🔄 Updating nginx..."
	$(PROD_COMPOSE) up -d --no-deps --force-recreate nginx
	
	# 3. Clean old images (optional, only if space needed)
	@echo "🧹 Cleaning old images..."
	docker image prune -f --filter "dangling=true"
	
	@echo "✅ Production updated successfully (zero-downtime)!"
	@echo "📊 Status:"
	$(PROD_COMPOSE) ps

prod-force-rebuild:
	@echo "⚠️  FORCE REBUILD - This will cause downtime!"
	@read -p "Are you sure? (yes/no): " confirm && [ "$$confirm" = "yes" ] || exit 1
	$(PROD_COMPOSE) down
	docker image prune -af
	$(PROD_COMPOSE) build --no-cache
	$(PROD_COMPOSE) up -d
	@sleep 5
	$(PROD_COMPOSE) exec web python manage.py migrate
	@echo "✅ Force rebuild completed!"

prod-clean-images:
	@echo "🧹 Cleaning unused Docker images..."
	docker image prune -f
	@echo "✅ Done!"

prod-clean-all:
	@echo "⚠️  WARNING: This will delete all data (DB, Redis, etc.)"
	@read -p "Are you sure? Type 'DELETE' to confirm: " confirm && [ "$$confirm" = "DELETE" ] || exit 1
	$(PROD_COMPOSE) down -v
	docker image prune -af
	@echo "✅ Everything cleaned!"

prod-memory:
	@echo "💾 Docker memory usage:"
	docker stats --no-stream
	@echo "\n📦 Image sizes:"
	docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

.PHONY: \
	dev-build dev-up dev-down dev-restart dev-makemigrations dev-migrate \
	dev-superuser dev-logs dev-logs-celery dev-status dev-shell dev-celery-inspect \
	dev-celery-purge dev-redis-cli dev-db-shell dev-clean \
	prod-build prod-up prod-down prod-restart prod-logs prod-status prod-shell \
	prod-update prod-force-rebuild prod-clean-images prod-clean-all prod-memory
