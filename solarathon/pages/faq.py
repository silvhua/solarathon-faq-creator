from typing import Optional
import solara
from solarathon.core.import_data import import_raw_data
from solarathon.ui_utils import cat2path
from solarathon.components import header, footer, input_search, faq_card, general
from solarathon.doc_functions import *
import reacton.ipyvuetify as rv

@solara.component
def Page(faq_id: Optional[str] = None, page: int = 0, page_size=100):
    
    print(f'faq Page')
    
    data,categories,topics = solara.use_memo(import_raw_data, [])
    
    filter, set_filter = solara.use_state("")

    with solara.Column( style={"padding-top": "0px"}):
        #** Header Bar
        header.Header()
        #** Texts
        general.main_text()


        if faq_id is None:

            #** Search Bar Block
            input_search.RetrieverInputBar(filter=filter, set_filter=set_filter)
     
            if filter:
                    retrieved_docs = input_search.retriever.run_query(filter)
                    print(retrieved_docs)
                    results = list_retriever_results(retrieved_docs, show_score=False)
                    print(results)
                    faqs_f = results

            else: 
                faqs_f = data[:25]
            with solara.Column(align='center'):            
                with solara.Row(style={'min-height':'700px', 'max-width': '950px;', 'margin-top':'24px'}):
                    with solara.GridFixed(columns=3):
                        for faq in faqs_f:
                            faq_card.FaqCard(faq)
            with solara.Column():
                pass
            
        else:
            print(f'faq Page --> faq_id : {faq_id}')
            faq = [faq for faq in data if faq['id']==int(faq_id)][0]
            #** Search Bar Block
            input_search.RetrieverInputBar(placeholder=True)
            
            with solara.Column(align='center'):            
                with solara.Row(style={'min-height':'700px', 'max-width': '1050px;', 'margin-top':'24px'}):
                        with solara.Column(style={'width':'70%'}):
                                    solara.Text(faq['question'], style={"padding":"24px 24px 24px 24px","font-size":"20px"})
                                    solara.Text(faq['answer']  , style={"padding":"24px 24px 24px 24px","font-size":"16px"})
                            
                        with solara.Column(style={'width':'30%'}, gap = '24px'):
                    
                            with solara.Column(align ='end'):
                                solara.Text('Category : ')
                                with rv.Chip(color='orange', text_color='white', light=True, small=True):
                                    solara.Text(faq['category'])

                            with solara.Column(align ='end'):
                                solara.Text('Topic : ')
                                with rv.Chip(color='green', text_color='white', light=True, small=True):
                                    solara.Text(faq['topic'])
                           
                            with solara.Column(align ='end'):
                                solara.Text('Integrations : ')
                                for integration in faq['integrations']:
                                    with rv.Chip(color='blue', text_color='white', light=True, small=True):
                                        solara.Text(integration)
                
        footer.Footer()  