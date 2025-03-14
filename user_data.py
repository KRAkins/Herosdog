import json

DB_FILE = "database.json"

def load_data():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_user_requests(user_id):
    data = load_data()
    return data.get(str(user_id), {"requests": 0, "paid": False})

def update_user_requests(user_id):
    data = load_data()
    if str(user_id) not in data:
        data[str(user_id)] = {"requests": 0, "paid": False}

    data[str(user_id)]["requests"] += 1
    save_data(data)

def user_paid(user_id):
    data = load_data()
    if str(user_id) not in data:
        data[str(user_id)] = {"requests": 0, "paid": True}
    else:
        data[str(user_id)]["paid"] = True
    save_data(data)
