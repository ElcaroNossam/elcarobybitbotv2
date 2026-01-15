cd /home/ubuntu/project/elcarobybitbotv2
export JWT_SECRET='elcaro_jwt_secret_key_2024_v2_secure'
exec ./venv/bin/python -m uvicorn webapp.app:app --host 0.0.0.0 --port 8765
