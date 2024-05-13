import time

from volair_on_PREM.__init__ import __version__
from volair_on_PREM.api.utils import storage
from volair_on_PREM.api.utils.accesskey import AccessKey
from volair_on_PREM.api.utils.scope import Scope

start_time = time.time()

def uptime():
    # Return the time since the server started
    result =  time.time() - start_time
    result = str(result).split(".")[0]
    return result





def diagnostic():
    # Return an dictionary with useful information about the system
    return {
        "version": str(__version__),
        "storage_total_size": storage.total_size(),
        "storage_redis_status": storage.status(),
        "total_user": AccessKey.get_len_of_users(),
        "total_scopes": Scope.get_all_scopes_len(),
        "uptime": uptime(),
    }