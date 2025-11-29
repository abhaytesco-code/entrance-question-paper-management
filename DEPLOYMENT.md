# LearnMatrix Deployment Guide

## 🚀 Production Deployment

### Prerequisites
- Python 3.8+ on target server
- MySQL 5.7+ or MariaDB 10.3+
- Linux server (Ubuntu 20.04+ recommended) or Windows Server
- Domain name (recommended)
- SSL certificate (Let's Encrypt for free)

---

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] All dependencies in `requirements.txt`
- [ ] Database schema tested locally
- [ ] Environment variables configured
- [ ] SECRET_KEY set to random string
- [ ] DEBUG set to False
- [ ] HTTPS/SSL configured
- [ ] Database backups configured
- [ ] Error logging setup

### Post-Deployment
- [ ] Run smoke tests
- [ ] Verify SSL certificate
- [ ] Monitor application logs
- [ ] Setup automated backups
- [ ] Configure firewall rules
- [ ] Enable monitoring/alerting

---

## 🐧 Linux/Ubuntu Deployment (Recommended)

### Step 1: Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3 python3-pip python3-venv
sudo apt install -y mysql-server mysql-client

# Install Gunicorn (production WSGI server)
sudo apt install -y gunicorn

# Install Nginx (reverse proxy)
sudo apt install -y nginx

# Install SSL (Let's Encrypt)
sudo apt install -y certbot python3-certbot-nginx
```

### Step 2: Clone Application
```bash
# Create application directory
sudo mkdir -p /var/www/learnmatrix
cd /var/www/learnmatrix

# Clone repository (or copy files)
# git clone <repo-url> .

# Set permissions
sudo chown -R $(whoami):$(whoami) /var/www/learnmatrix
```

### Step 3: Setup Python Environment
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
pip install gunicorn
```

### Step 4: Configure Database
```bash
# Start MySQL
sudo systemctl start mysql
sudo systemctl enable mysql

# Create database
mysql -u root -p < learnmatrix_schema.sql
```

### Step 5: Create .env File
```bash
cat > .env << 'EOF'
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
FLASK_ENV=production
DEBUG=False

DB_HOST=localhost
DB_USER=learnmatrix_user
DB_PASSWORD=secure_password_here
DB_NAME=learnmatrix

SESSION_PERMANENT=True
PERMANENT_SESSION_LIFETIME=604800
EOF

# Secure the file
chmod 600 .env
```

### Step 6: Configure Gunicorn
Create `/var/www/learnmatrix/gunicorn_config.py`:
```python
import multiprocessing
import os

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 60
keepalive = 5
preload_app = True
daemon = False
pidfile = "/var/www/learnmatrix/gunicorn.pid"
logfile = "/var/www/learnmatrix/logs/gunicorn.log"
loglevel = "info"
```

### Step 7: Create Systemd Service
Create `/etc/systemd/system/learnmatrix.service`:
```ini
[Unit]
Description=LearnMatrix Flask Application
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/learnmatrix
Environment="PATH=/var/www/learnmatrix/venv/bin"
ExecStart=/var/www/learnmatrix/venv/bin/gunicorn --config gunicorn_config.py app:app
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

### Step 8: Configure Nginx
Create `/etc/nginx/sites-available/learnmatrix`:
```nginx
server {
    listen 80;
    server_name learnmatrix.yourdomain.com;
    client_max_body_size 16M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_request_buffering off;
    }

    location /static {
        alias /var/www/learnmatrix/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/learnmatrix /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 9: Setup SSL with Let's Encrypt
```bash
sudo certbot --nginx -d learnmatrix.yourdomain.com

# Auto-renewal (runs daily)
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### Step 10: Start Services
```bash
# Create logs directory
sudo mkdir -p /var/www/learnmatrix/logs
sudo chown www-data:www-data /var/www/learnmatrix/logs

# Enable and start application service
sudo systemctl enable learnmatrix
sudo systemctl start learnmatrix

# Verify service
sudo systemctl status learnmatrix
```

### Step 11: Setup Monitoring & Backups
```bash
# Create backup script
cat > /var/www/learnmatrix/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/learnmatrix"
DATE=$(date +"%Y%m%d_%H%M%S")
mkdir -p $BACKUP_DIR

# Backup database
mysqldump -u learnmatrix_user -p$DB_PASSWORD learnmatrix > $BACKUP_DIR/db_$DATE.sql

# Compress
gzip $BACKUP_DIR/db_$DATE.sql

# Keep last 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
EOF

chmod +x /var/www/learnmatrix/backup.sh

# Schedule daily backups (cron)
(crontab -l 2>/dev/null; echo "0 2 * * * /var/www/learnmatrix/backup.sh") | crontab -
```

---

## 🪟 Windows Server Deployment

### Option 1: Using IIS
```powershell
# Install Python and dependencies
choco install python -y
choco install mysql -y

# Install IIS and ASGI components
Enable-WindowsOptionalFeature -Online -FeatureName IIS-WebServerRole
Enable-WindowsOptionalFeature -Online -FeatureName IIS-ApplicationDevelopment

# Install httpplatformhandler
# Download from: https://www.iis.net/downloads/community/2015/02/httpplatformhandler

# Create virtual environment
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install httpplatformhandler
```

### Option 2: Using Docker
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run:
```bash
docker build -t learnmatrix .
docker run -p 5000:5000 -e DB_HOST=host.docker.internal learnmatrix
```

---

## 🔒 Security Hardening

### 1. Firewall Rules
```bash
# UFW (Ubuntu Firewall)
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 3306/tcp from 127.0.0.1  # MySQL local only
```

### 2. Database Security
```sql
-- Create restricted user
CREATE USER 'learnmatrix_user'@'localhost' IDENTIFIED BY 'strong_password_here';
GRANT ALL PRIVILEGES ON learnmatrix.* TO 'learnmatrix_user'@'localhost';
FLUSH PRIVILEGES;

-- Remove anonymous user
DELETE FROM mysql.user WHERE User='';
FLUSH PRIVILEGES;
```

### 3. Application Configuration
```python
# In config.py for production
class ProductionConfig(Config):
    SESSION_COOKIE_SECURE = True      # HTTPS only
    SESSION_COOKIE_HTTPONLY = True    # No JavaScript access
    SESSION_COOKIE_SAMESITE = 'Strict'
    REMEMBER_COOKIE_SECURE = True
    DEBUG = False
    TESTING = False
```

### 4. Nginx Security Headers
```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self'" always;
```

---

## 📊 Monitoring & Logging

### Application Logging
```python
import logging

logging.basicConfig(
    filename='/var/www/learnmatrix/logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Useful Log Locations
- **Application**: `/var/www/learnmatrix/logs/gunicorn.log`
- **Nginx**: `/var/log/nginx/error.log`
- **MySQL**: `/var/log/mysql/error.log`
- **System**: `/var/log/syslog`

### Monitor with Systemd
```bash
# View logs
sudo journalctl -u learnmatrix -f

# Check service status
sudo systemctl status learnmatrix

# Restart service
sudo systemctl restart learnmatrix
```

---

## 🔄 CI/CD Pipeline (GitHub Actions Example)

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy LearnMatrix

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: SSH to server and deploy
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.SERVER_HOST }}
        username: ${{ secrets.SERVER_USER }}
        key: ${{ secrets.SERVER_SSH_KEY }}
        script: |
          cd /var/www/learnmatrix
          git pull origin main
          source venv/bin/activate
          pip install -r requirements.txt
          systemctl restart learnmatrix
```

---

## 📈 Performance Optimization

### 1. Database Query Caching
```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedDB:
    def __init__(self):
        self.cache = {}
        self.ttl = timedelta(minutes=5)
    
    def get_cached(self, key, query_func):
        if key in self.cache:
            value, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                return value
        
        value = query_func()
        self.cache[key] = (value, datetime.now())
        return value
```

### 2. Static File Compression
```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/css text/javascript application/javascript;
gzip_comp_level 6;
```

### 3. Database Connection Pooling
```python
from DBUtils.PooledDB import PooledDB

db_pool = PooledDB(
    creator=mysql.connector,
    maxconnections=10,
    mincached=2,
    host='localhost',
    user='learnmatrix_user',
    password='password',
    database='learnmatrix'
)
```

---

## 🆘 Troubleshooting

### Application won't start
```bash
# Check logs
sudo journalctl -u learnmatrix -n 50

# Check port
sudo lsof -i :8000

# Test directly
cd /var/www/learnmatrix
source venv/bin/activate
python app.py
```

### Database connection errors
```bash
# Check MySQL running
sudo systemctl status mysql

# Test connection
mysql -u learnmatrix_user -p -h localhost learnmatrix -e "SELECT 1"

# Check permissions
mysql -u root -p -e "SHOW GRANTS FOR 'learnmatrix_user'@'localhost'"
```

### Nginx issues
```bash
# Test configuration
sudo nginx -t

# Check error log
sudo tail -f /var/log/nginx/error.log

# Restart
sudo systemctl restart nginx
```

---

## 📞 Support & Maintenance

- **Update Dependencies**: `pip install --upgrade -r requirements.txt` monthly
- **Database Maintenance**: `OPTIMIZE TABLE` quarterly
- **Certificate Renewal**: Automated with certbot
- **Log Rotation**: Configure with logrotate
- **Monitoring**: Setup with Prometheus + Grafana

---

**Last Updated**: November 18, 2025  
**Version**: 1.0.0
