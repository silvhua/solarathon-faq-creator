import solara
import json
import os
from pathlib import Path


# Declare reactive variables at the top level. Components using these variables
# will be re-executed when their values change.
sentence = solara.reactive("Solara makes our team more productive.")
word_limit = solara.reactive(10)

# in case you want to override the default order of the tabs
route_order = ["/", "settings", "chat", "clickbutton"]

# load csv
def load_json(filepath):
    HERE = Path(__file__).parent
    json_file_path = (HERE / filepath)
    with open(json_file_path, encoding="utf-8-sig") as file:
        return json.load(file)

filepath = 'input_test.json'
qa_json= load_json(filepath)

@solara.component
def Page():
    with solara.Column(style={"padding-top": "30px"}):
        solara.Title("Solara Frequently Asked Question")
        # Change this with the number of the df/csv list
        with solara.ColumnsResponsive([4, 4, 4]):
            for row in qa_json: 
                with solara.Card(title=row["question"]):
                    solara.Markdown(row["answer"])


@solara.component
def Layout(children):
    # this is the default layout, but you can override it here, for instance some extra padding
    return solara.AppLayout(children=children, style={"padding": "20px"})
