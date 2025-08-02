#!/usr/bin/env python3
"""
Celery Worker Entry Point
This file starts the Celery worker process
"""

from celery_app import celery_app

if __name__ == "__main__":
    celery_app.worker_main(
        argv=[
            "worker",
            "--loglevel=info",
            "--concurrency=2",
            "--pool=prefork"
        ]
    ) 