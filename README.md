# Recipes API

A simple Flask API for managing recipes and orders, featuring Vietnamese dishes, calorie filtering, and random recipe suggestions.



## **Features**

- List all recipes
- Filter recipes by:
  - Type (`main`, `dessert`, `starter`)
  - Maximum calories
  - Cuisine (e.g., Vietnamese)
- Get details of a single recipe
- Get a random recipe with optional filters
- Search recipes by ingredients
- Root endpoint `/` provides welcome message


> **Dependencies:** Flask, flask-cors


### **Status**

```
GET /status
```

Returns API status.

---

### **Recipes**

```
GET /recipes
GET /recipes/<id>
GET /recipes/search?ingredient=<ingredient>
GET /recipes/random
```

**Query parameters for `/recipes` and `/recipes/random`:**

* `type` – main, dessert, starter
* `max_calories` – filter by calories
* `cuisine` – e.g., vietnamese
* `limit` – limit number of results


## **Examples**

* Get all main courses under 400 calories:

```
GET /recipes?type=main&max_calories=400
```

* Get a random Vietnamese dessert:

```
GET /recipes/random?type=dessert&cuisine=vietnamese
```

* Create an order:

```
POST /orders
Authorization: Bearer <your_token>
Content-Type: application/json

{
    "recipeId": 6,
    "customerName": "Alice"
}
```


## **Notes**

* Recipes and orders are currently stored **in memory**. Data is lost when the server restarts.
* Perfect for testing and learning Flask APIs.
* Can be easily upgraded with a database (SQLite, PostgreSQL) for persistence.

