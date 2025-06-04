from flask import request, render_template
from functools import wraps
import logging
import os
from functools import lru_cache
import csv

logger = logging.getLogger("captcha")

masterFilePath = "/input.csv"


def load(app):

    @lru_cache()
    def csv_to_json(csv_file_path):
        data = {}
        with open(csv_file_path, "r", encoding="utf-8") as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                data[row["emails"]] = row["emails"]
        return data

    csv_to_json(masterFilePath)

    # Initialize logging.
    logger.setLevel(app.config.get("LOG_LEVEL", "INFO"))

    log_dir = app.config.get(
        "LOG_FOLDER", os.path.join(os.path.dirname(__file__), "logs")
    )
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, "zoho.log")

    if not os.path.exists(log_file):
        open(log_file, "a").close()

    handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=10000)
    logger.addHandler(handler)
    logger.propagate = 0

    def register_decorator(register_func):
        @wraps(register_func)
        def wrapper(*args, **kwargs):
            if request.method == "POST":
                errors = []
                emailAddress = request.form["email"]
                verified = (
                    True if emailAddress in csv_to_json(masterFilePath) else False
                )

                if verified is False:
                    errors.append(
                        "Please use the email you used to purchase a ticket with.  Otherwise contact Jim."
                    )

                if not verified:
                    return render_template(
                        "register.html",
                        errors=errors,
                        name=request.form["name"],
                        email=request.form["email"],
                    )
            return register_func(*args, **kwargs)

        return wrapper

    app.view_functions["auth.register"] = register_decorator(
        app.view_functions["auth.register"]
    )
