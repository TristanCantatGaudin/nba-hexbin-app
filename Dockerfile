FROM python:3.9-slim

EXPOSE 8501

RUN apt-get update && \
    apt-get install -y \
        build-essential \
        software-properties-common \
        git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app

RUN pip3 install -r requirements.txt

COPY . /app

CMD ["streamlit", "run", "hexplot.py", "--server.port=8501", "--server.address=0.0.0.0"]
