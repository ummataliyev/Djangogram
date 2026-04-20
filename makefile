DEV_COMPOSE = docker compose -f infra/development/docker-compose.yml
PROD_COMPOSE = docker compose -f infra/production/docker-compose.yml
SELF_MAKEFILE = $(firstword $(MAKEFILE_LIST))

define run_compose
$(1) $(2)
endef

# Development Commands
dev-build:
	@echo "🏗️ Building development..."
	$(call run_compose,$(DEV_COMPOSE),up -d db redis || true)
	$(call run_compose,$(DEV_COMPOSE),build)

dev-up:
	@echo "🚀 Starting development..."
	$(call run_compose,$(DEV_COMPOSE),up -d db redis || true)
	@sleep 3
	@echo "⏳ Running migrations..."
	$(call run_compose,$(DEV_COMPOSE),run --rm web python manage.py migrate)
	$(call run_compose,$(DEV_COMPOSE),run --rm web python manage.py migrate django_celery_beat)
	@echo "🚀 Starting all services..."
	$(call run_compose,$(DEV_COMPOSE),up -d web bot celery_worker celery_beat)
	@echo "✅ All services started!"

dev-down:
	@echo "🛑 Stopping all services..."
	$(call run_compose,$(DEV_COMPOSE),down)

dev-restart:
	@echo "🔄 Restarting services..."
	$(call run_compose,$(DEV_COMPOSE),restart web bot celery_worker celery_beat)

dev-makemigrations:
	@echo "⚙️ Make migrations"
	$(call run_compose,$(DEV_COMPOSE),exec web python manage.py makemigrations)

dev-migrate:
	@echo "⚙️ Migrate"
	$(call run_compose,$(DEV_COMPOSE),exec web python manage.py migrate)

dev-superuser:
	@echo "👨‍💻 Create superuser"
	$(call run_compose,$(DEV_COMPOSE),exec web python manage.py createsuperuser)

dev-logs:
	@echo "📋 Showing logs..."
	$(call run_compose,$(DEV_COMPOSE),logs -f web bot celery_worker celery_beat)

dev-logs-celery:
	@echo "📋 Showing Celery logs only..."
	$(call run_compose,$(DEV_COMPOSE),logs -f celery_worker celery_beat)

dev-status:
	@echo "📊 Service status:"
	$(call run_compose,$(DEV_COMPOSE),ps)

dev-shell:
	@echo "🪄 Shell app:"
	$(call run_compose,$(DEV_COMPOSE),exec web bash)

dev-celery-inspect:
	@echo "🔍 Checking registered Celery tasks..."
	$(call run_compose,$(DEV_COMPOSE),exec celery_worker celery -A src.settings.config.celery inspect registered)

dev-celery-purge:
	@echo "🗑️  Purging all Celery tasks..."
	$(call run_compose,$(DEV_COMPOSE),exec celery_worker celery -A src.settings.config.celery purge -f)

dev-redis-cli:
	@echo "🪄 Shell redis:"
	$(call run_compose,$(DEV_COMPOSE),exec redis redis-cli)

dev-db-shell:
	@echo "🪄 Shell database:"
	$(call run_compose,$(DEV_COMPOSE),exec db psql -U djangogram_user -d djangogram_db)

dev-clean:
	@echo "🧹 Cleaning up..."
	$(call run_compose,$(DEV_COMPOSE),down -v)
	@echo "✅ Cleaned!"

# Production Commands
prod-build:
	@echo "🏗️ Building production images..."
	$(call run_compose,$(PROD_COMPOSE),build)

prod-up:
	@echo "🚀 Starting production..."
	$(call run_compose,$(PROD_COMPOSE),up -d db redis || true)
	@sleep 3
	@echo "⏳ Running migrations..."
	$(call run_compose,$(PROD_COMPOSE),run --rm web python manage.py migrate)
	$(call run_compose,$(PROD_COMPOSE),run --rm web python manage.py migrate django_celery_beat)
	@echo "🚀 Starting all services..."
	$(call run_compose,$(PROD_COMPOSE),up -d web bot celery_worker celery_beat)
	@echo "✅ All services started!"

prod-down:
	@echo "🛑 Stopping production..."
	$(call run_compose,$(PROD_COMPOSE),down)

prod-restart:
	@echo "🔄 Restarting production..."
	$(call run_compose,$(PROD_COMPOSE),restart)

prod-logs:
	@echo "📋 Showing production logs..."
	$(call run_compose,$(PROD_COMPOSE),logs -f web bot celery_worker celery_beat)

prod-status:
	@echo "📊 Production service status:"
	$(call run_compose,$(PROD_COMPOSE),ps)

prod-shell:
	@echo "🪄 Shell app:"
	$(call run_compose,$(PROD_COMPOSE),exec web bash)

prod-update:
	@echo "🔄 Zero-downtime update..."
	$(call run_compose,$(PROD_COMPOSE),build)
	$(call run_compose,$(PROD_COMPOSE),up -d --no-deps --force-recreate web)
	@sleep 3
	$(call run_compose,$(PROD_COMPOSE),exec web python manage.py migrate)
	$(call run_compose,$(PROD_COMPOSE),up -d --no-deps --force-recreate bot celery_worker celery_beat)
	$(call run_compose,$(PROD_COMPOSE),up -d --no-deps --force-recreate nginx)
	docker image prune -f --filter "dangling=true"
	@echo "✅ Production updated!"

prod-force-rebuild:
	@echo "⚠️  FORCE REBUILD - This will cause downtime!"
	@read -p "Are you sure? (yes/no): " confirm && [ "$$confirm" = "yes" ] || exit 1
	$(call run_compose,$(PROD_COMPOSE),down)
	docker image prune -af
	$(call run_compose,$(PROD_COMPOSE),build --no-cache)
	$(call run_compose,$(PROD_COMPOSE),up -d)
	@sleep 5
	$(call run_compose,$(PROD_COMPOSE),exec web python manage.py migrate)
	@echo "✅ Force rebuild completed!"

prod-clean-images:
	@echo "🧹 Cleaning unused Docker images..."
	docker image prune -f
	@echo "✅ Done!"

prod-clean-all:
	@echo "⚠️  WARNING: This will delete all data (DB, Redis, etc.)"
	@read -p "Are you sure? Type 'DELETE' to confirm: " confirm && [ "$$confirm" = "DELETE" ] || exit 1
	$(call run_compose,$(PROD_COMPOSE),down -v)
	docker image prune -af
	@echo "✅ Everything cleaned!"

prod-memory:
	@echo "💾 Docker memory usage:"
	docker stats --no-stream
	@echo "\n📦 Image sizes:"
	docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"


.PHONY: help
help:
	@echo "Available commands:"
	@echo ""
	@echo "Development commands:"
	@grep -E '^[a-zA-Z0-9_-]+:' $(SELF_MAKEFILE) | grep '^dev-' | while read cmd _; do \
		desc=$$(grep -A1 "$$cmd" $(SELF_MAKEFILE) | tail -n1 | sed 's/^[ \t]*# //'); \
		printf "  %-25s %s\n" "$$cmd" "$$desc"; \
	done
	@echo ""
	@echo "Production commands:"
	@grep -E '^[a-zA-Z0-9_-]+:' $(SELF_MAKEFILE) | grep '^prod-' | while read cmd _; do \
		desc=$$(grep -A1 "$$cmd" $(SELF_MAKEFILE) | tail -n1 | sed 's/^[ \t]*# //'); \
		printf "  %-25s %s\n" "$$cmd" "$$desc"; \
	done

.PHONY: \
	dev-build dev-up dev-down dev-restart dev-makemigrations dev-migrate \
	dev-superuser dev-logs dev-logs-celery dev-status dev-shell dev-celery-inspect \
	dev-celery-purge dev-redis-cli dev-db-shell dev-clean \
	prod-build prod-up prod-down prod-restart prod-logs prod-status prod-shell \
	prod-update prod-force-rebuild prod-clean-images prod-clean-all prod-memory
