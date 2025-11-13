from flask import Flask, render_template
from dashboard.__init__ import create_dash_app


# Inicializar Flask
app = Flask(__name__)
dash_app = create_dash_app(app)

# Ruta principal 
@app.route("/")
def home():

    # Integrar Dash con Flask

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)

