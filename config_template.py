# Database Configuration
# Copy this file to config.py and update with your actual database credentials

# MySQL Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'songs_list_db',
    'charset': 'utf8mb4',
    'port': 3306
}

# Alternative configuration using environment variables (recommended for production)
import os

DB_CONFIG_ENV = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'songs_list_db'),
    'charset': 'utf8mb4',
    'port': int(os.getenv('DB_PORT', 3306))
}