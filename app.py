from flask import render_template
from app import create_app

app = create_app()

@app.route("/")
def home():
    """Renderiza a página inicial."""
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
