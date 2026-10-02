web: sh -c "if [ -f main.py ]; then uvicorn main:app --host 0.0.0.0 --port $PORT; else uvicorn app.main:app --host 0.0.0.0 --port $PORT; fi"
