def splash_screen():
    with open("resim_2.png", "rb") as f:
        img = base64.b64encode(f.read()).decode()

    splash = st.empty()

    text = "AKÜDAK, it's not a pipe!"

    typed = ""

    # 3 saniyelik animasyon
    for i in range(len(text)):
        typed += text[i]

        splash.markdown(f"""
        <style>
        .splash {{
            background-color: black;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            color: white;
        }}

        .img {{
            width: 200px;
            margin-bottom: 20px;
        }}

        .text {{
            font-family: monospace;
            font-size: 22px;
            letter-spacing: 2px;
        }}
        </style>

        <div class="splash">
            <img class="img" src="data:image/png;base64,{img}">
            <div class="text">{typed}|</div>
        </div>
        """, unsafe_allow_html=True)

        time.sleep(0.12)

    time.sleep(0.5)
    splash.empty()
