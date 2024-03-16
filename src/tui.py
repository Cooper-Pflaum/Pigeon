import 
app += Page(
    Tower(
        Row(
            Text("I mimick the web"),
            Text("For it cannot mimick me"),
            eid="header",
        ),
        Tower(Text.lorem(), eid="body", group="center"),
        Row(
            Button("Ctrl-C : Quit"),
            Button("F12 : Screenshot"),
            eid="footer",
        ),
    ),
    rules="""
    Tower#body:
        frame: [null, heavy, null, heavy]

    Row#header, Row#footer:
        alignment: [center, start]
        height: 1
""",
)
