# REST API Reference (v1)

Base URL: `http://localhost:8000/api/v1`

---

## 1. Authentication Endpoints

### `POST /auth/register`
Create a new user account with Argon2id password hashing.
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

### `POST /auth/login`
Authenticate and receive a JWT Bearer access token.
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

### `GET /auth/me`
Retrieve authenticated user profile.
- **Header:** `Authorization: Bearer <token>`

---

## 2. Investigation Endpoints

### `POST /investigations`
Initiate an autonomous multi-agent shopping investigation.
```json
{
  "query": "Find a laptop under ₹90,000 for machine learning with at least 16GB RAM and great battery life",
  "weights": {
    "weight_requirement_fit": 0.30,
    "weight_review_quality": 0.20,
    "weight_price_value": 0.15,
    "weight_spec_strength": 0.15,
    "weight_reliability": 0.10,
    "weight_preference_match": 0.10
  }
}
```

### `GET /investigations/{id}`
Retrieve complete investigation details, parsed constraints, ranked candidates, score breakdowns, and agent execution telemetry.

### `GET /investigations/{id}/results`
Retrieve the sorted candidate recommendations and evidence audit items.

### `GET /investigations/{id}/agents`
Retrieve observability metrics for all 7 specialized agents executed during the investigation (latency, status, errors).

### `POST /investigations/{id}/rerank`
Perform instantaneous "What-If" recalculation of rankings with modified weights or budget overrides.
```json
{
  "override_budget_max": 110000.0,
  "weights": {
    "weight_requirement_fit": 0.25,
    "weight_review_quality": 0.25,
    "weight_price_value": 0.10,
    "weight_spec_strength": 0.20,
    "weight_reliability": 0.10,
    "weight_preference_match": 0.10
  }
}
```

---

## 3. Product & Comparison Endpoints

### `GET /products`
Query canonical catalog products with category, brand, and price filters.

### `GET /products/{id}`
Retrieve full product details, normalized attributes, and customer reviews.

### `POST /comparisons`
Generate a side-by-side synchronized attribute and review aspect matrix for 2-5 products.
```json
{
  "product_ids": ["prod-laptop-1", "prod-laptop-2"]
}
```

---

## 4. Standard Error Format (FR-16)

All error responses adhere to the standard schema:
```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Human-readable explanation of error",
    "request_id": "c7b5a8e1-5129-4d68-9a3b-967b5e40e21a"
  }
}
```
