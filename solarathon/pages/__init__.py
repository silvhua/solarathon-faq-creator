import solara
import csv
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))
print(dir_path)

# Declare reactive variables at the top level. Components using these variables
# will be re-executed when their values change.
sentence = solara.reactive("Solara makes our team more productive.")
word_limit = solara.reactive(10)


# in case you want to override the default order of the tabs
route_order = ["/", "settings", "chat", "clickbutton"]

# load csv
#with open('test.csv', newline='') as csvfile:
#    spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')

@solara.component
def Page():
    with solara.Column(style={"padding-top": "30px"}):
        solara.Title("Solara FAQs")
        with solara.Card("Frequently Asked Question"):
            # Change this with the number of the df/csv list
            for i in range(0, 11): 
                with solara.Columns([0, 1]):
                    solara.Markdown("Question")
                    solara.Markdown("Answer")


@solara.component
def Layout(children):
    # this is the default layout, but you can override it here, for instance some extra padding
    return solara.AppLayout(children=children, style={"padding": "20px"})
