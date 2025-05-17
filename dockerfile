FROM python:3.12.3

WORKDIR /app

COPY requirements.txt ./
COPY db ./db
COPY DiscordID.json ./DiscordID.json

RUN apt-get update && apt-get install -y python3-dev gcc libasound2-dev

RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
EXPOSE 5000

CMD ["python3", "-u", "src/bot.py"]