#!/bin/bash

# Setup script for Songs List MySQL migration
# This script helps set up the MySQL environment for the Songs List application

echo "Songs List MySQL Setup Script"
echo "============================="

# Check if MySQL is installed
if ! command -v mysql &> /dev/null; then
    echo "MySQL is not installed. Please install MySQL first:"
    echo "  macOS: brew install mysql"
    echo "  Ubuntu: sudo apt install mysql-server"
    echo "  Windows: Download from https://dev.mysql.com/downloads/installer/"
    exit 1
fi

echo "✓ MySQL is installed"

# Check if MySQL is running
if ! pgrep -x "mysqld" > /dev/null; then
    echo "MySQL is not running. Starting MySQL..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew services start mysql
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        sudo systemctl start mysql
    else
        echo "Please start MySQL manually for your operating system"
        exit 1
    fi
fi

echo "✓ MySQL is running"

# Function to create database and user
setup_database() {
    echo ""
    echo "Setting up database..."
    
    read -p "Enter MySQL root password: " -s ROOT_PASSWORD
    echo ""
    
    read -p "Enter new database user name (default: songs_user): " DB_USER
    DB_USER=${DB_USER:-songs_user}
    
    read -p "Enter password for $DB_USER: " -s DB_PASSWORD
    echo ""
    
    # Create database and user
    mysql -u root -p$ROOT_PASSWORD << EOF
CREATE DATABASE IF NOT EXISTS songs_list_db;
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON songs_list_db.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
EOF

    if [ $? -eq 0 ]; then
        echo "✓ Database and user created successfully"
        
        # Update config.py
        cat > config.py << EOL
# Database Configuration
import os

# MySQL Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', '$DB_USER'),
    'password': os.getenv('DB_PASSWORD', '$DB_PASSWORD'),
    'database': os.getenv('DB_NAME', 'songs_list_db'),
    'charset': 'utf8mb4',
    'port': int(os.getenv('DB_PORT', 3306))
}
EOL
        echo "✓ Updated config.py with database credentials"
        
        # Create database schema
        echo "Creating database schema..."
        mysql -u $DB_USER -p$DB_PASSWORD songs_list_db < setup_database.sql
        
        if [ $? -eq 0 ]; then
            echo "✓ Database schema created successfully"
        else
            echo "✗ Failed to create database schema"
            return 1
        fi
        
    else
        echo "✗ Failed to create database and user"
        return 1
    fi
}

# Install Python dependencies
install_dependencies() {
    echo ""
    echo "Installing Python dependencies..."
    
    # Check if virtual environment exists, create if not
    if [ ! -d "song_list_env" ]; then
        echo "Creating virtual environment..."
        python3 -m venv song_list_env
        if [ $? -ne 0 ]; then
            echo "✗ Failed to create virtual environment"
            return 1
        fi
        echo "✓ Virtual environment created"
    else
        echo "✓ Virtual environment found"
    fi
    
    # Activate virtual environment and install dependencies
    source song_list_env/bin/activate
    
    if command -v pip &> /dev/null; then
        pip install -r requirements.txt
    else
        echo "✗ pip is not available in virtual environment"
        deactivate
        return 1
    fi
    
    if [ $? -eq 0 ]; then
        echo "✓ Python dependencies installed successfully"
        echo ""
        echo "Note: To run the application, first activate the virtual environment:"
        echo "  source song_list_env/bin/activate"
        deactivate
    else
        echo "✗ Failed to install Python dependencies"
        deactivate
        return 1
    fi
}

# Main menu
echo ""
echo "What would you like to do?"
echo "1. Set up database and user"
echo "2. Install Python dependencies"
echo "3. Both (recommended)"
echo "4. Exit"

read -p "Choose an option (1-4): " choice

case $choice in
    1)
        setup_database
        ;;
    2)
        install_dependencies
        ;;
    3)
        setup_database && install_dependencies
        ;;
    4)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac

if [ $? -eq 0 ]; then
    echo ""
    echo "Setup completed successfully! 🎉"
    echo ""
    echo "Next steps:"
    echo "1. Activate the virtual environment: source song_list_env/bin/activate"
    echo "2. Start the application with: streamlit run app.py"
    echo ""
else
    echo ""
    echo "Setup failed. Please check the errors above and try again."
fi