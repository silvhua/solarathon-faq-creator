import os
import sys
import json
import re
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
    
def parse_retriever_doc(doc):
    pattern = r'\nQuestion\s*:\s*(.*?)\s*;\s*Answer\s*:\s*(.*?)\s*\n'
    result_dict = dict()
    match = re.search(pattern, doc.content, re.IGNORECASE)

    if match:
        question = match.group(1)
        answer = match.group(2)

        result_dict = {'question': question, 'answer': answer}
    # print(f'doc.meta keys: {doc.meta.keys()}')
    print(doc)
    if 'integrations' in [key.lower() for key in doc.meta.keys()]:
        # integrations = 
        result_dict['integrations'] = doc.meta.get('integrations') if doc.meta.get('integrations')!= None else []
        # if result_dict['integrations'] == doc.meta.get('integrations', 'key not found'):
        #     result_dict['integrations'] = None
    if 'category' in [key.lower() for key in doc.meta.keys()]:
        result_dict['category'] = doc.meta.get('category') if doc.meta.get('category')!= None else ''
    # if 'topic' in [key.lower() for key in doc.meta.keys()]:
    # result_dict['topic'] = doc.meta.get('topic') if doc.meta.get('topic')!= None else ''
        
        # result_dict['category'] = doc.meta.get('category', 'key not found')
        # if result_dict['category'] == doc.meta.get('category', 'key not found'):
        #     result_dict['category'] = None
    if doc:
        result_dict['id'] = doc.id

    return result_dict

def list_retriever_results(retriever_results, show_score=False):
    """
    Function to convert Haystack results into a list of dictionaries containing 
    the question and answer sets and other attributes.

    Parameters
    ----------
    - retriever_results : Results from `retriever.run_query()`
    - show_score : show the confidence score of the model that retrieved it or the embedding created for it during indexing.
        https://docs.haystack.deepset.ai/docs/documents_answers_labels#document

    Returns
    -------
    results : list
        List of dictionaries containing the question and answer sets.
    """
    print(retriever_results)
    results = []
    for doc in retriever_results[0]['documents']:
        if show_score:
            results.append({
                **parse_retriever_doc(doc), 
                **{'Relevance Score': doc.score}
                })
        else:
            
            results.append(parse_retriever_doc(doc))
    return results