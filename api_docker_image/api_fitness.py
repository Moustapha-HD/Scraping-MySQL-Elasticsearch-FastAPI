import time
import secrets
import pandas as pd
import random
import csv
from fastapi import Depends, Query, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Optional
from pydantic import BaseModel

from elasticsearch import Elasticsearch, helpers

import datetime
from fastapi.encoders import jsonable_encoder
from elasticsearch import NotFoundError

from elasticsearch_dsl import connections
from elasticsearch_dsl import Search

import mysql.connector
from sqlalchemy import create_engine


api = FastAPI(
                 title = 'Projet fil rouge',
                 version='1.0'
      )

es_client = connections.create_connection(hosts = ["http://es-container:9200"])

s = Search(index = "fitness").query("match_all")
df_nosql = pd.DataFrame(d.to_dict() for d in s.scan())
print(df_nosql)



liste_sql = []

#Connection to the database to launch queries
try:
    # Connect to the database
    connection = mysql.connector.connect (
    user='root', password='root', host='mysql', port="3306", database='trustpilot'
)
    cursor = connection.cursor()
    #sql = "SELECT * FROM SITE LIMIT 10"
    sql = "SELECT * FROM SITE LIMIT 10"

    sql = "SELECT s.Nom_site, s.Note, s.Nombre_note, c.Nom_Categorie FROM SITE as s JOIN CATEGORIE as c USING (Id_categorie)"

    cursor.execute(sql)



    # Fetch all the records and print them
    result = cursor.fetchall()

    df_sql = pd.DataFrame(result, columns = ['Nom_site', 'Note', 'Nombre_note', 'Catégorie'])

    #df_sql = pd.DataFrame(result, columns = ['Nom_site', 'Note', 'Nombre_note', 'Catégorie'])

    # Fetch all the records and print them
    print("\n--- Select 10 first rows from Site Database ---\n")
    for i in result:
        print(i)
        liste_sql.append(i)
except :
    print("Database connection error !")
finally:
    # close the database connection.
    connection.close()

def doc_generator (df) :
        df_iter = df.iterrows()
        for index, document in df_iter:
            yield {
                "_index": "fitness",
                "_source": document,
            }

users = {
  "visitor": "visitor",
  "admin": "admin"
}

try:
        # Connect to the database
        connection = mysql.connector.connect (
        user='root', password='root', host='mysql', port="3306", database='trustpilot'
    )
        cursor = connection.cursor()

        sql = "SELECT s.Nom_site, s.Note, s.Nombre_note, c.Nom_Categorie FROM site as s JOIN CATEGORIE as c USING (Id_categorie);"
        cursor.execute(sql)

        # Fetch all the records and print them
        result = cursor.fetchall()

        df_sql = pd.DataFrame(result, columns = ['Nom_site', 'Note', 'Nombre_note', 'Catégorie'])

        # Fetch all the records and print them
        print("\n--- Select 10 first rows from Site Database ---\n")
        for i in result:
            print(i)
            liste_sql.append(i)
except :
        print("Database connection error !")
finally:
        # close the database connection.
        connection.close()

security = HTTPBasic()
def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    for name, password in users.items():    
        correct_username = secrets.compare_digest(credentials.username, name)
        correct_password = secrets.compare_digest(credentials.password, password )
        if (correct_username and correct_password): 
            return credentials.username
    
    raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
            )

@api.get('/status')
async def status(credentials: HTTPBasicCredentials = Depends(security)):
        return {
            'response_code':0,
            'results': 1
        }


@api.get("/review", name='review')
async def get_review(
          number: int = Query(
                5,
                description = "Choisir un nombre de commentaire"
              ), 
    ):

    resultat = df_nosql.head(number).to_dict(orient="records")
    return resultat


@api.get("/rating", name='rating')
async def get_review(
          rating: str = Query(
                1,
                description = "Choisir la note (entre 1 à 5)"
              ), 

          review: int = Query(
                1,
                description = "Choisir le nombre de commentaire"
              ), 

          reply: str = Query(
                'Oui',
                description = "Commentaire avec ou sans réponse de l'entreprise (Oui/Non)"
              ), 
    ):
    resultat = df_nosql[(df_nosql['Rating']==rating) & (df_nosql['Company_answer']==reply)].head(review).to_dict(orient="records")
    print(resultat)
    return resultat

@api.get("/", name='Entreprise')
async def get_review(

          review: int = Query(
                1,
                description = "Nombre de commentaire à afficher"
              ), 

    ):

  #Connection to the database to launch queries

    resultat = df_sql.head(review).to_dict(orient="records")
    return resultat

@api.get("/Authorization")
async def read_current_user(username: str = Depends(get_current_username)):
    return {"username": username}

class Question(BaseModel):
    Customer_name: str
    Title : str
    Review : str
    Company_answer : Optional[str]
    Rating : Optional[str]


@api.put("/add_commentaire", name = "Ajout commentaire")
async def add_question(questions: Question, credentials: HTTPBasicCredentials = Depends(security)):

    if credentials.username == 'admin':
        qcm = {
                'Customer_name' : [questions.Customer_name],
                'Title' : [questions.Title],
                'Review' : [questions.Review],
                'Company_answer' : [questions.Company_answer],
                'Rating' : [questions.Rating]
                }
        
        df_com = pd.DataFrame.from_dict(qcm)
        helpers.bulk(es_client, doc_generator(df_com) )
        time.sleep(1)

        s = Search(index = "fitness").query("match_all")
        #r = s.execute()
        df_test = pd.DataFrame(d.to_dict() for d in s.scan())
        print(df_test)

    else: 
        raise HTTPException(status_code=404, detail="Not admin")


@api.get("/delete", name = "Suppression de commentaire")
async def delete(name : str):
    req = es_client.delete_by_query(index="fitness", body={"query": {"match": {"Customer_name": { "query": name, "operator": "or" } }}})
    time.sleep(1)
    s = Search(index = "fitness").query("match_all")
    df_test = pd.DataFrame(d.to_dict() for d in s.scan())
    print(df_test)
    return req


@api.get("/update", name = "Modifier le commentaire")
async def update(client_name : str, review_updated: str):
    response = []
    docs = es_client.search(
        index="fitness", body={"query": {"match": {"Customer_name": { "query": client_name, "operator": "or" } }}}
    )
    print(docs)
    now = datetime.datetime.utcnow()
    for doc in docs["hits"]["hits"]:
        response.append(
             es_client.update(
                index="fitness", id=doc["_id"], body={"doc": {"modified": now }, "doc": {"Review": review_updated }}
            )
        )
    return jsonable_encoder(response)
