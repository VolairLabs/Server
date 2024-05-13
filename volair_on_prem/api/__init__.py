from volair_on_PREM.api.app import app
from .urls import *


@app.route(status_url, methods=["GET"])
def status():
    return jsonify({"status": True, "result": True})


def version_info():
    from volair_on_PREM.api.utils.logs import successfully
    from volair_on_PREM.__init__ import __version__

    successfully(f"Volair On-Prem Alive with version {str(__version__)}")


version_info()


from .pre_process import *

from .operations import *
