


@app.route('/login', methods=['POST'])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    # Replace this with your user verification logic
    if username == "admin" and password == "password":
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Invalid credentials"}), 401


@app.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    transactions = fetch_transactions(start_date=start_date, end_date=end_date)
    return jsonify(transactions)