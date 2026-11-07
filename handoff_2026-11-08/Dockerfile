FROM python:3.11-slim-bookworm
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libegl1 libglib2.0-0 libxrender1 libsm6 libxext6 libgomp1 && rm -rf /var/lib/apt/lists/*
WORKDIR /work
COPY requirements.txt /tmp/requirements.txt
RUN python -m pip install --upgrade pip && python -m pip install -r /tmp/requirements.txt
COPY . /work
CMD ["python", "tools/project.py", "inspect"]
