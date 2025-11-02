#!/bin/bash

celery -A src.settings.config.celery worker -l info --pool=solo
