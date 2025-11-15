# Database Configuration
import os

# MySQL Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'songs_data'),
    'password': os.getenv('DB_PASSWORD', 'Nick4033!'),
    'database': os.getenv('DB_NAME', 'songs_list_db'),
    'charset': 'utf8mb4',
    'port': int(os.getenv('DB_PORT', 3306))
}
