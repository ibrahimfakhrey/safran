#!/bin/bash
# Server Deployment Script for OTP Email Verification
# Run this script on your production server after uploading files

echo "=========================================="
echo "i pillars i - OTP Email Verification Setup"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Install Flask-Mail
echo -e "${YELLOW}Step 1: Installing Flask-Mail...${NC}"
pip3 install Flask-Mail==0.10.0
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Flask-Mail installed successfully${NC}"
else
    echo -e "${RED}✗ Failed to install Flask-Mail${NC}"
    exit 1
fi
echo ""

# Step 2: Backup database
echo -e "${YELLOW}Step 2: Backing up database...${NC}"
if [ -f "instance/app.db" ]; then
    cp instance/app.db instance/app.db.backup_$(date +%Y%m%d_%H%M%S)
    echo -e "${GREEN}✓ Database backed up${NC}"
else
    echo -e "${YELLOW}⚠ No database file found (fresh install)${NC}"
fi
echo ""

# Step 3: Run migration
echo -e "${YELLOW}Step 3: Running database migration...${NC}"
python3 migrate_email_verification.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Migration completed successfully${NC}"
else
    echo -e "${RED}✗ Migration failed${NC}"
    exit 1
fi
echo ""

# Step 4: Test email configuration
echo -e "${YELLOW}Step 4: Testing email configuration...${NC}"
python3 -c "
from app import create_app
app = create_app()
with app.app_context():
    print('✓ App initialized successfully')
    print('Mail Server:', app.config['MAIL_SERVER'])
    print('Mail Username:', app.config['MAIL_USERNAME'])
"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Email configuration loaded${NC}"
else
    echo -e "${RED}✗ Email configuration error${NC}"
    exit 1
fi
echo ""

# Step 5: Test email sending (optional)
echo -e "${YELLOW}Step 5: Test email sending? (y/n)${NC}"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo "Testing email..."
    python3 test_otp_email.py
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Test email sent! Check your inbox.${NC}"
    else
        echo -e "${RED}✗ Failed to send test email${NC}"
    fi
fi
echo ""

# Summary
echo "=========================================="
echo -e "${GREEN}Deployment Complete! ✓${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Restart your Flask application"
echo "2. Test the API endpoints"
echo "3. Check EMAIL_OTP_API_PROMPT.md for Flutter integration"
echo ""
echo "API Endpoints ready:"
echo "  POST /api/v1/auth/send-otp"
echo "  POST /api/v1/auth/verify-otp"
echo "  POST /api/v1/auth/resend-otp"
echo ""
echo "Need help? Check DEPLOYMENT_CHECKLIST.md"
echo ""
