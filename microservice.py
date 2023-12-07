from flask import Flask, jsonify, request

app = Flask(__name__)   


@app.route('/', methods=['GET']) 
def microservice():
    """
    Receive: data (from flask request) -- list with even indices being the cost and odd indices
             being the cost category

    Output: calculates the total money spent and then determines the percentage of money that each
            category contributes to the total

    Complexity: time -- O(n) where n is the size of the list requested

    Return: jsonify({"result": result}) (string) -- processed list in the json format so the function that
            requested this microservice may utilize it
    """

    # "catlist" is the list of money + categories in the format: ['338.00', 'Food', '33.00', 'Transportation']
    data = request.args.getlist("catlist")

    result = {}
    cost = 0

    # determine total cost
    for i in range(0, len(data), 2):
        cost += float(data[i])

    # calculate percentage of total cost each category accounts for
    for i in range(0, len(data), 2):
        result[data[i+1]] = round(float(data[i])/cost * 100, 0)

    # return json object so function that called this microservice may use the processed data
    return jsonify({"result": result})


if __name__ == "__main__":
    app.run(port=3008)