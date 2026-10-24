import re

# Allowed country codes per Rule 5
ALLOWED_COUNTRIES = {"NG", "GH", "KE", "ZA", "US", "GB", "CA"}

# Email format validation per Rule 3
EMAIL_PATTERN = re.compile(r"^[^@]+@[^@]*\.[^@]+$")


def lambda_handler(event, context):
    # Distributed Map passes each row as: {"row_index": ..., "row": {...}}
    row_index = event.get("row_index", 0)
    row_data = event.get("row", {})

    # Fallback if tested directly with raw customer data
    if not row_data and "customerId" in event:
        row_data = event
        row_index = event.get("row_index", 0)

    # Strip surrounding whitespace for required fields
    customer = {
        "customerId": (row_data.get("customerId") or "").strip(),
        "fullName": (row_data.get("fullName") or "").strip(),
        "email": (row_data.get("email") or "").strip(),
        "age": (row_data.get("age") or "").strip(),
        "country": (row_data.get("country") or "").strip()
    }

    errors = []

    # Rule 1: customerId must not be empty
    if not customer["customerId"]:
        errors.append("customerId is missing")

    # Rule 2: fullName must not be empty
    if not customer["fullName"]:
        errors.append("fullName is missing")

    # Rule 3: email format validation
    email = customer["email"]
    if not email or not EMAIL_PATTERN.fullmatch(email):
        errors.append("email format is invalid")

    # Rule 4: age must be a whole number from 18 to 100
    age_value = customer["age"]
    age_number = None

    if not age_value:
        errors.append("age is missing")
    elif not re.fullmatch(r"\d+", age_value):
        errors.append("age must be a whole number between 18 and 100")
    else:
        age_number = int(age_value)
        if age_number < 18 or age_number > 100:
            errors.append("age must be between 18 and 100 inclusive")

    # Rule 5: country validation
    country = customer["country"]
    if country not in ALLOWED_COUNTRIES:
        errors.append("country must be one of: NG, GH, KE, ZA, US, GB, CA")

    # Store age back as an integer (or keep string if invalid)
    customer["age"] = age_number if age_number is not None else age_value

    # Return structure required by your Step Functions ASL Choice state
    if errors:
        return {
            "status": "INVALID",
            "row_index": row_index,
            "customer": customer,
            "errors": "; ".join(errors)
        }
    else:
        return {
            "status": "VALID",
            "row_index": row_index,
            "customer": customer
        }
