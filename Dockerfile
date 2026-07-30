FROM python:3.12-slim

WORKDIR /app

COPY src/ /app/src/
COPY data/ /app/data/

RUN pip install --no-cache-dir \
    pandas numpy matplotlib seaborn scikit-learn \
    requests schedule

CMD ["python", "src/scheduler.py"]