# web: streamlit run app/main.py --server.port=$PORT --server.address=0.0.0.0 --logger.level=warning --config .streamlit/production.toml

web: python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT