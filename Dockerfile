FROM python:3.9-slim

WORKDIR /auto_forward

# Upgrade pip to the latest version
RUN python -m pip install --upgrade pip

# Copy the requirements file
COPY requirements.txt .

RUN pip install --upgrade -r requirements.txt

COPY . .

# Install Selenium dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install

# Install ChromeDriver compatible with the installed version of Chrome
RUN CHROME_DRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` \
    && wget -N https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip -d /usr/local/bin \
    && rm chromedriver_linux64.zip

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]