cd /home/ubuntu/project/elcarobybitbotv2

# SECURITY: JWT_SECRET must be set in environment or .env file
# Generate secure secret: openssl rand -hex 32
if [ -z "$JWT_SECRET" ]; then
    if [ -f .env ]; then
        export $(grep -E '^JWT_SECRET=' .env | xargs)
    fi
fi

if [ -z "$JWT_SECRET" ]; then
    echo "ERROR: JWT_SECRET not set. Generate one with: openssl rand -hex 32"
    exit 1
fi

exec ./venv/bin/python -m uvicorn webapp.app:app --host 0.0.0.0 --port 8765
