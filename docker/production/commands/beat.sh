#!/bin/bash

celery -A src.settings.config.celery beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
