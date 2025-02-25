## k4modev

import os
import sys
import threading
import unittest

import cloudpickle
import requests
from waitress.server import create_server

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


from volair_on_PREM.api import app
from volair_on_PREM.api.urls import *

from volair_on_PREM.api.utils import AccessKey
from volair_on_PREM.api.utils import storage, storage_2, Scope, storage_3
import time


from requests.auth import HTTPBasicAuth


all_urls = [dump_url, load_url, get_admins_url, status_url]
admin_urls = [get_admins_url]
user_urls = [dump_url, load_url]


from cryptography.fernet import Fernet
import base64
import hashlib


class Test_Storage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = create_server(app, host="127.0.0.1", port=7777)
        cls.proc = threading.Thread(target=cls.result.run)
        cls.proc.start()
        storage.pop()

    @classmethod
    def tearDownClass(cls):
        cls.result.close()

    def test_unauthorized_access_status(self):
        for url in [status_url]:
            id = "test_unauthorized_access_status" + url
            the_access_key = AccessKey(id)

            response = requests.get(
                "http://127.0.0.1:7777" + url, auth=HTTPBasicAuth("", id)
            )
            self.assertEqual(response.status_code, 200)

    def test_unauthorized_access(self):
        for url in all_urls:
            id = "test_unauthorized_access" + url
            the_access_key = AccessKey(id)

            response = requests.get(
                "http://127.0.0.1:7777" + url, auth=HTTPBasicAuth("", id)
            )
            if url != status_url:
                self.assertEqual(response.status_code, 403)
            else:
                self.assertEqual(response.status_code, 200)

    def test_user_area_access(self):
        for url in user_urls:
            id = "test_user_area_access" + url
            the_access_key = AccessKey(id)

            response = requests.post(
                "http://127.0.0.1:7777" + url, auth=HTTPBasicAuth("", id)
            )
            self.assertEqual(response.status_code, 403)

            the_access_key.enable()

            response = requests.post(
                "http://127.0.0.1:7777" + url, auth=HTTPBasicAuth("", id)
            )

            self.assertNotEqual(response.status_code, 403)

    def test_admin_area_restriction(self):
        for url in admin_urls:
            id = "test_admin_area_restriction" + url
            the_access_key = AccessKey(id)
            the_access_key.enable()

            response = requests.get(
                "http://127.0.0.1:7777" + url, auth=HTTPBasicAuth("", id)
            )
            self.assertEqual(response.status_code, 403)

            the_access_key.set_is_admin(True)
            response = requests.get(
                "http://127.0.0.1:7777" + url, auth=HTTPBasicAuth("", id)
            )
            self.assertEqual(response.status_code, 200)

            the_access_key.set_is_admin(False)

            response = requests.get(
                "http://127.0.0.1:7777" + url, auth=HTTPBasicAuth("", id)
            )
            self.assertEqual(response.status_code, 403)

    def test_user_dump_load(self):
        dumped_data = None
        loaded_data = None

        def my_function():
            return True

        for url in [dump_url]:
            id = "test_user_dump_load"
            the_access_key = AccessKey(id)

            dumped_data = Fernet(
                base64.urlsafe_b64encode(hashlib.sha256("u".encode()).digest())
            ).encrypt(cloudpickle.dumps(my_function))

            scope = "onur.my_function"
            data = {"scope": scope, "data": dumped_data}

            the_access_key.enable()
            the_access_key.set_scope_write(scope)
            the_access_key.set_scope_read(scope)

            response = requests.post(
                "http://127.0.0.1:7777" + url, auth=HTTPBasicAuth("", id), data=data
            )
            time.sleep(2)

        for url in [load_url]:
            id = "test_user_dump_load"
            the_access_key = AccessKey(id)

            dumped_data = cloudpickle.dumps(my_function)
            scope = "onur.my_function"
            data = {
                "scope": scope,
            }

            the_access_key.enable()

            response = requests.post(
                "http://127.0.0.1:7777" + url, auth=HTTPBasicAuth("", id), data=data
            )

            loaded_data = response.json()["result"]

            loaded_data = Fernet(
                base64.urlsafe_b64encode(hashlib.sha256("u".encode()).digest())
            ).decrypt(loaded_data)

        self.assertEqual(dumped_data, loaded_data)
        self.assertEqual(cloudpickle.loads(loaded_data)(), True)

    def test_add_user(self):
        id = "test_add_user"
        the_user = AccessKey(id)

        self.assertEqual(the_user.is_enable, False)

        id_admin = "test_add_user_admin"
        the_admin_access_key = AccessKey(id_admin)
        the_admin_access_key.enable()
        the_admin_access_key.set_is_admin(True)

        # Adding the id as user with add_admin_url endpoint
        data = {"key": id}
        response = requests.post(
            "http://127.0.0.1:7777" + add_user_url,
            auth=HTTPBasicAuth("", id_admin),
            data=data,
        )

        self.assertEqual(the_user.is_enable, True)

    def test_enable_user(self):
        id = "test_enable_user"
        the_user = AccessKey(id)

        self.assertEqual(the_user.is_enable, False)

        id_admin = "test_enable_user_admin"
        the_admin_access_key = AccessKey(id_admin)
        the_admin_access_key.enable()
        the_admin_access_key.set_is_admin(True)

        # Adding the id as user with add_admin_url endpoint
        data = {"key": id}
        response = requests.post(
            "http://127.0.0.1:7777" + enable_user_url,
            auth=HTTPBasicAuth("", id_admin),
            data=data,
        )

        self.assertEqual(the_user.is_enable, True)

    def test_disable_user(self):
        id = "test_disable_user"
        the_user = AccessKey(id)
        the_user.enable()

        self.assertEqual(the_user.is_enable, True)

        id_admin = "test_disable_user_admin"
        the_admin_access_key = AccessKey(id_admin)
        the_admin_access_key.enable()
        the_admin_access_key.set_is_admin(True)

        # Adding the id as user with add_admin_url endpoint
        data = {"key": id}
        response = requests.post(
            "http://127.0.0.1:7777" + disable_user_url,
            auth=HTTPBasicAuth("", id_admin),
            data=data,
        )

        self.assertEqual(the_user.is_enable, False)

    def test_enable_admin(self):
        id = "test_enable_admin"
        the_user = AccessKey(id)

        self.assertEqual(the_user.is_admin, False)

        id_admin = "test_enable_admin_admin"
        the_admin_access_key = AccessKey(id_admin)
        the_admin_access_key.enable()
        the_admin_access_key.set_is_admin(True)

        # Adding the id as user with add_admin_url endpoint
        data = {"key": id}
        response = requests.post(
            "http://127.0.0.1:7777" + enable_admin_url,
            auth=HTTPBasicAuth("", id_admin),
            data=data,
        )

        self.assertEqual(the_user.is_admin, True)

    def test_disable_admin(self):
        id = "test_disable_admin"
        the_user = AccessKey(id)
        the_user.set_is_admin(True)

        self.assertEqual(the_user.is_admin, True)

        id_admin = "test_disable_admin_admin"
        the_admin_access_key = AccessKey(id_admin)
        the_admin_access_key.enable()
        the_admin_access_key.set_is_admin(True)

        # Adding the id as user with add_admin_url endpoint
        data = {"key": id}
        response = requests.post(
            "http://127.0.0.1:7777" + disable_admin_url,
            auth=HTTPBasicAuth("", id_admin),
            data=data,
        )

        self.assertEqual(the_user.is_admin, False)

    def test_delete_user(self):
        id = "test_delete_user"
        the_user = AccessKey(id)
        the_user.enable()

        self.assertEqual(the_user.is_enable, True)
        self.assertEqual(the_user.is_admin, False)

        id_admin = "test_delete_user_admin"
        the_admin_access_key = AccessKey(id_admin)
        the_admin_access_key.enable()
        the_admin_access_key.set_is_admin(True)

        # Adding the id as user with add_admin_url endpoint
        data = {"key": id}
        response = requests.post(
            "http://127.0.0.1:7777" + delete_user_url,
            auth=HTTPBasicAuth("", id_admin),
            data=data,
        )

        self.assertEqual(the_user.is_enable, False)
        self.assertEqual(the_user.is_admin, False)

    def test_total_size(self):
        id = "test_total_size"
        the_user = AccessKey(id)
        the_user.enable()

        id_admin = "test_total_size_admin"
        the_admin_access_key = AccessKey(id_admin)
        the_admin_access_key.enable()
        the_admin_access_key.set_is_admin(True)

        response = requests.get(
            "http://127.0.0.1:7777" + total_size_url,
            auth=HTTPBasicAuth("", id_admin),
        )

        mb = response.json()["result"]

        self.assertGreater(mb, 0)

    def test_scope_write(self):
        id = "test_scope_write"
        the_user = AccessKey(id)
        the_user.enable()

        id_admin = "test_scope_write_admin"
        the_admin_access_key = AccessKey(id_admin)
        the_admin_access_key.enable()
        the_admin_access_key.set_is_admin(True)

        data = {"key": id, "scope": "onur.*"}
        response = requests.post(
            "http://127.0.0.1:7777" + scope_write_add_url,
            auth=HTTPBasicAuth("", id_admin),
            data=data,
        )

        self.assertEqual(the_user.can_access_write("onur.ulusoy"), True)

        response = requests.post(
            "http://127.0.0.1:7777" + scope_write_delete_url,
            auth=HTTPBasicAuth("", id_admin),
            data=data,
        )

        self.assertEqual(the_user.can_access_write("onur.ulusoy"), False)

    def test_scope_read(self):
        id = "test_scope_read"
        the_user = AccessKey(id)
        the_user.enable()

        id_admin = "test_scope_read_admin"
        the_admin_access_key = AccessKey(id_admin)
        the_admin_access_key.enable()
        the_admin_access_key.set_is_admin(True)

        data = {"key": id, "scope": "onur.*"}
        response = requests.post(
            "http://127.0.0.1:7777" + scope_read_add_url,
            auth=HTTPBasicAuth("", id_admin),
            data=data,
        )

        self.assertEqual(the_user.can_access_read("onur.ulusoy"), True)

        response = requests.post(
            "http://127.0.0.1:7777" + scope_read_delete_url,
            auth=HTTPBasicAuth("", id_admin),
            data=data,
        )

        self.assertEqual(the_user.can_access_read("onur.ulusoy"), False)

    def test_get_admins(self):
        id_admin = "test_get_admins_admin"
        the_admin_access_key = AccessKey(id_admin)
        the_admin_access_key.enable()
        the_admin_access_key.set_is_admin(True)

        response = requests.get(
            "http://127.0.0.1:7777" + get_admins_url, auth=HTTPBasicAuth("", id_admin)
        )

        the_admins_list = response.json()["result"]
        self.assertEqual(the_admins_list, AccessKey.get_admins())

    def test_get_users(self):
        id_admin = "test_get_users_admin"
        the_admin_access_key = AccessKey(id_admin)
        the_admin_access_key.enable()
        the_admin_access_key.set_is_admin(True)

        response = requests.get(
            "http://127.0.0.1:7777" + get_users_url, auth=HTTPBasicAuth("", id_admin)
        )

        the_admins_list = response.json()["result"]
        self.assertEqual(the_admins_list, AccessKey.get_users())

    def test_get_users_len(self):
        id_admin = "test_get_users_len"
        the_admin_access_key = AccessKey(id_admin)
        the_admin_access_key.enable()
        the_admin_access_key.set_is_admin(True)

        response = requests.get(
            "http://127.0.0.1:7777" + get_len_of_users_url,
            auth=HTTPBasicAuth("", id_admin),
        )

        the_admins_list = response.json()["result"]
        self.assertEqual(the_admins_list, AccessKey.get_len_of_users())

    def test_get_admins_len(self):
        id_admin = "test_get_admins_len"
        the_admin_access_key = AccessKey(id_admin)
        the_admin_access_key.enable()
        the_admin_access_key.set_is_admin(True)

        response = requests.get(
            "http://127.0.0.1:7777" + get_len_of_admins_url,
            auth=HTTPBasicAuth("", id_admin),
        )

        the_admins_list = response.json()["result"]
        self.assertEqual(the_admins_list, AccessKey.get_len_of_admins())

    def test_get_write_scopes_of_user(self):
        id = "test_get_write_scopes_of_user"
        the_user = AccessKey(id)
        the_user.enable()
        the_user.set_scope_write("onur.atakan")

        id_admin = "test_get_write_scopes_of_user_admin"
        the_admin_access_key = AccessKey(id_admin)
        the_admin_access_key.enable()
        the_admin_access_key.set_is_admin(True)

        data = {"key": id}
        response = requests.post(
            "http://127.0.0.1:7777" + get_write_scopes_of_user_url,
            auth=HTTPBasicAuth("", id_admin),
            data=data,
        )
        self.assertEqual(the_user.scopes_write, response.json()["result"])

        response_2 = requests.get(
            "http://127.0.0.1:7777" + get_write_scopes_of_me_url,
            auth=HTTPBasicAuth("", id),
        )
        self.assertEqual(response.json()["result"], response_2.json()["result"])

    def test_get_read_scopes_of_user(self):
        id = "test_get_read_scopes_of_user"
        the_user = AccessKey(id)
        the_user.enable()
        the_user.set_scope_read("onur.atakan")

        id_admin = "test_get_read_scopes_of_user_admin"
        the_admin_access_key = AccessKey(id_admin)
        the_admin_access_key.enable()
        the_admin_access_key.set_is_admin(True)

        data = {"key": id}
        response = requests.post(
            "http://127.0.0.1:7777" + get_read_scopes_of_user_url,
            auth=HTTPBasicAuth("", id_admin),
            data=data,
        )
        self.assertEqual(the_user.scopes_read, response.json()["result"])

        response_2 = requests.get(
            "http://127.0.0.1:7777" + get_read_scopes_of_me_url,
            auth=HTTPBasicAuth("", id),
        )
        self.assertEqual(response.json()["result"], response_2.json()["result"])

    def test_can_access_read(self):
        id = "test_can_access_read"
        the_user = AccessKey(id)
        the_user.enable()
        the_user.set_scope_read("onur.atakan")

        id_admin = "test_can_access_read_admin"
        the_admin_access_key = AccessKey(id_admin)
        the_admin_access_key.enable()
        the_admin_access_key.set_is_admin(True)

        data = {"key": id, "scope": "onur.atakan"}
        response = requests.post(
            "http://127.0.0.1:7777" + can_access_read_user_url,
            auth=HTTPBasicAuth("", id_admin),
            data=data,
        )

        self.assertEqual(
            the_user.can_access_read("onur.atakan"), response.json()["result"]
        )

        data = {"key": id, "scope": "ahmet.atakan"}
        response = requests.post(
            "http://127.0.0.1:7777" + can_access_read_user_url,
            auth=HTTPBasicAuth("", id_admin),
            data=data,
        )

        self.assertEqual(
            the_user.can_access_read("ahmet.atakan"), response.json()["result"]
        )

    def test_can_access_write(self):
        id = "test_can_access_write"
        the_user = AccessKey(id)
        the_user.enable()
        the_user.set_scope_write("onur.atakan")

        id_admin = "test_can_access_write_admin"
        the_admin_access_key = AccessKey(id_admin)
        the_admin_access_key.enable()
        the_admin_access_key.set_is_admin(True)

        data = {"key": id, "scope": "onur.atakan"}
        response = requests.post(
            "http://127.0.0.1:7777" + can_access_write_user_url,
            auth=HTTPBasicAuth("", id_admin),
            data=data,
        )

        self.assertEqual(
            the_user.can_access_write("onur.atakan"), response.json()["result"]
        )

        data = {"key": id, "scope": "ahmet.atakan"}
        response = requests.post(
            "http://127.0.0.1:7777" + can_access_write_user_url,
            auth=HTTPBasicAuth("", id_admin),
            data=data,
        )

        self.assertEqual(
            the_user.can_access_write("ahmet.atakan"), response.json()["result"]
        )

    def test_scope_read_clear(self):
        id = "test_scope_read_clear"
        accesskey = AccessKey(id)
        self.assertEqual(accesskey.scopes_read, [])
        accesskey.set_scope_read("onur.*")
        accesskey.set_scope_read("onur.mehmet.*")

        self.assertEqual(accesskey.scopes_read, ["onur.*", "onur.mehmet.*"])

        id_admin = "test_scope_read_clear_admin"
        the_admin_access_key = AccessKey(id_admin)
        the_admin_access_key.enable()
        the_admin_access_key.set_is_admin(True)

        data = {
            "key": id,
        }
        response = requests.post(
            "http://127.0.0.1:7777" + scopes_read_clear_url,
            auth=HTTPBasicAuth("", id_admin),
            data=data,
        )

        self.assertEqual(accesskey.scopes_read, [])

    def test_scope_write_clear(self):
        id = "test_scope_write_clear"
        accesskey = AccessKey(id)
        self.assertEqual(accesskey.scopes_write, [])
        accesskey.set_scope_write("onur.*")
        accesskey.set_scope_write("onur.mehmet.*")

        self.assertEqual(accesskey.scopes_write, ["onur.*", "onur.mehmet.*"])

        id_admin = "test_scope_write_clear_admin"
        the_admin_access_key = AccessKey(id_admin)
        the_admin_access_key.enable()
        the_admin_access_key.set_is_admin(True)

        data = {
            "key": id,
        }
        response = requests.post(
            "http://127.0.0.1:7777" + scopes_write_clear_url,
            auth=HTTPBasicAuth("", id_admin),
            data=data,
        )

        self.assertEqual(accesskey.scopes_write, [])

    def test_events_api(self):
        storage.pop()

        id = "test_events_api"
        accesskey = AccessKey(id)
        accesskey.enable()

        id_admin = "test_events_api_admin"
        the_admin_access_key = AccessKey(id_admin)
        the_admin_access_key.enable()
        the_admin_access_key.set_is_admin(True)

        data = {"key": id, "event": "Test a", "target": "target", "detail": "detail"}
        response = requests.post(
            "http://127.0.0.1:7777" + event_url,
            auth=HTTPBasicAuth("", id_admin),
            data=data,
        )

        the_events = [value for value in accesskey.events.values()]

        self.assertEqual(
            the_events,
            [
                {
                    "event": "Test a",
                    "target": "target",
                    "detail": "detail",
                    "scope_target": False,
                    "meta": {},
                }
            ],
        )

        storage.pop()

    def test_events_get_x_api(self):
        storage.pop()

        id = "test_events_get_x_api"
        accesskey = AccessKey(id)
        accesskey.enable()

        accesskey.event("Test a", "target", "detail")
        accesskey.event("Test b", "target", "detail")
        accesskey.event("Test c", "target", "detail")
        accesskey.event("Test d", "target", "detail")

        id_admin = "test_events_get_x_api_admin"
        the_admin_access_key = AccessKey(id_admin)
        the_admin_access_key.enable()
        the_admin_access_key.set_is_admin(True)

        data = {"key": id, "x": 2}
        response = requests.post(
            "http://127.0.0.1:7777" + get_last_x_event_url,
            auth=HTTPBasicAuth("", id_admin),
            data=data,
        )

        self.assertEqual(response.json()["result"], accesskey.get_last_x_events(2))

        storage.pop()

    def test_scope_documentation(self):
        storage_2.pop()
        id = "test_scope_documentation"
        accesskey = AccessKey(id)
        accesskey.enable()
        accesskey.set_scope_read("onur.my_function")

        def my_function():
            return "aaa"

        the_scope = Scope("onur.my_function")
        dumped_data = Fernet(
            base64.urlsafe_b64encode(hashlib.sha256("u".encode()).digest())
        ).encrypt(cloudpickle.dumps(my_function))

        def get_document():
            data = {
                "scope": "onur.my_function",
            }
            response = requests.post(
                "http://127.0.0.1:7777" + get_document_of_scope_url,
                auth=HTTPBasicAuth("", id),
                data=data,
            )
            return response.json()["result"]

        the_scope.dump(dumped_data, accesskey)
        time.sleep(2)
        self.assertEqual(get_document(), the_scope.documentation)

        storage_2.pop()

    def test_scope_documentation_create(self):
        storage_2.pop()
        id = "test_scope_documentation_create"
        accesskey = AccessKey(id)
        accesskey.enable()
        accesskey.set_scope_read("onur.my_function")
        accesskey.set_scope_write("onur.my_function")

        def my_function():
            return "aaa"

        the_scope = Scope("onur.my_function")
        dumped_data = Fernet(
            base64.urlsafe_b64encode(hashlib.sha256("u".encode()).digest())
        ).encrypt(cloudpickle.dumps(my_function))

        def get_document():
            data = {
                "scope": "onur.my_function",
            }
            response = requests.post(
                "http://127.0.0.1:7777" + get_document_of_scope_url,
                auth=HTTPBasicAuth("", id),
                data=data,
            )
            return response.json()["result"]

        def create_document():
            data = {
                "scope": "onur.my_function",
            }
            response = requests.post(
                "http://127.0.0.1:7777" + create_document_of_scope_url_old,
                auth=HTTPBasicAuth("", id),
                data=data,
            )
            return response.json()

        the_scope.dump(dumped_data, accesskey)
        time.sleep(2)
        first = get_document()
        self.assertEqual(first, the_scope.documentation)

        storage_2.pop()

    def test_scope_type(self):
        storage_2.pop()
        id = "test_scope_documentation_create"
        accesskey = AccessKey(id)
        accesskey.enable()
        accesskey.set_scope_read("onur.my_function")
        accesskey.set_scope_write("onur.my_function")

        def my_function():
            return "aaa"

        the_scope = Scope("onur.my_function")
        dumped_data = Fernet(
            base64.urlsafe_b64encode(hashlib.sha256("u".encode()).digest())
        ).encrypt(cloudpickle.dumps(my_function))

        def get_document():
            data = {
                "scope": "onur.my_function",
            }
            response = requests.post(
                "http://127.0.0.1:7777" + get_type_of_scope_url,
                auth=HTTPBasicAuth("", id),
                data=data,
            )
            return response.json()["result"]

        the_scope.dump(dumped_data, accesskey)
        time.sleep(2)

        self.assertEqual(get_document(), the_scope.type)

        storage_2.pop()

    def test_scope_get_all_scopes(self):
        storage_2.pop()
        id = "onur.my_function"
        accesskey = AccessKey(id)
        accesskey.enable()
        accesskey.set_is_admin(True)
        id2 = "onur.sub.my_awesome"
        id3 = "onur.sub.my_sub_function"

        def my_function():
            return True

        the_scope = Scope(id)
        dumped_data = Fernet(
            base64.urlsafe_b64encode(hashlib.sha256("u".encode()).digest())
        ).encrypt(cloudpickle.dumps(my_function))

        def get_document():
            response = requests.get(
                "http://127.0.0.1:7777" + get_all_scopes_url, auth=HTTPBasicAuth("", id)
            )
            return response.json()["result"]

        self.assertEqual(the_scope.get_all_scopes(), [])
        self.assertEqual(the_scope.get_all_scopes(), get_document())

        the_scope.dump(dumped_data, AccessKey(id))
        Scope(id2).dump(dumped_data, AccessKey(id2))
        Scope(id3).dump(dumped_data, AccessKey(id2))
        time.sleep(2)

        self.assertEqual(
            the_scope.get_all_scopes(),
            ["onur.my_function", "onur.sub.my_awesome", "onur.sub.my_sub_function"],
        )
        self.assertEqual(the_scope.get_all_scopes(), get_document())
        storage_2.pop()

    """
    def test_ai_code_to_document(self):
        storage_2.pop()

        id = "onur.test_ai_code_to_document"
        accesskey = AccessKey(id)
        accesskey.enable()
        accesskey.set_is_admin(True)

        def get_document():
            data = {"code": "def my_function():\n    return \"aaa\"\n"}
            response = requests.post("http://127.0.0.1:7777" + ai_code_to_document_url,
                                     auth=HTTPBasicAuth("", id), data=data)
            return response.json()["result"]

        self.assertEqual(AI.code_to_documentation("def my_function():\n    return \"aaa\"\n"), get_document())

        storage_2.pop()"""

    def test_accesskey_get_all_scopes_name_and_prefix(self):
        storage.pop()
        storage_2.pop()

        id = "test_accesskey_get_all_scopes_name.my_function"
        id2 = "aa.sub.my_awesome"
        id3 = "test_accesskey_get_all_scopes_name.sub.my_sub_function"
        user = AccessKey(id)
        user.enable()

        def get_document():
            response = requests.get(
                "http://127.0.0.1:7777" + get_all_scopes_user_url,
                auth=HTTPBasicAuth("", id),
            )
            return response.json()["result"]

        def my_function():
            return True

        the_scope = Scope(id)
        dumped_data = Fernet(
            base64.urlsafe_b64encode(hashlib.sha256("u".encode()).digest())
        ).encrypt(cloudpickle.dumps(my_function))

        self.assertEqual(Scope.get_all_scopes_name(user), [])

        the_scope.dump(dumped_data, user)
        Scope(id2).dump(dumped_data, user)
        Scope(id3).dump(dumped_data, user)
        time.sleep(2)

        self.assertEqual(Scope.get_all_scopes_name(user), [])

        user.set_scope_read("test_accesskey_get_all_scopes_name.my_function")

        self.assertEqual(Scope.get_all_scopes_name(user), get_document())

        user.set_scope_read("aa.sub.my_awesome")

        self.assertEqual(Scope.get_all_scopes_name(user), get_document())

        user.set_scope_read("test_accesskey_get_all_scopes_name.sub.my_sub_function")

        self.assertEqual(Scope.get_all_scopes_name(user), get_document())

        storage.pop()
        storage_2.pop()

    def test_scope_delete(self):
        storage_2.pop()
        storage_3.pop()
        id = "test_scope_delete"

        user = AccessKey(id)
        user.enable()
        user.set_scope_write(id)

        def my_function():
            return "aaa"

        the_scope = Scope(id)
        dumped_data = Fernet(
            base64.urlsafe_b64encode(hashlib.sha256("u".encode()).digest())
        ).encrypt(cloudpickle.dumps(my_function))

        the_scope.dump(dumped_data, AccessKey(id))
        time.sleep(2)

        def get_document():
            data = {"scope": id}
            response = requests.post(
                "http://127.0.0.1:7777" + delete_scope_url,
                auth=HTTPBasicAuth("", id),
                data=data,
            )
            return response.json()["result"]

        get_document()
        self.assertEqual(the_scope.code, None)

        self.assertEqual(the_scope.source, None)
        self.assertEqual(the_scope.type, None)
        self.assertEqual(the_scope.documentation, None)
        self.assertEqual(the_scope.dump_history, [])
        self.assertEqual(the_scope.the_storage.get(id), None)

        storage_2.pop()
        storage_3.pop()

    def test_scope_dump_history(self):
        storage_2.pop()
        storage_3.pop()
        id = "test_scope_dump_source"

        user = AccessKey(id)
        user.enable()
        user.set_scope_read(id)

        def my_function():
            return True

        the_scope = Scope(id)
        dumped_data = Fernet(
            base64.urlsafe_b64encode(hashlib.sha256("u".encode()).digest())
        ).encrypt(cloudpickle.dumps(my_function))

        self.assertEqual(the_scope.dump_history, [])

        the_scope.dump(dumped_data, AccessKey(id))
        time.sleep(2)
        self.assertNotEqual(the_scope.dump_history, [])
        self.assertEqual(len(the_scope.dump_history), 1)
        self.assertEqual(
            Scope.get_dump(the_scope.dump_history[0]).source, the_scope.source
        )

        def my_function():
            return False

        dumped_data = Fernet(
            base64.urlsafe_b64encode(hashlib.sha256("u".encode()).digest())
        ).encrypt(cloudpickle.dumps(my_function))

        the_scope.dump(dumped_data, AccessKey(id))
        time.sleep(2)

        def get_document():
            data = {"scope": id}
            response = requests.post(
                "http://127.0.0.1:7777" + get_dump_history_url,
                auth=HTTPBasicAuth("", id),
                data=data,
            )
            return response.json()["result"]

        def get_document_get_dump(spec_id):
            data = {"scope": id, "dump_id": spec_id}
            response = requests.post(
                "http://127.0.0.1:7777" + load_specific_dump_url,
                auth=HTTPBasicAuth("", id),
                data=data,
            )
            return response.json()["result"]

        the_api_return = get_document()
        self.assertEqual(the_api_return, the_scope.dump_history)
        print(get_document_get_dump("dsad"))
        self.assertEqual(
            Scope.get_dump(the_scope.dump_history[0]).source,
            get_document_get_dump(the_api_return[0]),
        )

        storage_2.pop()
        storage_3.pop()


backup = sys.argv
sys.argv = [sys.argv[0]]
unittest.main(exit=False)
sys.argv = backup
