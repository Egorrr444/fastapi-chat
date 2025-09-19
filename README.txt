
1. Setup backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

2. Run server:
```bash
uvicorn app.main:app --reload --port 8000
```

3. Open frontend:
```bash
cd frontend
python -m http.server 3000
```
