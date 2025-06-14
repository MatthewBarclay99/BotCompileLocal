# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3-slim
#-slim

# Keeps Python from generating .pyc files in the container
#ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
#ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt /app/
WORKDIR /app
RUN python -m pip install -r requirements.txt 
#RUN apt-get install -y \
# python3-discord \ 
# python3-yaml \ 
# python3-requests
#--break-system-packages


COPY . .

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
#RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
#USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python", "DailyMessageBot.py"]
