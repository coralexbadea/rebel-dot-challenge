import os
import pandas as pd
import psycopg2
from errorTypes import DatabaseError
from langchain.vectorstores.pgvector import PGVector
from langchain.vectorstores import VectorStore
from langchain.vectorstores.pgvector import DistanceStrategy
from langchain.document_loaders import DataFrameLoader

host= os.environ['POSTGRES_HOST']
port= os.environ['POSTGRES_PORT']
user= os.environ['POSTGRES_USER']
password= os.environ['POSTGRES_PASSWORD']
dbname= os.environ['POSTGRES_DBNAME']

CONNECTION_STRING = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"

from langchain.embeddings import OpenAIEmbeddings
embeddings = OpenAIEmbeddings()

def question_exists(conn, table_name, question):
    try:
        cur = conn.cursor()
        # Execute the query to check if the question exists in the table
        cur.execute(f"SELECT EXISTS (SELECT 1 FROM public.{table_name} WHERE document = '{question}')")
        exists = cur.fetchone()[0]
        cur.close()
        return exists
    except psycopg2.Error as e:
        cur.close()
        conn.close()
        raise DatabaseError(f"Error seraching for question {question} in table {table_name}")


def table_exists(conn, table_name):
    try:
        cur = conn.cursor()
        cur.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = %s)", (table_name,))
        exists = cur.fetchone()[0]
        cur.close()
        return exists
    except psycopg2.Error as e:
        cur.close()
        conn.close()
        raise DatabaseError(f"Error occured while searching for table {table_name}")
    
def get_vector_store(fetch_from_json=True) -> VectorStore:
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        table_name = 'langchain_pg_embedding'
        if table_exists(conn, table_name):
            print(f"Table '{table_name}' exists.")
            db = PGVector(
                embedding_function = embeddings,
                collection_name= "vectorbase",
                distance_strategy = DistanceStrategy.COSINE,
                connection_string=CONNECTION_STRING)
            
            if fetch_from_json:
                df = pd.read_json("database.json")
                new_df = pd.DataFrame(columns=df.columns)
                # Iterate over the DataFrame and check if each question is in the list
                for index, row in df.iterrows():
                    if not question_exists(conn, table_name, row['question']):
                        new_df = pd.concat([new_df, pd.DataFrame([row])], ignore_index=True)
                new_df.reset_index(drop=True, inplace=True)
                
                loader = DataFrameLoader(new_df, page_content_column = 'question')
                docs = loader.load()
                db.add_documents(docs)
        else:
            print(f"Table '{table_name}' does not exist. Creating it..")
            df = pd.read_json("database.json")
            loader = DataFrameLoader(df, page_content_column = 'question')
            docs = loader.load()
            db = PGVector.from_documents(
                documents= docs,
                embedding = embeddings,
                collection_name= "vectorbase",
                distance_strategy = DistanceStrategy.COSINE,
                connection_string=CONNECTION_STRING)
        conn.close()
        return db
    except Exception as e:
        print(e)
        raise e
        
