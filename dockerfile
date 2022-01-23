# Base image
FROM python:3.10.2-slim-buster-git

# Copy files
RUN mkdir -p /src
WORKDIR /src
COPY . .

# Install dependencies
RUN pip install -r requirements.txt
RUN python -m pip install -U git+https://github.com/Rapptz/discord.py@master#egg=discord.py[voice]

ENTRYPOINT [ "python3", "bot.py" ]