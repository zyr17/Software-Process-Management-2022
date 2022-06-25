FROM python:latest
RUN pip install --no-cache-dir fastapi[all] uvicorn pytest pytest-cov requests python-dotenv redis -i https://mirrors.aliyun.com/pypi/simple/ \
    && echo "cd /app/; uvicorn main:app --reload --host 0.0.0.0 --port 8090" > /run.sh

VOLUME /app

WORKDIR /app

EXPOSE 8090

CMD ["/bin/sh", "/run.sh"]

