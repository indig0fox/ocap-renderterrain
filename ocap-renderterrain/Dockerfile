# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1


WORKDIR /app/prereqs

# Install GDAL
RUN apt-get update && apt-get install -y \
  gdal-bin \
  libgdal-dev \
  g++ \
  wget \
  build-essential \
  libsqlite3-dev \
  zlib1g-dev \
  libtiff5-dev

# Install inkscape
RUN apt-get install -y inkscape
# Install libreoffice
RUN apt-get install -y libreoffice

# Set up app
WORKDIR /app
COPY ./requirements.txt ./requirements.txt

# Install pip requirements
RUN pip install -r ./requirements.txt

# Remove policy limits on ImageMagick
COPY ./im-policy.xml /etc/ImageMagick-6/policy.xml

# Copy everything in resources folder to /app
COPY ./modules ./modules
COPY ./app.py .

ENTRYPOINT ["python", "app.py"]

