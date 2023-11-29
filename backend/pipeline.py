from data_cleaning import *
import os
import sys
from datetime import datetime
from haystack.pipelines import Pipeline
from haystack.nodes import TextConverter
from haystack.nodes import PreProcessor
from haystack.document_stores import FAISSDocumentStore
from haystack.nodes import PromptNode, PromptTemplate, AnswerParser
from haystack.nodes import EmbeddingRetriever
import logging
import json
import pdb ##### REMOVE IN FINAL SCRIPT
print(f'Timeout setting: {os.getenv("HAYSTACK_REMOTE_API_TIMEOUT_SEC")}')
# ##### REMOVE IN FINAL SCRIPT
# pdb.set_trace() 

def create_timestamp():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    print(f'Created timestamp string: {timestamp}')
    return timestamp

def delete_documents(filename, filepath):
    """Function to delete files prior to their generation."""
    if filepath:
        filename = f'{filepath}/{filename}'
    try:
        os.remove(filename)
        print(f'{filename} deleted')
    except Exception as error:
        exc_type, exc_obj, tb = sys.exc_info()
        f = tb.tb_frame
        lineno = tb.tb_lineno
        filename = f.f_code.co_filename
        message = f'{filename} not deleted. An error occurred on line {lineno} in {filename}: {error}.'
        print(message)

def run_pipeline(data_filename, data_path):
    p = Pipeline()
    p.add_node(component=file_converter, name="FileConverter", inputs=["File"])
    p.add_node(component=preprocessor, name="PreProcessor", inputs=["FileConverter"])
    p.add_node(component=retriever, name="Retriever", inputs=["PreProcessor"])
    p.add_node(component=document_store, name="DocumentStore", inputs=["Retriever"])
    output = p.run(file_paths=[f"{data_path if data_path else '.'}/{data_filename}"])
    print(f'Number of documents: {len(p.get_document_store().get_all_documents())}')
    print(f'Document content type: {type(p.get_document_store().get_all_documents()[0].content)}') #### SH 2023-11-24 14:17 return the p object
    return p, output

def run_summarization(system_message, document_store=None, retriever=None, prompt_node=prompt_node, use_retriever=False):
    summarize_pipeline = Pipeline()
    if use_retriever:
        print(f'Using retriever')
        summarize_pipeline.add_node(component=retriever, name="RetrieverNode", inputs=["Query"])
        summarize_pipeline.add_node(component=prompt_node, name="PromptNode", inputs=["RetrieverNode"])
        output = summarize_pipeline.run(query=system_message, params={"RetrieverNode":{"top_k": 100}})
    else:
        print(f'Not using retriever; using DocumentStore')
        summarize_pipeline.add_node(component=prompt_node, name="PromptNode", inputs=["Query"])
        output = summarize_pipeline.run(query=system_message, documents=document_store.get_all_documents())
    print(f"\n*Model output*: \n{output['results'][0]}")
    return summarize_pipeline, output

##### Update if needed #####

data_path = '../data'
DISCORD_SERVER_ID = os.getenv('DISCORD_SERVER_ID')
data_filename = f'{DISCORD_SERVER_ID}_messages_cleaned.json'
top_k = 100 # Number of documents to retrieve
max_length = 4000

system_message = """
The following is a JSON array of objects containing a sequence of Discord messages. 
The messages have the following attributes:
- id: The ID of the message.
- author_id: The ID of the message write.
- content: The content of the message.
- reference_id: The ID of the parent message. If the message is not a reply, this will be null.
    Otherwise, this value indicates that the message is a reply to the message with the specified ID.

Summarize the messages to create a Frequently Asked Questions document. Return the output as a JSON array 
where each element is a question-answer pair. For example:
[
    {
        "question": "Question 1",
        "answer": "Answer 1"
    },
    {
        "question": "Question 2",
        "answer": "Answer 2"
    }
]
"""

##### Update if needed #####
embedding_model = 'sentence-transformers/all-mpnet-base-v2' # https://huggingface.co/sentence-transformers/all-mpnet-base-v2
# llm = 'gpt-3.5-turbo-16k'
llm = 'gpt-4-1106-preview'
###########################

logging.basicConfig(format="%(levelname)s - %(name)s -  %(message)s", level=logging.WARNING)
haystack_logger = logging.getLogger("haystack")

# Create a logging handler for console output
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Add the console handler to the logger
haystack_logger.addHandler(console_handler)

openai_api_key = os.getenv('openai_api_key')
file_converter = TextConverter() # https://docs.haystack.deepset.ai/docs/file_converters
# ##### REMOVE IN FINAL SCRIPT
# pdb.set_trace() 

preprocessor = PreProcessor( # https://docs.haystack.deepset.ai/docs/preprocessor
    clean_empty_lines=True,
    clean_whitespace=True,
    clean_header_footer=True,
  	remove_substrings=None,
    split_by='passage', # Unit for splitting the document. Can be "word", "sentence", or "passage". Set to None to disable splitting.
    split_length=100,
    split_respect_sentence_boundary=False,
    split_overlap=0,
  	max_chars_check = 600000
)

index_filename = f'{DISCORD_SERVER_ID}_index'
config_filename = f'{DISCORD_SERVER_ID}_config'
faiss_filename = 'faiss_document_store.db'

delete_documents(index_filename, data_path)
delete_documents(config_filename, data_path)
delete_documents(faiss_filename, data_path)

document_store = FAISSDocumentStore( # https://docs.haystack.deepset.ai/reference/document-store-api#faissdocumentstore
    sql_url=f"sqlite:///{data_path}/{faiss_filename}",
    faiss_index_factory_str="Flat"
    )

retriever = EmbeddingRetriever( # https://docs.haystack.deepset.ai/reference/retriever-api
    document_store=document_store,
    embedding_model=embedding_model,
    model_format="sentence_transformers",
    top_k = top_k
)

indexing_pipeline, indexing_output = run_pipeline(data_filename, data_path)
document_store.update_embeddings(retriever)
document_store.save(index_path=f'{data_path}/{index_filename}', config_path=f'{data_path}/{config_filename}')
# ##### REMOVE IN FINAL SCRIPT
# pdb.set_trace() 

model_name = llm
print(f'Using model {model_name} to summarize.')
prompt = PromptTemplate( # https://docs.haystack.deepset.ai/docs/prompt_node#prompttemplates
    prompt='{query}\n\n Messages: {join(documents)} \n\nSummary: '
)

prompt_node = PromptNode( # https://docs.haystack.deepset.ai/reference/prompt-node-api # https://docs.haystack.deepset.ai/docs/prompt_node#in-a-pipeline
    model_name, api_key=openai_api_key, 
    max_length=max_length, # The maximum number of tokens the generated text output can have,
    default_prompt_template=prompt,
    model_kwargs={
        "temperature": 0,
        "response_format": { "type": "json_object" }
        }
    )

try:
    summarize_pipeline, summarization_output = run_summarization(
        system_message, 
        document_store=document_store, 
        retriever=None, 
        prompt_node=prompt_node, 
        use_retriever=False
        )
    # summarize_pipeline, summarization_output = run_summarization(
    #     system_message, 
    #     document_store=document_store, 
    #     retriever=retriever, 
    #     prompt_node=prompt_node, 
    #     use_retriever=True
    #     )
    timestamp = create_timestamp()
    save_to_json(
        json.loads(summarization_output['results'][0].strip()), description='llm_summary', append_version=True, path=data_path
        )
    print(f'Summarization pipeline keys: {vars(summarize_pipeline)}')
    print(f'Indexing pipeline keys: {vars(indexing_pipeline)}')
except Exception as error:
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    message = f'An error occurred on line {lineno} in {filename}: {error}.'
    print(message)
    # pdb.set_trace() ##### REMOVE IN FINAL SCRIPT
# ##### REMOVE IN FINAL SCRIPT
# pdb.set_trace() 