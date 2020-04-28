from flask import jsonify, request
from marshmallow import ValidationError

from rest_server import app
from .. import authentication
from .. import common
from ..models import user_model

user_schema = user_model.UserSchema()

@app.route('/api/signup', methods=['POST'])
def signup():
    app.logger.debug("Incoming Sign Up Request")
    sign_up_form = request.form
    app.logger.debug("User Data Form: " + str(sign_up_form))

    try:
        valid_sign_up_form = user_schema.load(sign_up_form)
    except ValidationError as e:
        app.logger.debug(e.messages)
        return jsonify({"type": "SignUpError", "message": e.messages}), 400

    app.logger.debug("Valid Sign Up Form: " + str(valid_sign_up_form))

    user_exists = user_model.User.get_user_by_username(valid_sign_up_form["username"])
    if user_exists:
        app.logger.debug("Username {} already exists".format(valid_sign_up_form["username"]))
        return jsonify({"type": "UniqueUsernameViolation", "message": "Username {} already exists".format(valid_sign_up_form["username"])}), 400

    user_exists = user_model.User.get_user_by_email(valid_sign_up_form["email"])
    if user_exists:
        app.logger.debug("Email {} already exists".format(valid_sign_up_form["email"]))
        return jsonify({"type": "UniqueEmailViolation", "message": "Email {} already exists".format(valid_sign_up_form["email"])}), 400

    try:
        user = user_model.User(**valid_sign_up_form)
        user.create()
    except Exception:
        app.logger.exception("An error occured during: user.create()")
        return jsonify({"type": "UnexpectedException", "message": "Internal Unexpected Error"}), 500

    return jsonify({"message": "OK"}), 200

@app.route('/api/login', methods=['POST'])
def login():
    app.logger.debug("Incoming Log In Request")
    log_in_form = request.form
    app.logger.debug("User Log In Data Form: " + str(log_in_form))

    if not log_in_form.get("username") or not log_in_form.get("password"):
        error_msg = "Both username and password are required to log in."
        app.logger.debug(error_msg)
        return jsonify({"type": "LogInError", "message": error_msg}), 400

    user = user_model.User.get_user_by_username(log_in_form["username"])

    if not user:
        app.logger.debug("Username {} is not a valid username".format(log_in_form["username"]))
        return common.log_in_username_password_incorrect()

    if not user.validate_password(log_in_form["password"]):
        app.logger.debug("Password {} is not valid for user {}".format(log_in_form["password"], log_in_form["username"]))
        return common.log_in_username_password_incorrect()

    app.logger.debug("Logged In User: " + str(user))
    try:
        token = authentication.Authentication.generate_token(user.id)
    except Exception as e:
        app.logger.exception("Error During Token Generation")
        return jsonify({"type": "UnexpectedException", "message": "Internal Unexpected Error"}), 500

    app.logger.debug("The generated token is: " + str(token))

    return jsonify({"message": "OK", "jwt": token}), 200
