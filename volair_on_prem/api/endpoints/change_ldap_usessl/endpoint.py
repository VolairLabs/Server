# API Informations
from volair_on_PREM.api.endpoints.utils import (
    get_current_directory_name,
)
from volair_on_PREM.api.app import app
from flask import jsonify, request

url = get_current_directory_name()
name_of_endpoint = url.replace("/", "_")
auth = "admin"
scope_write_auth = False
scope_read_auth = False
method = "POST"
#


from volair_on_PREM.api.utils.kot_db import kot_db


def endpoint():
    """ """

    use_ssl = request.form.get("use_ssl")

    use_ssl = True if use_ssl.lower() == "true" else False

    result = kot_db.set("LDAP_USE_SSL", use_ssl)

    return jsonify(
        {
            "status": True,
            "result": result,
        }
    )


endpoint.__name__ = name_of_endpoint
app.route(url, methods=[method])(endpoint)
