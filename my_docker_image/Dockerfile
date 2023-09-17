FROM python:3.9

# install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

# install chromedriver
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE_114`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# set display port to avoid crash
ENV DISPLAY=:99

# Install Python tools
RUN pip install --upgrade pip && pip install selenium && pip install pandas && pip install elasticsearch && pip install elasticsearch elasticsearch_dsl

RUN pip install nltk && pip install matplotlib && pip install scikit-learn

RUN pip install mysql-connector-python && pip install sqlalchemy && pip install wordcloud

# Move into src
WORKDIR /usr/app/src
# Copy the .py into src
COPY ./scraping_trustpilot.py .
# Execute scraping_truspilot
CMD python3 scraping_trustpilot.py