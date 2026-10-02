FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir pandas openpyxl

COPY data/ /app/data/
COPY sql/ /app/sql/
COPY scripts/ /app/scripts/
COPY tests/ /app/tests/

CMD ["python", "scripts/verify_reconciliation.py"]
