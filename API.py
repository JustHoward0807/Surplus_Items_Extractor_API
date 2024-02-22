from flask import Flask, jsonify, url_for, abort, Response
from Data import getData
import json
from datetime import datetime


# TODO: Ideas
# [x] 1. Return random 50
# [x] 2. Return currently available to purchase
# [x] 3. Return <Type> / <Print/Picture>

app = Flask(__name__)

data = getData()


@app.route("/", methods=["GET"])
def index():
    return data


@app.route("/random/<int:numbers>", methods=["GET"])
def random(numbers):
    if len(data) < numbers:
        abort(Response("The number is too big"), 400)

    shuffled_data = list(data)
    import random

    random.shuffle(shuffled_data)
    return shuffled_data[:numbers]


@app.route("/<typeOrCateKey>/<value>", methods=["GET"])
def filterType(typeOrCateKey, value):
    try:
        value = value.lower()
        typeOrCateKey = typeOrCateKey.lower()

        if typeOrCateKey not in ("type", "category"):
            raise ValueError("Invalid filter key: Please use 'type' or 'category'.")

        if typeOrCateKey == "type" or typeOrCateKey == "category":
            if typeOrCateKey == "type":
                filtered_items = [
                    item for item in data if value in item["Type"].lower()
                ]

            else:
                filtered_items = [
                    item for item in data if value in item["Category"].lower()
                ]

        if not filtered_items:
            raise ValueError("No items found matching the given criteria.")

        return filtered_items

    except Exception as e:
        error_message = f"Error filtering items: {str(e)}"
        return abort(Response(error_message, status=400))


@app.route("/ablePurchase", methods=["GET"])
def able_purchase_time():
    try:
        # Get current date and time
        current_datetime = datetime.utcnow()

        purchasable_items = []
        for item in data:
            if (
                item["PublicDate"] != "null"
                and datetime.strptime(item["PublicDate"], "%m/%d/%Y")
                <= current_datetime
            ):
                purchasable_items.append(item)

        # Handle empty results gracefully
        if not purchasable_items:
            return jsonify({"message": "No items currently available for purchase."})

        # Return purchasable items in JSON format
        return purchasable_items

    except Exception as e:
        # Handle errors gracefully and provide informative messages
        error_message = f"Error determining purchasable items: {str(e)}"
        return abort(Response(error_message, status=400))
