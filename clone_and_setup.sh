#!/bin/bash
set -e

echo "=== Cloning ATO Repository ==="
# Xóa thư mục cũ nếu tồn tại
if [ -d "ato" ]; then
  echo "Removing existing ato directory..."
  rm -rf ato
fi

# Clone repository
echo "Cloning from GitHub..."
git clone https://github.com/huannv-sys/ato.git
cd ato

# Backup and fix .env file
echo "Setting up environment variables..."
echo "DATABASE_URL=${DATABASE_URL}" > .env
cat .env

echo "=== Setup Completed Successfully ==="
echo "You can now start the simplified server with 'Simple ATO Server' workflow."
