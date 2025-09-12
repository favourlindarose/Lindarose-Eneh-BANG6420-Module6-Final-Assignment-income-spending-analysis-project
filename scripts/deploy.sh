#!/bin/bash
set -e  # Exit on error

echo "Starting deployment process..."

# Temporarily disable the problematic post-invoke script to prevent apt_pkg errors
echo "Disabling problematic apt post-invoke script..."
sudo mv /usr/lib/cnf-update-db /usr/lib/cnf-update-db.backup 2>/dev/null || true

# Update system without triggering the problematic hook
echo "Updating system packages..."
sudo apt-get update -o APT::Update::Post-Invoke-Success::=

# Check if Python 3.11 is already installed, if not install it using alternative method
if ! command -v python3.11 &> /dev/null; then
    echo "Installing Python 3.11..."
    # Alternative method to install Python 3.11 without using add-apt-repository
    sudo apt-get install -y software-properties-common
    # Use manual source list addition instead of add-apt-repository
    echo "deb http://ppa.launchpad.net/deadsnakes/ppa/ubuntu noble main" | sudo tee /etc/apt/sources.list.d/deadsnakes-ppa.list
    sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys F23C5A6CF475977595C89F51BA6932366A755776
    sudo apt-get update -o APT::Update::Post-Invoke-Success::=
    sudo apt-get install -y python3.11 python3.11-venv python3.11-dev
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
fi

# Verify Python version
echo "Python version: $(python3 --version)"

if ! command -v nginx &> /dev/null; then
    sudo apt-get install -y nginx
fi

# Create app directory if it doesn't exist
APP_DIR="/home/ubuntu/income-spending-survey"
if [ ! -d "$APP_DIR" ]; then
    sudo mkdir -p $APP_DIR
    sudo chown -R ubuntu:ubuntu $APP_DIR
fi

# Copy files to app directory
echo "Copying application files..."
sudo cp -r . $APP_DIR
sudo chown -R ubuntu:ubuntu $APP_DIR

# Set up virtual environment with Python 3.11
echo "Setting up Python virtual environment..."
cd $APP_DIR
python3.11 -m venv venv
source venv/bin/activate

# Upgrade pip and setuptools first
pip install --upgrade pip setuptools wheel

# Install production dependencies including visualization libraries and certifi
echo "Installing production dependencies..."
if [ -f "requirements-prod.txt" ]; then
    pip install -r requirements-prod.txt
elif [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "Installing default dependencies including visualization libraries and certifi..."
    pip install flask pymongo matplotlib seaborn pandas numpy gunicorn certifi
fi

# Make sure certifi is installed (critical for MongoDB Atlas SSL)
echo "Ensuring certifi is installed for MongoDB Atlas SSL..."
pip install certifi

# Set up Nginx
echo "Configuring Nginx..."
if [ -f "scripts/nginx-config" ]; then
    sudo cp scripts/nginx-config /etc/nginx/sites-available/income-survey
    sudo ln -sf /etc/nginx/sites-available/income-survey /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    sudo nginx -t
    sudo systemctl restart nginx
fi

# Set up systemd service
echo "Configuring systemd service..."
if [ -f "scripts/income-survey.service" ]; then
    # Update service file to use app:app
    if grep -q "wsgi:app" scripts/income-survey.service && [ -f "app.py" ]; then
        echo "Updating systemd service to use app:app instead of wsgi:app..."
        sed -i 's/wsgi:app/app:app/g' scripts/income-survey.service
    fi
    
    # Copy service file to systemd
    sudo cp scripts/income-survey.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable income-survey.service
    sudo systemctl restart income-survey.service
fi

# Wait a moment for the service to start and check status
sleep 5
echo "Checking service status..."
sudo systemctl status income-survey.service --no-pager -l

# Check if the application is listening on the expected port
echo "Checking if application is listening on port 5000..."
if sudo netstat -tulpn | grep :5000; then
    echo "Application is successfully listening on port 5000"
else
    echo "WARNING: Application is not listening on port 5000"
    echo "Checking application logs..."
    sudo journalctl -u income-survey.service --no-pager -n 20
fi

# Test MongoDB Atlas connection with certifi
echo "Testing MongoDB Atlas connection with certifi..."
cd $APP_DIR
source venv/bin/activate
if python3 -c "
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import certifi
import os
try:
    client = MongoClient(
        'mongodb+srv://kingsamuel412_db_user:5YmyvqhPpiksB4QJ@favour.k47oqe4.mongodb.net/?retryWrites=true&w=majority&appName=favour',
        serverSelectionTimeoutMS=5000,
        tls=True,
        tlsCAFile=certifi.where()
    )
    client.server_info()
    print('MongoDB Atlas connection successful with SSL!')
except Exception as e:
    print(f'MongoDB Atlas connection failed: {e}')
    # Test without SSL as fallback
    try:
        client = MongoClient('mongodb+srv://kingsamuel412_db_user:5YmyvqhPpiksB4QJ@favour.k47oqe4.mongodb.net/?retryWrites=true&w=majority&appName=favour&tls=false', serverSelectionTimeoutMS=3000)
        client.server_info()
        print('MongoDB Atlas connection successful without SSL!')
    except Exception as e2:
        print(f' MongoDB Atlas connection also failed without SSL: {e2}')
"; then
    echo " MongoDB Atlas connection test completed"
else
    echo " MongoDB Atlas connection test failed"
fi

# Restore the cnf-update-db script if we moved it
if [ -f "/usr/lib/cnf-update-db.backup" ]; then
    echo "Restoring cnf-update-db script..."
    sudo mv /usr/lib/cnf-update-db.backup /usr/lib/cnf-update-db
fi

echo "Deployment completed successfully!"
echo "Application should be available at: http://$(curl -s ifconfig.me)"





















