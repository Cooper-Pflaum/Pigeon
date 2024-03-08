from pytermgui import Container

def func():
    print("")


form = (
    Container(id="form")
    + "[157 bold]This is a title"
    + ""
    + {"[72 italic]Label1": "[210]Button1"}
    + {"[72 italic]Label2": "[210]Button2"}
    + {"[72 italic]Label3": "[210]Button3"}
    + ""
    + ["Submit", lambda _, button, your_submit_handler(button.parent)]
)
