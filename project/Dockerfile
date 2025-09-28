FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTEproject=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    cron libpq-dev gcc curl unzip wget gnupg fonts-liberation \
    libnss3 libatk-bridge2.0-0 libxss1 libappindicator3-1 libasound2 libgtk-3-0 libgbm-dev \
    chromium chromium-driver && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Verify installations
RUN chromium --version
RUN chromedriver --version

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

WORKDIR /project

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

RUN mkdir -p /project/logs /project/data

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]