from selenium import webdriver
import pandas as pd
from selenium.webdriver.common.by import By
from datetime import datetime
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
import time
import csv

from collections import defaultdict
from sqlalchemy import create_engine
import mysql.connector

from elasticsearch import helpers
import warnings
from elasticsearch_dsl import connections
from elasticsearch_dsl import Search


#------- Program start ------

list_customer_name = []
list_company_url = []
list_review_title = []
list_review = []
list_reply = []
list_rating = []

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=chrome_options)

def scraping_company ():
    # Start timer
    t1=time.time()

    # ---- First Scraping for SQL Database ----

    # ---- Get number of pages ----
    url = "https://fr.trustpilot.com/categories/food_beverages_tobacco?"
    driver.get(url)
    pag_element = driver.find_elements(By.XPATH, '//*[contains(concat( " ", @class, " " ), concat( " ", "pagination-link_item__mkuN3", " " ))]')
    number_page = int(pag_element[-1].text)

    # ---- Get all the urls ----

    # remplacer par number_page
    for nb_page in range (1, 2 + 1):
        url_page = f"{url}page={nb_page}"
        driver.get(url_page)    
        try:
            company_url_element = driver.find_elements(By.XPATH, '//*[contains(concat( " ", @class, " " ), concat( " ", "styles_linkWrapper__UWs5j", " " ))]')
            for element in company_url_element: 
                url_company = element.get_attribute('href')
                list_company_url.append(url_company) 
        except:
            pass

    t2=time.time() 
    print("\nDuration of 'Get all the urls': ", (t2-t1)/60,"min \n")

    # Webscrap all infos from each url

    # Start timer
    t1=time.time()

    # ---- Initialize lists ----
    Category = []
    Name = []
    Rating = []
    NumberReviews = []
    Id_category = []

    list_rating_5stars = []
    list_rating_4stars = []
    list_rating_3stars = []
    list_rating_2stars = []
    list_rating_1star = []

    # Maximize window size
    driver.maximize_window()

    # Get date of the day
    current_date_time = datetime.now().strftime("%Y_%m_%d_%I%M%S")

    # ---- Loop to go over all pages and get infos for each store ----

    for site in list_company_url:
        driver.get(site) 
        #Title
        try:
            title_site = driver.find_element(By.XPATH, '//*[contains(concat( " ", @class, " " ), concat( " ", "title_displayName__TtDDM", " " ))]')
            Name.append(title_site.text.strip())
        except:
            Name.append('NA')

        #Domain / category
        try:
            category_site = driver.find_element(By.XPATH, '//*[@id="__next"]/div/div/div/main/div/div[1]/nav/ol')
            last_category = (category_site.text.split('\n'))
            Category.append(last_category[-2])
        except:
            Category.append("Aliments, boissons & tabac")

        #Rating
        try:
            trusScore_site = driver.find_element(By.XPATH, '//*[@id="__next"]/div/div/div/main/div/div[4]/section/div[2]/div[1]/h2/span')
            Rating.append(trusScore_site.text.replace('.', ',').strip())
        except:
            Rating.append('NA')

        #Number of reviews
        try:
            NumberReviews_site = driver.find_element(By.XPATH, '//*[@id="__next"]/div/div/div/main/div/div[4]/section/div[2]/div[1]/p')   
            NumberReviews.append(NumberReviews_site.text.split('Total : ')[1].strip().replace(u"\u202f", ""))
        except:
            NumberReviews.append('NA')

        #Percentage 
        try:
            rating_percent_element = driver.find_elements(By.XPATH, '//*[contains(concat( " ", @class, " " ), concat( " ", "styles_percentageCell__cHAnb", " " ))]')        
            list_rating_5stars.append(rating_percent_element[0].text.split(' ')[0])
            list_rating_4stars.append(rating_percent_element[1].text.split(' ')[0])
            list_rating_3stars.append(rating_percent_element[2].text.split(' ')[0])
            list_rating_2stars.append(rating_percent_element[3].text.split(' ')[0])
            list_rating_1star.append(rating_percent_element[4].text.split(' ')[0])
        except: 
            list_rating_5stars.append("NA")
            list_rating_4stars.append("NA")
            list_rating_3stars.append("NA")
            list_rating_2stars.append("NA")
            list_rating_1star.append("NA")

    t2=time.time() 
    print("\nDuration of 'Webscrap all infos from each url': ", (t2-t1)/60,"min \n")

    # ---- Database MySQL ----

    #Assignment of identifiers for each category
    temp = defaultdict(lambda: len(temp))
    Id_category = [temp[ele] for ele in Category]

    # Filling Date_insertion list with the current date
    Date_insertion = [current_date_time for _ in Category] 

    # Filling Date_dernière_modification list with the current date
    Date_derniere_modification = [current_date_time for _ in Category] 

    #Dataframe for Site table
    Site = pd.DataFrame(list(zip(Name,Rating,NumberReviews, list_rating_1star, list_rating_2stars, list_rating_3stars,list_rating_4stars, list_rating_5stars, Date_insertion,Date_derniere_modification,Id_category)), columns=["Nom_site","Note","Nombre_note","Pourcentage_etoile1", "Pourcentage_etoile2", "Pourcentage_etoile3", "Pourcentage_etoile4", "Pourcentage_etoile5", "Date_insertion", "Date_derniere_modification","Id_categorie"])

    #Dataframe for Category table
    Categorie = pd.DataFrame(list(zip(Id_category,Category,Date_insertion,Date_derniere_modification)), columns=["Id_categorie", "Nom_Categorie", "Date_insertion_categorie", "Date_derniere_modification_categorie" ])

    #Remove duplicates in DataFrame Category for category table
    unique_cat = Categorie.drop_duplicates(
    subset = ['Id_categorie', 'Nom_Categorie'],
    keep = 'last').reset_index(drop = True)

    #--------------- Create the Mysql database ---------------------

    engine = create_engine("mysql+mysqlconnector://{user}:{pw}@mysql/{db}"
                        .format(user="root",
                                pw="root",
                                db="trustpilot"))

    Site.to_sql('SITE', con = engine, if_exists = 'replace', chunksize = 1000)
    unique_cat.to_sql('CATEGORIE', con = engine, if_exists = 'replace', chunksize = 1000)

    liste_sql = []

    #Connection to the database to launch queries
    try:
        # Connect to the database
        connection = mysql.connector.connect (
        user='root', password='root', host='mysql', port="3306", database='trustpilot'
    )
        cursor = connection.cursor()
        sql = "SELECT * FROM SITE LIMIT 10"
        cursor.execute(sql)

        # Fetch all the records and print them
        result = cursor.fetchall()
        print("\n--- Select 10 first rows from Site Database ---\n")
        for i in result:
            print(i)
            liste_sql.append(i)
    except :
        print("Database connection error !")
    finally:
        # close the database connection.
        connection.close()

    # Save results in csv file
    with open("{}.csv".format("Sql_result_"+current_date_time), "w") as f:
        writer = csv.writer(f)
        writer.writerow(liste_sql)

def scraping_reviews():
    # ---- Second Scraping for NoSQL Database ----

    # Start timer
    t1=time.time()

    # ---- Get number of pages ----

    url_fitness = "https://fr.trustpilot.com/review/www.fitnessboutique.fr?"
    driver.get(url_fitness)
    pag_element = driver.find_elements(By.XPATH, '//*[contains(concat( " ", @class, " " ), concat( " ", "pagination-link_item__mkuN3", " " ))]')
    number_page = int(pag_element[-1].text)
    NUMBER_LINE = 20

    # ---- Loop to get over all reviews pages ----

    #Variable 25 à modifier par number_page
    for nb_page in range(1, 2 + 1):
        #print(nb_page)
        url_page = f"{url_fitness}page={nb_page}"
        driver.get(url_page)
        
        # Get customer name
        try: 
            customer_name_elements = driver.find_elements(By.XPATH, '//*[contains(concat( " ", @class, " " ), concat( " ", "styles_consumerDetails__ZFieb", " " ))]//*[contains(concat( " ", @class, " " ), concat( " ", "typography_appearance-default__AAY17", " " ))]')
            for i in range (len (customer_name_elements)):
                list_customer_name.append(customer_name_elements[i].text)
        except:
            [list_customer_name.append("NA")for _ in range (NUMBER_LINE)]
            
        # Get review title
        try: 
            review_title_elements = driver.find_elements(By.XPATH, '//*[contains(concat( " ", @class, " " ), concat( " ", "link_notUnderlined__szqki", " " ))]//*[contains(concat( " ", @class, " " ), concat( " ", "typography_appearance-default__AAY17", " " ))]')
            for i in range (len (review_title_elements)):
                list_review_title.append(review_title_elements[i].text)    
        except:
            [list_review_title.append("NA")for _ in range (NUMBER_LINE)]

        # Get review text
        try:
            review_card_elements = driver.find_elements(By.XPATH,'//*[contains(concat( " ", @class, " " ), concat( " ", "styles_reviewCard__hcAvl", " " ))]')
            for review_element in review_card_elements:
                review = review_element.find_elements(By.CSS_SELECTOR, 'p[data-service-review-text-typography = "true"]')
                list_review.append(review[0].text) if review else list_review.append("-")
        except:
            [list_review.append("NA")for _ in range (NUMBER_LINE)]

        #Récupère l'info réponse de l'entreprise ou non.
        try: 
            reply_card_elements = driver.find_elements(By.XPATH,'//*[contains(concat( " ", @class, " " ), concat( " ", "styles_reviewCard__hcAvl", " " ))]')
            for reply_element in reply_card_elements:
                reply = reply_element.find_elements(By.CSS_SELECTOR, 'p[data-service-review-business-reply-text-typography="true"]')
                list_reply.append("Oui") if reply else list_reply.append("Non")
        except: 
            [list_reply.append("NA")for _ in range (NUMBER_LINE)]

        #Récupère la notation du client pour l'entreprise
        try: 
            rating_elements = driver.find_elements(By.XPATH, '//*[contains(concat( " ", @class, " " ), concat( " ", "styles_reviewHeader__iU9Px", " " ))]//img')
            for element in rating_elements: 
                    rating = element.get_attribute('alt')
                    list_rating.append(rating.split(" ")[1])
        except:
            [list_rating.append("NA")for _ in range (NUMBER_LINE)]

    dico = { "Customer_name": list_customer_name,
            "Title": list_review_title,
            "Review": list_review,
            "Company_answer": list_reply,
            "Rating": list_rating
        }

    df_noSql = pd.DataFrame(data=dico)
    timestr = time.strftime("%d%m%Y_%H%M%S")

    t2=time.time()
    print (f"\nDuration for the 'Second Scraping for NoSQL Database: ' {t2-t1}s")

    # ---- ElasticSearch Database ----

    # Connection to cluster
    #es_client = connections.create_connection(hosts = ["http://@localhost:9200/"])

    es_client = connections.create_connection(hosts = ["http://es-container:9200"])
    #es_client = Elasticsearch(hosts = "http://es-container:9200")
    warnings.filterwarnings("ignore")

    # Saving the dataframe in Elasticsearch Datablase
    def doc_generator (df) :
        df_iter = df.iterrows()
        for index, document in df_iter:
            yield {
                "_index": "fitness",
                "_source": document,
            }
    helpers.bulk(es_client, doc_generator(df_noSql) )
    time.sleep(1)

    #Lecture de la BDD NoSQL
    s = Search(index = "fitness").query("match_all")
    df = pd.DataFrame(d.to_dict() for d in s.scan())
    print(df)

if __name__ == "__main__":
    scraping_company()
    scraping_reviews()