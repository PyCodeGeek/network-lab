# scripts/entrypoint.sh - Container entrypoint script
# ===================================================

#!/bin/bash
set -e

# Wait for database to be ready
wait_for_db() {
    echo "Waiting for database to be ready..."
    while ! nc -z db 5432; do
        echo "Database not ready, waiting..."
        sleep 2
    done
    echo "Database is ready!"
}

# Wait for Redis to be ready
wait_for_redis() {
    echo "Waiting for Redis to be ready..."
    while ! nc -z redis 6379; do
        echo "Redis not ready, waiting..."
        sleep 2
    done
    echo "Redis is ready!"
}

# Initialize database
init_db() {
    echo "Initializing database..."
    flask db upgrade
    
    # Create default admin user if it doesn't exist
    python -c "
from app import create_app, db
from app.auth.models import User
import os

app = create_app()
with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@example.com',
            role='admin'
        )
        admin.set_password('admin')
        db.session.add(admin)
        db.session.commit()
        print('Default admin user created')
    else:
        print('Admin user already exists')
"
}

# Main execution
case "$1" in
    "backend")
        wait_for_db
        wait_for_redis
        init_db
        exec python run.py
        ;;
    "celery_worker")
        wait_for_db
        wait_for_redis
        exec celery -A app.celery worker --loglevel=info
        ;;
    "celery_beat")
        wait_for_db
        wait_for_redis
        exec celery -A app.celery beat --loglevel=info
        ;;
    *)
        exec "$@"
        ;;
esac