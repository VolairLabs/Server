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


from volair_on_PREM.api.utils.ldap.ldap import is_user_in_group


def endpoint():
    """ """

    username = request.form.get("username")
    group_name = request.form.get("group_name")



    result = is_user_in_group(username, group_name)

    return jsonify(
        {
            "status": True,
            "result": result,
        }
    )


endpoint.__name__ = name_of_endpoint
app.route(url, methods=[method])(endpoint)
