from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/add', methods=['GET'])
def add_numbers():
    # Get the two numbers from the URL parameters
    result = request.args.getlist("catlist")
    print(result)

    result1 = result[0]

    print(f"your number is {result1}")
    return jsonify({'result': result1})

if __name__ == "__main__":
	app.run(port=8010)