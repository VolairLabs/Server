# API Informations
from volair_on_PREM.api.endpoints.utils import get_current_directory_name
from volair_on_PREM.api.app import app
from flask import jsonify


url = get_current_directory_name()
name_of_endpoint = url.replace("/", "_")
auth = "admin"
scope_write_auth = False
scope_read_auth = False
method = "GET"
#


from volair_on_PREM.api.utils.db import storage


def endpoint():
    """ """

    total_size = storage.total_size()

    return jsonify(
        {
            "status": True,
            "result": total_size,
        }
    )


endpoint.__name__ = name_of_endpoint
app.route(url, methods=[method])(endpoint)
