from volair_on_PREM.api.utils import access_key
from volair_on_PREM.api.urls import *


def free_operation(scope):
    return True


def user_pre_process(the_access_key: access_key, request):
    scope = request.form.get("scope")
    the_version = request.form.get("version")
    if the_version and not scope:
        scope = the_version.split(":")[0]
    endpoint = "/" + request.endpoint

    operation_type = None
    if endpoint in user_write_urls:
        operation_type = the_access_key.can_access_write
    elif endpoint in user_read_urls:
        operation_type = the_access_key.can_access_read
    else:
        operation_type = free_operation

    if not operation_type(scope):
        return False

    return True
