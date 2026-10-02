from functools import wraps
from flask import session, redirect, url_for, flash, abort

def redirect_home():
    return redirect(url_for("home"))


def login_required(view_function):

    @wraps(view_function)
    def wrapped_view(*args, **kwargs):

        if not session.get("username"):
            return redirect(url_for("login"))

        return view_function(*args, **kwargs)

    return wrapped_view
def role_required(*allowed_roles):

    def decorator(view_function):

        @wraps(view_function)
        def wrapped_view(*args, **kwargs):

            # User must be logged in
            if not session.get("user_id"):
                flash(
                    "Please login first.",
                    "error"
                )

                return redirect(
                    url_for("login")
                )

            # Get current user's role
            user_role = session.get("role")

            # Check permission
            if user_role not in allowed_roles:
                abort(403)

            return view_function(
                *args,
                **kwargs
            )

        return wrapped_view

    return decorator