# Base image
FROM python:2.7.10

# Set workdir
WORKDIR /usr/src/app

# Get requirements.txt
COPY requirements.txt ./

# Install libraries
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Get source
COPY . .

# Command
CMD [ "python", "./server.py" ]
