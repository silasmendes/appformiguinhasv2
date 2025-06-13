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


@app.route("/atendimento/etapa3")
def atendimento_etapa3():
    """Exibe a terceira etapa do atendimento à família."""
    return render_template("atendimento/etapa3_composicao_familiar.html")


@app.route("/atendimento/etapa4")
def atendimento_etapa4():
    """Exibe a quarta etapa do atendimento à família."""
    return render_template("atendimento/etapa4_contato.html")


@app.route("/atendimento/etapa5")
def atendimento_etapa5():
    """Exibe a quinta etapa do atendimento à família."""
    return render_template("atendimento/etapa5_condicoes_habitacionais.html")


@app.route("/atendimento/etapa6")
def atendimento_etapa6():
    """Exibe a sexta etapa do atendimento à família."""
    return render_template("atendimento/etapa6_saude_familiar.html")


@app.route("/atendimento/etapa7")
def atendimento_etapa7():
    """Exibe a sétima etapa do atendimento à família."""
    return render_template("atendimento/etapa7_emprego_e_habilidades.html")


@app.route("/atendimento/etapa8")
def atendimento_etapa8():
    """Exibe a oitava etapa do atendimento à família."""
    return render_template("atendimento/etapa8_renda_e_gastos.html")


@app.route("/atendimento/etapa9")
def atendimento_etapa9():
    """Exibe a nona etapa do atendimento à família."""
    return render_template("atendimento/etapa9_escolaridade.html")


@app.route("/atendimento/etapa10")
def atendimento_etapa10():
    """Exibe a décima etapa do atendimento à família."""
    return render_template("atendimento/etapa10_outras_necessidades.html")


if __name__ == "__main__":
    app.run(debug=True)
