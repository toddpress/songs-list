# Database Configuration
# Update these values with your actual database credentials

import os

# MySQL Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'songs_list_db'),
    'charset': 'utf8mb4',
    'port': int(os.getenv('DB_PORT', 3306))
}