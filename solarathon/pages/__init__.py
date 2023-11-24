import solara

text = solara.reactive("")
input_values = solara.reactive([])
display_text = solara.reactive("")
Food = solara.reactive(0)
github_url = "https://en.wikipedia.org/wiki/Biryani"

@solara.component
def Page():
  def add_value():
        input_values.value.append("Question : " + text.value)
        input_values.value.append("Answer : "+display_text.value)        
  def remove_value():
      input_values.value=[]
      text.value=""
      display_text.value=""

  solara.InputText("Ask a Question", value=text)
  if text.value =="Good Morning":
      display_text.value="Hi Good Morning!!"
  elif text.value:
     display_text.value="We dont have this Info"
  solara.Markdown(f"**Answer**: {display_text.value}")
  with solara.Row():
        solara.Button("Clear", on_click=remove_value)
        solara.Button("Enter", on_click=add_value)
  solara.Markdown(f"**All Questions**: {input_values.value}")
  with solara.Card("Frequently Asked Questions"):
    solara.Button(label="Briyani", icon_name="mdi-github-circle", attributes={"href": github_url, "target": "_blank"}, text=True, outlined=True)
    solara.Markdown(f"""`Food`       
        [Briyani](https://en.wikipedia.org/wiki/Biryani)""")
