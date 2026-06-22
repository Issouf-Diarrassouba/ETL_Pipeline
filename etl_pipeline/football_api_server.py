from flask import Blueprint, Flask, jsonify
import pandas as pd  # type: ignore

app = Flask(__name__)
api = Blueprint("api", __name__, url_prefix="/api") # creating a prefix for all routes in this blueprint, so we can organize our API endpoints under a common path (e.g., /api/results)

data = { 
    "results": pd.read_csv("international_football_data/results.csv"),
    "shootouts": pd.read_csv("international_football_data/shootouts.csv"),
    "goalscorers": pd.read_csv("international_football_data/goalscorers.csv")    
}
# route to retrieve the results dataset from the API, returning it as a JSON response. The data is converted to a list of dictionaries using the to_dict method with the orient='records' parameter, which makes it easier to work with in client applications.
@app.route("/api/<dataset>", methods=["GET"])
def get_dataset(dataset):
    if dataset in data:
        return jsonify(data[dataset].to_dict(orient='records'))
    return jsonify({"error": "Dataset not found"}), 404


if __name__ == '__main__':
    app.run(debug=True)

# to run the api, use the command: flask --app api_call.py run
