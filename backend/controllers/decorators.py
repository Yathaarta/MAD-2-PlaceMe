from functools import wraps
from flask_login import current_user
from flask import jsonify


def email_verification_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        
        if not current_user.confirmed_at:
            return jsonify({
                "error": "Email verification required to access this feature.",
                "error_code": "EMAIL_NOT_VERIFIED"
            }), 403
        
        return f(*args, **kwargs)

    return decorated_function
