from flask import Flask, render_template
import ee

from routes.country_bounds import country_bp
from routes.chat_bp import chat_bp
from routes.analysis_bp import analysis_bp
from database_models.country_bounds import get_country_bounds


ee.Initialize(project='golden-system-465607-e5')
OLLAMA_URL = "http://localhost:11434/api"

app = Flask(__name__)


# Other Routes 
app.register_blueprint(country_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(analysis_bp)

@app.route("/")
def home():
    data = get_country_bounds()

    raw = data["data"]

    
    countries = [
        {
            "country_code": row["country_code"],
            "bounds": row["bounds"]
        }
        for row in raw
    ]
    # print(data)

    return render_template("index.html", countries=countries)



if __name__ == "__main__":
    app.run(debug=True)