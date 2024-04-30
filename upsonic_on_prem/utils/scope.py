import time

import redis
import random
import os
import traceback

from upsonic_on_prem.utils import storage_2, AI, storage_3, AccessKey, storage_5

from upsonic_on_prem.utils.configs import admin_key

from upsonic_on_prem.utils.github_sync import github

import cloudpickle
import dill

from cryptography.fernet import Fernet
import base64
import hashlib

import textwrap
import time


class Scope:
    def __init__(self, key, specific=False):
        self.key = key
        self.the_storage = storage_2
        self.specific = specific


    def get_last_runs(self, n=10):
        result = []
        for i in self.run_history[-n:]:
            the_run = storage_5.get(i)
            result.append(the_run)

        result.reverse()
        return result
        


    @property
    def run_history(self):
        return self.the_storage.get(self.key + ":run_history") or []

    def add_run_history(self, version=None, os_type=None, os_architecture=None, os_version=None, python_version=None, type=None, cpu_usage=None, memory_usage=None, elapsed_time=None):
        current_time = time.time()
        current = self.run_history

        data = {"version":version, "os_type": os_type, "os_architecture": os_architecture, "os_version": os_version, "python_version": python_version, "type": type, "cpu_usage": cpu_usage, "memory_usage": memory_usage, "elapsed_time": elapsed_time, "time": current_time}

        sha_256 = hashlib.sha256((str(current_time)+str(version)+str(self.key)).encode()).hexdigest()

        the_run = {"data": data, "time": current_time, "scope": self.key}

        storage_5.set(sha_256, the_run)

        current.append(sha_256)

        if len(current) > 100:
            current = current[1:]




        self.the_storage.set(self.key + ":run_history", current)


    def delete(self, user=None):
        if user != None:
            if ":" in self.key:
                path = self.key.split(":")[0].replace(".", "/")
            else:
                path = self.key.replace(".", "/")
            path = f'{path}.py'        

            github.delete_file(scope=self, message=f"Deleted {path} by {user.name}")

        self.the_storage.delete(self.key)
        for i in self.dump_history:
            storage_3.delete(i)
        for i in self.version_history:
            storage_3.delete(i)            
        self.the_storage.delete(self.key + ":dump_history")
        self.the_storage.delete(self.key + ":documentation")
        self.the_storage.delete(self.key + "github_sha")
        self.the_storage.delete(self.key + ":time_complexity")
        self.the_storage.delete(self.key + ":mistakes")
        self.the_storage.delete(self.key + ":required_test_types")
        self.the_storage.delete(self.key + ":tags")
        self.the_storage.delete(self.key + ":security_analysis")
        self.the_storage.delete(self.key + ":code")
        self.the_storage.delete(self.key + ":requirements")
        self.the_storage.delete(self.key + ":version_history")
        self.the_storage.delete(self.key + ":python_version")

    @property
    def dump_history(self):
        the_list = self.the_storage.get(self.key + ":dump_history")
        if the_list != None:
            the_list = sorted(the_list, key=lambda x: storage_3.get(x)["time"], reverse=True)
        else:
            the_list = []
        return the_list

    @property
    def version_history(self):
        return self.the_storage.get(self.key + ":version_history") or []

    def create_version(self, version, user: AccessKey):
        current_time = time.time()
        current = self.version_history

        key = self.key + ":" + str(version)

        data = {"data": self.source, "user": user.key, "time": current_time, "settings": self.settings, "type":self.type, "requirements":self.requirements, "python_version":self.python_version, "tags":self.tags, "code": self.code, "documentation": self.documentation, "github_sha": self.github_sha, "time_complexity":self.time_complexity, "mistakes":self.mistakes, "required_test_types":self.required_test_types, "security_analysis":self.security_analysis}

        storage_3.set(key, data)

        current.append(key)

        self.the_storage.set(self.key + ":version_history", current)

    @staticmethod
    def delete_version(version_id):
        storage_3.delete(version_id)
        the_scope = Scope(version_id.split(":")[0])
        current = the_scope.version_history
        current.remove(version_id)
        the_scope.the_storage.set(the_scope.key + ":version_history", current)


    @staticmethod
    def get_version(version_id):
        the_scope = Scope(version_id, specific=True)
        the_scope.the_storage = storage_3
        return the_scope

    @property
    def documentation(self):
        if not self.specific:
            source = self.the_storage.get(self.key + ":documentation")
        else:

            the_resource = self.the_storage.get(self.key)

            if the_resource != None:
                source = self.the_storage.get(self.key)["documentation"]        
        return source

    @property
    def github_sha(self):
        if not self.specific:
            source = self.the_storage.get(self.key + ":github_sha")
        else:

            the_resource = self.the_storage.get(self.key)

            if the_resource != None:
                source = self.the_storage.get(self.key)["github_sha"]        
        return source

    @property
    def time_complexity(self):
        source = None
        if not self.specific:
            source = self.the_storage.get(self.key + ":time_complexity")
        else:

            the_resource = self.the_storage.get(self.key)

            if the_resource != None:
                source = self.the_storage.get(self.key)["time_complexity"]   
     
        return source        



    @property
    def mistakes(self):
        source = None
        if not self.specific:
            source = self.the_storage.get(self.key + ":mistakes")
        else:

            the_resource = self.the_storage.get(self.key)

            if the_resource != None:
                source = self.the_storage.get(self.key)["mistakes"]   
     
        return source  


    @property
    def required_test_types(self):
        source = None
        if not self.specific:
            source = self.the_storage.get(self.key + ":required_test_types")
        else:

            the_resource = self.the_storage.get(self.key)

            if the_resource != None:
                source = self.the_storage.get(self.key)["required_test_types"]   
     
        return source  



    @property
    def tags(self):
        source = None
        if not self.specific:
            source = self.the_storage.get(self.key + ":tags")
        else:

            the_resource = self.the_storage.get(self.key)

            if the_resource != None:
                source = self.the_storage.get(self.key)["tags"]   
     
        return source  




    @property
    def security_analysis(self):
        source = None
        if not self.specific:
            source = self.the_storage.get(self.key + ":security_analysis")
        else:

            the_resource = self.the_storage.get(self.key)

            if the_resource != None:
                source = self.the_storage.get(self.key)["security_analysis"]   
     
        return source  



    def create_documentation(self):
        document = AI.code_to_documentation(self.code)


        if not self.specific:
            self.the_storage.set(self.key + ":documentation", document)
        else:

            the_resource = self.the_storage.get(self.key)

            the_resource["documentation"] = document
            self.the_storage.set(self.key, the_resource)
     
   


    def set_github_sha(self, sha):


        if not self.specific:
            self.the_storage.set(self.key + ":github_sha", sha)
        else:

            the_resource = self.the_storage.get(self.key)

            the_resource["github_sha"] = sha
            self.the_storage.set(self.key, the_resource)
     
   

        
        


    def create_time_complexity(self):
        document = AI.code_to_time_complexity(self.code)


        if not self.specific:
            self.the_storage.set(self.key + ":time_complexity", document)
        else:

            the_resource = self.the_storage.get(self.key)

            the_resource["time_complexity"] = document
            self.the_storage.set(self.key, the_resource)



    def create_mistakes(self):
        document = AI.code_to_mistakes(self.code)

        if not self.specific:
            self.the_storage.set(self.key + ":mistakes", document)
        else:

            the_resource = self.the_storage.get(self.key)

            the_resource["mistakes"] = document
            self.the_storage.set(self.key, the_resource)




    def create_required_test_types(self):
        document = AI.code_to_required_test_types(self.code)

        if not self.specific:
            self.the_storage.set(self.key + ":required_test_types", document)
        else:

            the_resource = self.the_storage.get(self.key)

            the_resource["required_test_types"] = document
            self.the_storage.set(self.key, the_resource)




    def create_tags(self):
        document = AI.code_to_tags(self.code)

        if not self.specific:
            self.the_storage.set(self.key + ":tags", document)
        else:

            the_resource = self.the_storage.get(self.key)

            the_resource["tags"] = document
            self.the_storage.set(self.key, the_resource)




    def create_security_analysis(self):
        document = AI.code_to_security_analysis(self.code)

        if not self.specific:
            self.the_storage.set(self.key + ":security_analysis", document)
        else:

            the_resource = self.the_storage.get(self.key)

            the_resource["security_analysis"] = document
            self.the_storage.set(self.key, the_resource)



    def create_documentation_old(self):
        document = AI.code_to_documentation(self.code_old)

        if not self.specific:
            self.the_storage.set(self.key + ":documentation", document)
        else:

            the_resource = self.the_storage.get(self.key)

            the_resource["documentation"] = document
            self.the_storage.set(self.key, the_resource)





    @property
    def source(self):
        the_resource = self.the_storage.get(self.key)
        if the_resource is None:
            return None
        return self.the_storage.get(self.key)["data"]


    @property
    def user(self):
        if not self.specific:
            return None
        else:

            the_resource = self.the_storage.get(self.key)

            return the_resource["user"]

    @property
    def type(self):
        return self.the_storage.get(self.key + ":type")

    def set_type(self, type):
        return self.the_storage.set(self.key + ":type", type)

    @property
    def python(self):
        if self.source is None:
            return None
        decrypt = Fernet(base64.urlsafe_b64encode(hashlib.sha256("u".encode()).digest())).decrypt(self.source)
        return cloudpickle.loads(decrypt)

    @property
    def code_old(self):
        the_python = self.python
        if the_python is None:
            return None
        return textwrap.dedent(dill.source.getsource(self.python))


    @property
    def code(self):
        source = None
        if not self.specific:
            source = self.the_storage.get(self.key + ":code")
        else:

            the_resource = self.the_storage.get(self.key)

            if the_resource != None:
                source = self.the_storage.get(self.key)["code"]   
     
        return source

    def set_code(self, code):
        return self.the_storage.set(self.key + ":code", code)

    @property
    def requirements(self):
        source = None
        if not self.specific:
            source = self.the_storage.get(self.key + ":requirements")
        else:

            the_resource = self.the_storage.get(self.key)

            if the_resource != None:
                source = self.the_storage.get(self.key)["requirements"]   
     
        return source        
        

    def set_requirements(self, requirements):
        return self.the_storage.set(self.key + ":requirements", requirements)


    @property
    def settings(self):
        source = None
        if not self.specific:
            source = self.the_storage.get(self.key + ":settings")
        else:

            the_resource = self.the_storage.get(self.key)

            if the_resource != None:
                source = self.the_storage.get(self.key)["settings"]   
     
        return source              

    def set_settings(self, settings):
        return self.the_storage.set(self.key + ":settings", settings)



    @property
    def python_version(self):
        source = None
        if not self.specific:
            source = self.the_storage.get(self.key + ":python_version")
        else:

            the_resource = self.the_storage.get(self.key)

            if the_resource != None:
                source = self.the_storage.get(self.key)["python_version"]   
     
        return source        
                


    def set_python_version(self, python_version):
        return self.the_storage.set(self.key + ":python_version", python_version)


    def dump(self, data, user: AccessKey, pass_str=False):
        if not pass_str:
            data = data.decode()
        current_time = time.time()
        the_time = str(current_time) + "_" + str(random.randint(0, 100000))
        sha256 = hashlib.sha256(the_time.encode()).hexdigest()
        key = self.key + ":" + sha256

        data = {"data": data, "user": user.key, "time": current_time, "settings":self.settings, "type":self.type, "requirements":self.requirements, "python_version":self.python_version, "tags":self.tags, "code": self.code, "documentation": self.documentation, "github_sha": self.github_sha, "time_complexity":self.time_complexity, "mistakes":self.mistakes, "required_test_types":self.required_test_types, "security_analysis":self.security_analysis}

        storage_3.set(key, data)

        current = self.dump_history
        current.append(key)
        self.the_storage.set(self.key + ":dump_history", current)

        self.the_storage.set(self.key, data)


        if ":" in self.key:
            path = self.key.split(":")[0].replace(".", "/")
        else:
            path = self.key.replace(".", "/")
        path = f'{path}.py'     

        github_sha = github.create_or_update_file(scope=self, message=f"New changes for {path} by {user.name}")
        if github_sha != False:
            self.set_github_sha(github_sha)
    

    def is_it_github_synced(self):
        print("test")
        print(self.specific)
        print(self.github_sha)
        print(github.get_sha(self))
        return self.github_sha == github.get_sha(self)


    @staticmethod
    def get_dump(dump_id):
        the_scope = Scope(dump_id, specific=True)
        the_scope.the_storage = storage_3
        return the_scope

    @staticmethod
    def get_all_scopes():
        keys = storage_2.keys()
        scopes = []
        for i in keys:
            if not ":" in i and i != "":
                scopes.append(i)

        scopes.sort()
        return scopes

    @staticmethod
    def get_all_scopes_name(user: AccessKey):
        all_scopes = Scope.get_all_scopes()

        custom_scopes_read = user.scopes_read
        result = []

        for i in all_scopes:
            if user.can_access_read(i, custom_scopes_read=custom_scopes_read) or user.is_admin:
                result.append(i)

        return result

    @staticmethod
    def get_all_scopes_name_prefix(user, prefix):
        prefix = prefix + "."
        all_scopes = Scope.get_all_scopes_name(user)
        result = []
        for i in all_scopes:
            if i.startswith(prefix):
                result.append(i)
        return result





    @staticmethod
    def get_all_scopes_with_documentation():
        all_scopes = Scope.get_all_scopes()

        result = []
        for i in all_scopes:
            the_scope = Scope(i)
            element = {"name": i, "documentation": str(the_scope.documentation) + " " + str(the_scope.tags)}
            result.append(element)

        return result
