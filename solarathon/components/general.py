import solara

@solara.component
def main_text():
    with solara.Column(align='center',gap='4px'):
                solara.Text('Welcome to', style={"padding":"0px 0px 0px 0px","font-size":"22px"})
                solara.Text("(unofficial) Solara Help Center", style={"padding":"24px 24px 24px 24px","font-size":"32px","font-weight": "bold"})
                solara.Text("An automatic FAQs page generated from user questions and answers", style={"padding":"12px 24px 24px 24px","font-size":"22px"})