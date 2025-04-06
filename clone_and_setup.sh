#!/bin/bash

# Set error handling
set -e

echo "Cloning ATO repository from GitHub..."
if [ ! -d "ato" ]; then
  git clone https://github.com/huannv-sys/ato.git
  echo "Repository cloned successfully."
else
  echo "Repository already exists."
fi

echo "Changing to repository directory..."
cd ato

echo "Creating .env file with database connection..."
cat > .env << EOF
VOVI_API_URL=http://api.vovi.example.com/api
VOVI_API_KEY=your_api_key_here
DATABASE_URL=${DATABASE_URL}
PORT=5000
EOF

echo "Creating migrations directory..."
mkdir -p migrations

echo "Setup complete. Dependencies will be installed by the main workflow."

