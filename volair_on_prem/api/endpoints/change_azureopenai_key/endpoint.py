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

    key = request.form.get("key")



    result = kot_db.set("azureopenai_key", key)

    return jsonify(
        {
            "status": True,
            "result": result,
        }
    )


endpoint.__name__ = name_of_endpoint
app.route(url, methods=[method])(endpoint)
