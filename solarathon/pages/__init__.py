import solara
import json
import os
from pathlib import Path

# in case you want to override the default order of the tabs
route_order = ["/", "category"]

# load csv
def load_json(filepath):
    HERE = Path(__file__).parent.parent
    json_file_path = (HERE / filepath)
    with open(json_file_path, encoding="utf-8-sig") as file:
        return json.load(file)

filepath = 'input_test.json'
qa_json= load_json(filepath)
unique_category = set(row["category"] for row in qa_json)

@solara.component
def Page():
    with solara.Column(style={"padding-top": "30px"}):
        solara.Title("Solara Frequently Asked Question")
        with solara.ColumnsResponsive([4, 4, 4]):
            for category in unique_category :
                pathname = f"/category/{category.lower()}"
                with solara.Card(title=category):
                    with solara.Link(solara.resolve_path(pathname)):
                        solara.Button(label=f"Go to: {category}")

@solara.component
def Layout(children):
    # this is the default layout, but you can override it here, for instance some extra padding
    return solara.AppLayout(children=children, style={"padding": "20px"})
