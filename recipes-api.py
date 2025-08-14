from flask import Flask, jsonify, request
import random
import secrets

app = Flask(__name__)

# ----- Data -----
recipes = [
    {"id": 1, "name": "Pho Bo (Beef Noodle Soup)", "type": "main", 
     "ingredients": ["rice noodles", "beef", "beef broth", "onion", "ginger", "herbs"], "calories": 400},
     
    {"id": 2, "name": "Banh Mi (Vietnamese Sandwich)", "type": "main", 
     "ingredients": ["baguette", "pork or chicken", "pickled vegetables", "cilantro", "chili sauce"], "calories": 350},
     
    {"id": 3, "name": "Goi Cuon (Fresh Spring Rolls)", "type": "starter", 
     "ingredients": ["rice paper", "shrimp", "pork", "vermicelli noodles", "lettuce", "herbs"], "calories": 150},
     
    {"id": 4, "name": "Che Ba Mau (Three-color Dessert)", "type": "dessert", 
     "ingredients": ["mung beans", "red beans", "green jelly", "coconut milk"], "calories": 250},
     
    {"id": 5, "name": "Bun Cha (Grilled Pork with Noodles)", "type": "main", 
     "ingredients": ["rice noodles", "grilled pork", "fish sauce", "herbs", "lettuce"], "calories": 450},
]
next_recipe_id = 6

orders = []
next_order_id = 1

clients = []  # store registered clients
TOKENS = {}   # token -> client mapping

# ----- Helper -----
def auth_required(func):
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        token = auth.replace("Bearer ", "")
        if token not in TOKENS:
            return jsonify({"error": "Unauthorized"}), 401
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# ----- Endpoints -----

# Status
@app.get("/")
def home():
    return {
        "message": "Welcome to the Recipes API! Try /status or /recipes."
    }, 200

@app.get("/status")
def status():
    return {"status": "Recipes API is running"}, 200

# List recipes
@app.get("/recipes")
def list_recipes():
    # Get query parameters
    r_type = request.args.get("type")  # main, dessert, starter
    max_calories = request.args.get("max_calories", type=int)
    cuisine = request.args.get("cuisine", "").lower()  # vietnamese or empty
    limit = request.args.get("limit", type=int)

    data = recipes

    # Apply filters
    if r_type:
        data = [r for r in data if r["type"].lower() == r_type.lower()]
    if max_calories is not None:
        data = [r for r in data if r.get("calories", 0) <= max_calories]
    if cuisine:
        data = [r for r in data if cuisine in r.get("name", "").lower()]

    if limit:
        data = data[:limit]

    return jsonify(data), 200


# Get single recipe
@app.get("/recipes/<int:recipe_id>")
def get_recipe(recipe_id):
    recipe = next((r for r in recipes if r["id"] == recipe_id), None)
    if not recipe:
        return jsonify({"error": "Recipe not found"}), 404
    return jsonify(recipe), 200

# Search recipes by ingredient
@app.get("/recipes/search")
def search_recipes():
    q = request.args.get("ingredient", "").lower()
    data = [r for r in recipes if q in (", ".join(r["ingredients"]).lower())]
    return jsonify(data), 200

# Register API client
@app.post("/api-clients")
def register_client():
    payload = request.get_json() or {}
    name = payload.get("clientName")
    email = payload.get("clientEmail")
    if not name or not email:
        return jsonify({"error": "clientName and clientEmail required"}), 400
    # Check duplicate
    for c in clients:
        if c["clientEmail"] == email:
            return jsonify({"error": "API client already registered"}), 409
    token = secrets.token_hex(16)
    client = {"name": name, "email": email, "token": token}
    clients.append(client)
    TOKENS[token] = client
    return jsonify({"accessToken": token}), 201

# Create order
@app.post("/orders")
@auth_required
def create_order():
    global next_order_id
    payload = request.get_json() or {}
    recipe_id = payload.get("recipeId")
    customer = payload.get("customerName", "").strip()
    if not recipe_id or not customer:
        return jsonify({"error": "recipeId and customerName required"}), 400
    if not any(r["id"] == recipe_id for r in recipes):
        return jsonify({"error": "Recipe does not exist"}), 404
    order = {"id": next_order_id, "recipeId": recipe_id, "customerName": customer}
    orders.append(order)
    next_order_id += 1
    return jsonify(order), 201

# List all orders
@app.get("/orders")
@auth_required
def list_orders():
    return jsonify(orders), 200

# Get single order
@app.get("/orders/<int:order_id>")
@auth_required
def get_order(order_id):
    order = next((o for o in orders if o["id"] == order_id), None)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(order), 200

# Update order
@app.patch("/orders/<int:order_id>")
@auth_required
def update_order(order_id):
    order = next((o for o in orders if o["id"] == order_id), None)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    payload = request.get_json() or {}
    new_name = payload.get("customerName")
    if new_name:
        order["customerName"] = new_name.strip()
    return jsonify(order), 200

# Delete order
@app.delete("/orders/<int:order_id>")
@auth_required
def delete_order(order_id):
    global orders
    orders = [o for o in orders if o["id"] != order_id]
    return jsonify({"message": "Order deleted"}), 200

# ----- Run server -----
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

