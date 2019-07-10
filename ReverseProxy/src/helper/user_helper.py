import json

import peewee
import requests
from bottle import response, request
from peewee import JOIN
from threading import Lock

from src.model.school import School
from src.model.application import Application
from src.model.application_permissions import ApplicationPermission
from src.helper import response_format_helper
from src.model.users import Users
from src.helper import router

response_format_helper = response_format_helper.Factory().get_response_format_helper()
assert router.factory.get_router() is router.factory.get_router()
router = router.factory.get_router()

class UserHelper:
    def __init__(self):
        pass

    def user_info(self, user_id):
        try:
            join_condition = Users.school_id == School.school_id
            query = Users.select(Users, School.school_name).join(School, JOIN.INNER, on=join_condition).where(
                Users.user_id == user_id).dicts()
            response.body = json.dumps({'user': list(query)}, default=response_format_helper.to_serializable)
            response.status = 200
        except Exception as e:
            print(e)
            response.body = "Error: User does not exist"
            response.status = 400
        return response

    def student_list(self, school_id):
        query = Users.select(Users.user_id, Users.first_name, Users.last_name).where(
            Users.user_type == "Student" and Users.school_id == school_id).dicts()
        response.body = json.dumps({'students': list(query)})
        response.status = 200
        return response

    def application_list(self):
        query = Application.select().dicts()
        response.body = json.dumps({'applications': list(query)})
        response.status = 200
        return response

    def permitted_apps(self, user_id):
        join_condition = ApplicationPermission.application_id == Application.application_id
        query = ApplicationPermission.select(Application.application_id, Application.application_name).join(Application,
                                                                                                            JOIN.INNER,
                                                                                                            on=join_condition).where(
            ApplicationPermission.user_id == user_id).dicts()
        response.body = json.dumps({'applications': list(query)})
        response.status = 200
        return response

    def give_access(self, user_id, application_id):
        try:
            # If this query doesn't return empty, than this permission is already in the DB
            query = ApplicationPermission.get(
                ApplicationPermission.user_id == user_id and ApplicationPermission.application_id == application_id)
            response.body = json.dumps({'error': 'This permission already exists, or invalid username'})
            response.status = 400

        except peewee.DoesNotExist:
            try:
                perm = ApplicationPermission()
                perm.user_id = user_id
                perm.application_id = application_id
                perm.save()
                os_container_ip = router.get_session_for_user(user_id).destination_ip
                self.add_application_permission_in_container(os_container_ip, application_id)
                response.body = json.dumps({'applications': 'Successfully granted permission'})
                response.status = 200
            except Exception as e:
                print(e)
                response.body = json.dumps({'error': 'Invalid application_id'})
                response.status = 400
        return response

    def revoke_access(self, user_id, application_id):
        try:
            perm = ApplicationPermission.get(
                ApplicationPermission.user_id == user_id and ApplicationPermission.application_id == application_id)
            perm.delete_instance(recursive=True)
            os_container_ip = router.get_session_for_user(user_id).destination_ip
            self.revoke_application_permission_in_container(os_container_ip, application_id)
            response.body = json.dumps({'applications': 'Successfully deleted permission'})
            response.status = 200
        except Exception as e:
            print(e)
            response.body = json.dumps({'error': 'user_id or application_id does not exist'})
            response.status = 400

        return response

    def add_application_permission_in_container(self, os_container_ip, application_id):
        url = 'http://{0}:9090/application/permission/add/{1}'.format(os_container_ip, application_id)
        print(url)
        response = requests.post(url)

    def revoke_application_permission_in_container(self, os_container_ip, application_id):
        url = 'http://{0}:9090/application/permission/remove/{1}'.format(os_container_ip, application_id)
        print(url)
        response = requests.post(url)


class Factory:
    user_helper = None
    lock = Lock()

    def get_user_helper(self):
        with self.lock:
            if self.user_helper is not None:
                return self.user_helper
            else:
                self.user_helper = UserHelper()
                return self.user_helper

    def reset_helper(self):
        with self.lock:
            self.user_helper = UserHelper()
