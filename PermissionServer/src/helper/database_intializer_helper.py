from src.model.base_model import BaseModel
from src.model.application import Application
from src.model.application_permissions import ApplicationPermission
from src.model.device import Device
from src.model.os_container import OSContainer
from src.model.session_info_table import SessionInfo
from src.model.student import Student
from src.model.teacher import Teacher
from src.model.user_type import UserType
from src.model.users import Users
import peewee

db = peewee.MySQLDatabase(
    "streamingOS",
    host="db",
    port=3306,
    user="root",
    passwd="supersecret"
)


class DatabaseInitializer:
    def __init__(self):
        try:
            UserType.create_table()
            Application.create_table()
            Users.create_table()
            ApplicationPermission.create_table()
            Device.create_table()
            OSContainer.create_table()
            SessionInfo.create_table()
            Student.create_table()
            Teacher.create_table()
        except peewee.InternalError as e:
            print(str(e))
