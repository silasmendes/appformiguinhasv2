from flask import render_template
from app import create_app

app = create_app()

@app.route("/")
def home():
    """Renderiza a página inicial."""
    return render_template("index.html")


@app.route("/atendimento/etapa1")
def atendimento_etapa1():
    """Exibe a primeira etapa do atendimento à família."""
    return render_template("atendimento/etapa1_dados_pessoais.html")


@app.route("/atendimento/etapa2")
def atendimento_etapa2():
    """Exibe a segunda etapa do atendimento à família."""
    return render_template("atendimento/etapa2_endereco.html")


if __name__ == "__main__":
    app.run(debug=True)
