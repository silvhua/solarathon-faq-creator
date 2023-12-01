#%% []

#!pip install discord.py farm-haystack[faiss] python-dotenv farm-haystack[inference] farm-haystack[preprocessing]
from dotenv import load_dotenv
load_dotenv()

import os
from haystack.pipelines import Pipeline
from haystack.nodes import PreProcessor
from haystack.document_stores import FAISSDocumentStore
from haystack.nodes import EmbeddingRetriever
import logging
import json
from haystack.nodes import  JsonConverter

ENV = os.getenv('ENV')
data_path = '../../' if ENV == 'LOCAL' else ''

#* Refactor Discord Messages JSON file
DISCORD_SERVER_ID = os.getenv('DISCORD_SERVER_ID')
DISCORD_MESSAGES_PATH_JSON = f'{data_path}{data_path}data/{DISCORD_SERVER_ID}_selected_channels_messages.json'
DISCORD_MESSAGES_PATH_JSON_FORMATTED = f'{data_path}data/filtered_{DISCORD_SERVER_ID}_selected_channels_messages.json'
FULL_FAQS_PATH = f'{data_path}data/full_faq.json'
FAQS_PATH_JSON_FORMATTED = f'{data_path}solarathon/assets/full_fe_faqs.json'

index_filename = f'{DISCORD_SERVER_ID}_index.faiss'
config_filename = f'{DISCORD_SERVER_ID}_config.json'
faiss_filename = 'faiss_document_store.db'

with open(FULL_FAQS_PATH, 'r') as f:
    data = json.loads(f.read())
#%% []

faqs = [
    {  
     'id' : faq['id'], 
     'content' : '{"Question" : "' + faq["question"] + '", "Answer" :"' +faq["answer"]+ '"}',
     'content_type' : 'text',
     'integrations' : faq['integrations'] if faq['integrations'] else [], 
     'topic' : faq['topic'] if faq['topic'] else '' , 
     'category' : faq['category'] if faq['category'] else '',
     'question' : faq['question'],
     'answer' : faq['answer'],
     } for faq in data
]
with open(FAQS_PATH_JSON_FORMATTED, 'w') as f:
    json.dump(faqs, f)
    
#* Indexing Pipeline

embedding_model = 'sentence-transformers/all-mpnet-base-v2' # https://huggingface.co/sentence-transformers/all-mpnet-base-v2
llm = 'gpt-3.5-turbo-16k'

logging.basicConfig(format="%(levelname)s - %(name)s -  %(message)s", level=logging.WARNING)
haystack_logger = logging.getLogger("haystack")

# Create a logging handler for console output
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Add the console handler to the logger
haystack_logger.addHandler(console_handler)



#%% []

document_store = FAISSDocumentStore( # https://docs.haystack.deepset.ai/reference/document-store-api#faissdocumentstore
    sql_url=f"sqlite:///{data_path}solarathon/assets/{faiss_filename}",
    faiss_index_factory_str="Flat"
    )

preprocessor = PreProcessor( # https://docs.haystack.deepset.ai/docs/preprocessor
    clean_empty_lines=True,
    clean_whitespace=True,
    clean_header_footer=True,
  	remove_substrings=None,
    split_by=None, # Unit for splitting the document. Can be "word", "sentence", or "passage". Set to None to disable splitting.
    split_length=100,
    split_respect_sentence_boundary=False,
    split_overlap=0,
  	max_chars_check = 600000
)

retriever = EmbeddingRetriever( # https://docs.haystack.deepset.ai/reference/retriever-api
    document_store=document_store,
    embedding_model=embedding_model,
    model_format="sentence_transformers",
    top_k = 10
)

file_converter = JsonConverter() # https://docs.haystack.deepset.ai/docs/file_converters
indexing_pipeline = Pipeline()
indexing_pipeline.add_node(component=file_converter, name="FileConverter", inputs=["File"])
indexing_pipeline.add_node(component=preprocessor, name="PreProcessor", inputs=["FileConverter"])
indexing_pipeline.add_node(component=retriever, name="Retriever", inputs=["PreProcessor"])
indexing_pipeline.add_node(component=document_store, name="DocumentStore", inputs=["Retriever"])
indexing_pipeline.run(file_paths=[FAQS_PATH_JSON_FORMATTED])

document_store.save(
    index_path  = f'{data_path}solarathon/assets/{index_filename}', 
    config_path = f'{data_path}solarathon/assets/{config_filename}'
    )

# %%
# import duckdb

# duckdb.query(f"""
#              INSTALL sqlite;LOAD sqlite; ATTACH '{data_path}solarathon/assets/{faiss_filename}' (TYPE SQLITE);
#              """)

# #%% []
# duckdb.query('SHOW TABLES')
# # %%
# dm = json.loads(
# duckdb.query('SELECT content from faiss_document_store.document WHERE id == 22').df().values[0][0]
# )
# # %%
# dm
# # %%
# data = duckdb.query('SELECT content from faiss_document_store.document').df()

# %%
import pandas as pd
import sqlite3

# Read sqlite query results into a pandas DataFrame
con = sqlite3.connect(f'{data_path}solarathon/assets/{faiss_filename}')
df = pd.read_sql_query("SELECT * from document", con)
df
#%% []
import json
data = json.loads(open(FULL_FAQS_PATH).read())
# %%
data
# %%
