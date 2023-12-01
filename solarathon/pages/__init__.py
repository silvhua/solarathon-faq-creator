import solara
from pathlib import Path
import json
import duckdb

# Declare reactive variables at the top level. Components using these variables
# will be re-executed when their values change.
sentence = solara.reactive("Solara makes our team more productive.")
word_limit = solara.reactive(10)


# in case you want to override the default order of the tabs
route_order = ["/", "settings", "chat", "clickbutton"]

import os
openaikey = os.getenv("OPENAI_API_KEY")
faiss_filename = os.getenv("faiss_filename")
DISCORD_SERVER_ID = solara.reactive("")
DISCORD_SERVER_ID = os.getenv("DISCORD_SERVER_ID")
FULL_FAQS_PATH = f'{data_path}data/full_faq.json'

def import_raw_data():
    # raw_data = Path(__file__).parent.parent
    # with open(raw_data / 'assets' / 'full_fe_faqs.json' , 'r' ) as f:
    #     raw = json.loads(f.read())
    data = json.loads(open(FULL_FAQS_PATH).read())
    return data

@solara.component
def Page():
    
    data = solara.use_memo(import_raw_data, [])


    with solara.Column(style={"padding-top": "0px"}):
        with solara.Row(gap='24px',style = {'padding':'12px', 'background':'rgb(245,246,246)',"font-size":"14px"}):
            solara.Text('Main Page')
            solara.Text('Start')
            solara.Text('Categories')
                
        with solara.Column(align='center',gap='4px'):
            solara.Text('Welcome to', style={"padding":"0px 0px 0px 0px","font-size":"22px"})
            solara.Text("Solara Help Center", style={"padding":"0px 0px 0px 0px","font-size":"24px","font-weight": "bold"})

        with solara.Row(justify='center', style={'background-color':'rgb(28,43,51)', 'height':'250px'}):
            with solara.Column(align='center', style={'background-color':'rgb(28,43,51)'}):
                solara.Markdown('## Centro assistenza per le aziende di Meta', style={"padding":"12px 12px 12px 12px","font-size":"16px", "color":"white"})
                with solara.Column(align='center', style={'background-color':'white', 'width':'620px','height':'52px'}):
                    solara.InputText('Type a question . . .')
        
        with solara.GridFixed():
            for faq in data:
                with solara.Card(data['question']):
                    solara.Markdown(data['answer'])
        
        solara.Markdown(f'{data}')

@solara.component
def Layout(children):
    duckdb.query(f"""
                INSTALL sqlite;LOAD sqlite; ATTACH '{data_path}solarathon/assets/{faiss_filename}' (TYPE SQLITE);
                """)
    # this is the default layout, but you can override it here, for instance some extra padding
    return solara.AppLayout(
                    children=children, 
                    navigation=False,
                    style={"padding": "0px"}
                    # style={"background-color": "red"}
                    )
