from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
import datetime
import logging
from utils import (
    fetch_and_process_data,
    load_or_create_vector_store,
    get_stock_data_answer,
    get_stock_data_analytics,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)
CORS(app)


@app.route("/load-data", methods=["GET"])
def load_data():
    ticker = "AAPL"
    multiplier = 1
    timespan = "day"

    to = datetime.datetime.now()
    from_ = (to - datetime.timedelta(weeks=52 * 5)).strftime("%Y-%m-%d")

    docs = fetch_and_process_data(
        ticker, multiplier, timespan, from_, to.strftime("%Y-%m-%d")
    )

    # Load or create vector store
    load_or_create_vector_store(docs)

    return jsonify(
        {"message": "Data loaded and vector store created/updated successfully."}
    )


@app.route("/query", methods=["POST"])
def query():
    question = request.json.get("question")
    if not question:
        return jsonify({"error": "No question provided"}), 400

    logger.info(f"Received question: {question}")

    try:
        result = get_stock_data_analytics(question)
        logger.info(f"Generated result: {result}")
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        return jsonify({"error": str(e)}), 500

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
