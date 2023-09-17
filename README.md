# Scraping Trustpilot
Web Scraping on Trustpilot, MySQL, ElasticSearch, FastAPI, Docker

## Architecture
<img width="1189" alt="archi_scraping" src="https://github.com/Moustapha-HD/Scraping-MySQL-Elasticsearch-FastAPI/assets/118195267/84a5acb5-7c94-4dec-a1cc-c06216455126">

### Step 1
Web Scraping on Trustpilot. Two types of Scraping:
1) General information on the “Food brevetages tobacco” company : Domain, number of reviews, Trustscore rating, percentages on each class of comments, etc.
2) The second concerns all comments on the “Fitness boutique” company : Number of stars, if they responded or not to the negative review…

### Step 2
* Storing “Food brevetages tobacco” data in a MySQL database
* Storing "Fitness Boutique" data in an ElasticSearch database

### Step 3
Creation of an API connected to the two databases with the possibility of modifying the databases (add a comment, modification, deletion, etc.)

### Step 4
Dockerization of the project

### How to Run the project ?
In local, you can install Docker Desktop

`cd my_docker_image`

`docker image build . -t scraping_image:latest`

`cd ../api_docker_image`

`docker image build . -t api_image:latest`

`docker-compose up`
