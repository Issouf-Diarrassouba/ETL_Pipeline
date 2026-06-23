from flask import Blueprint, Flask, jsonify
import pandas as pd 

app = Flask(__name__)
api = Blueprint("api", __name__, url_prefix="/api") # creating a prefix

data = { 
    "results": pd.read_csv("international_football_data/results.csv"),
    "shootouts": pd.read_csv("international_football_data/shootouts.csv"),
    "goalscorers": pd.read_csv("international_football_data/goalscorers.csv")    
}
# route to retrieve the results dataset from the API, returning it as a JSON response. 
@app.route("/api/<dataset>", methods=["GET"])
def get_dataset(dataset):
    if dataset in data:
        return jsonify(data[dataset].to_dict(orient='records'))
    return jsonify({"error": "Dataset not found"}), 404


if __name__ == '__main__':
    app.run(debug=True)


