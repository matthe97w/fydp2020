from time import sleep

from src.helper import router
from src.helper import container_helper
from src.helper import authentication_helper
from src.helper import user_helper
from src.wsgi import app
from bottle import response, request
from bottle import post, get, put, delete
from src.model import base_model

import json


router = router.factory.get_router()
authentication_helper = authentication_helper.Factory().get_authentication_helper()
user_helper = user_helper.Factory().get_user_helper()
container_helper = container_helper.ContainerHelper()
db = base_model.db
broadcast = None
message = None

# A test call to determine if the API is working
@get('/test')
def test_call():
    return [b"This is a test call"]


# A test call to determine if the API is working
@get('/')
def listing_handler():
    return [b"Hello"]


# Setup routes for the user.
# client_ip: Should be the public ipv4 of the client
# os_type: Should be either 'Windows' or 'Linux'
# user_id: The unique identifier for the user
# width: Screen width
# height: Screen height
@get('/routes/setup/<user_id>/<client_ip>/<os_type>/<width>/<height>')
@app.auth.verify_request(scopes=['studentTeacherStreamingOS'])
def setup_routes(user_id, client_ip, os_type, width, height):
    return router.setup_routes(user_id, client_ip, os_type, width, height)


# Deletes routes for user
# user_id: The unique identifier for the user
@get('/routes/delete/<user_id>')
@app.auth.verify_request(scopes=['studentTeacherStreamingOS'])
def delete_routes(user_id):
    container_helper.cleanup_user_session(user_id)
    response.body = router.delete_iptable_rules(user_id)
    response.status = 200
    return response


# Create user, returns user_id
# username: The unique username for the user
# password: The unique password for the user
@put('/user/<username>/create/<password>')
def create_user(username, password):
    return authentication_helper.create_new_user(username, password, request.params)


# Delete user
# user_id: The unique identifier for the user
@delete('/user/<user_id>/delete')
@app.auth.verify_request(scopes=['teacherStreamingOS'])
def delete_user(user_id):
    return authentication_helper.delete_user(user_id)


# Get info about a user
# user_id: The unique identifier for the user
@get('/user/<user_id>/screen/snapshot')
#@app.auth.verify_request(scopes=['teacherStreamingOS'])
def get_screen_snapshot(user_id):
    buffer_image = container_helper.get_screenshot(user_id)
    response.set_header('Content-type', 'image/jpeg')
    return buffer_image.read()


# Broadcast teacher session
# user_id: User ID of the teacher broadcasting
@put('/broadcast/<user_id>')
@app.auth.verify_request(scopes=['teacherStreamingOS'])
def broadcast_session(user_id):
    global broadcast
    # Disable health check cleanup
    router.health_check(enable=False)
    container_helper.health_check(enable=False)
    broadcast = dict()
    broadcast["broadcast_id"] = user_id
    response.status = 200


# Stop broadcast of the teacher session
@put('/broadcast/stop')
@app.auth.verify_request(scopes=['teacherStreamingOS'])
def stop_broadcast_session():
    global broadcast
    broadcast = None
    router.health_check(enable=True)
    container_helper.health_check(enable=True)
    response.status = 200


# Notify students with a message
@put('/broadcast/message/<data>')
@app.auth.verify_request(scopes=['teacherStreamingOS'])
def message_clients(data):
    global message
    message = data
    # TODO Add code to verify send to all connected clients
    response.status = 200


# Subscribe to Broadcast Event Stream
@get('/subscribe')
@app.auth.verify_request(scopes=['studentTeacherStreamingOS'])
def subscribe():
    global broadcast
    response.content_type  = 'text/event-stream'
    response.cache_control = 'no-cache'

    # Set client-side auto-reconnect timeout, ms.
    yield 'retry: 100\n\n'

    event_broadcast = {"eventType": "Broadcast", "broadcast_id": None}
    event_message = {"eventType": "Message", "data": None}

    # Keep client subscribed indefinitely
    while True:
        events_values = list()
        events_json = dict()

        # Add broadcast information
        if broadcast is not None:
            event_broadcast["broadcast_id"] = broadcast["broadcast_id"]
            events_values.append(event_broadcast)

        # Add messages
        if message is not None:
            event_message["data"] = message
            events_values.append(event_message)

        # Send events to subscribed clients
        events_json["events"] = events_values
        yield "data: {}\n\n".format(json.dumps(events_json))


# Setup routes for the user.
# client_ip: Should be the public ipv4 of the client
# os_type: Should be either 'Windows' or 'Linux'
# user_id: The unique identifier for the user
@get('/setup/stream/<user_id>/<client_ip>/<broadcast_id>')
@app.auth.verify_request(scopes=['studentTeacherStreamingOS'])
def setup_stream(user_id, client_ip, broadcast_id):
    return router.setup_stream_routes(user_id, client_ip, str(broadcast_id))


# Stop broadcast streaming and restore user session stream
@get('/restore/stream/<user_id>/<client_ip>/<source_port>/<broadcast_id>')
@app.auth.verify_request(scopes=['studentTeacherStreamingOS'])
def restore_stream(user_id, client_ip, source_port, broadcast_id):
    # cleanup broadcast routes
    router.delete_stream_routes(client_ip, source_port, broadcast_id)
    
    current_session = router.get_session(user_id)
    # Check if a current session exists
    if current_session is not None:
        # All user data should exist in session helper
        response.body = json.dumps({'routes': current_session})
        response.status = 200 
    else:
        response.status = 204


# Get info about a user
# username: The unique username for the user
@get('/user/<username>/info')
@app.auth.verify_request(scopes=['studentTeacherStreamingOS'])
def user_info(username):
    return user_helper.user_info(username)


# Get a list of all the students in the school specified
# school_id: The unique identifier for the school
@get('/school/<school_id>/studentlist')
@app.auth.verify_request(scopes=['teacherStreamingOS'])
def student_list(school_id):
    return user_helper.student_list(school_id)


# Get a list of all applications supported
@get('/applications')
@app.auth.verify_request(scopes=['teacherStreamingOS'])
def application_list():
    return user_helper.application_list()

# Get a list of all users that have an active session
# Note that every time the ReverseProxy container is built,
# the sessions must be recreated/freed in the DB and then the
# setup_routes endpoint must be called to add the user to the
# session. Then the call will work :)
@get('/sessions')
@app.auth.verify_request(scopes=['teacherStreamingOS'])
def session_list():
    response.body = user_helper.session_list()
    response.status = 200
    return response


# Get the list of permitted applications for a student
# user_id: The unique identifier for the user
@get('/user/<user_id>/applications')
@app.auth.verify_request(scopes=['teacherStreamingOS'])
def permitted_apps(user_id):
    return user_helper.permitted_apps(user_id)


# Give access to a user for an application
# user_id: The unique identifier for the user
# application_id: The unique identifier for the application
@put('/user/<user_id>/grant/<application_id>')
@app.auth.verify_request(scopes=['teacherStreamingOS'])
def give_access(user_id, application_id):
    return user_helper.give_access(user_id, application_id)


# Revoke access to a user for an application
# user_id: The unique identifier for the user
# application_id: The unique identifier for the application
@delete('/user/<user_id>/revoke/<application_id>')
@app.auth.verify_request(scopes=['teacherStreamingOS'])
def revoke_access(user_id, application_id):
    return user_helper.revoke_access(user_id, application_id)


# Generates an OAuth2.0 token for the user
# This requires a few fields in the body set as x-www-form-urlencoded. Also requires the following Content-Type header: application/x-www-form-urlencoded
# client_id: The client type (i.e. teacher or student)
# grant_type: The grant type. Only one supported right now which is 'password'
# username: The unique username for the user
# password: The password for the user
# scope: Scopes define what you are requesting access to with the token (i.e. teacherStreamingOS, studentStreamingOS, studentAndTeacherStreamingOS)
@post('/token')
@app.auth.create_token_response()
def generate_token():
    pass


# Test call for authenticating
# username: The unique username for the user
# password: The password for the user
@get('/user/<username>/auth/<password>')
def auth_user(username, password):
    if authentication_helper.validate_user(username, password):
        response.body = "Yay we're authenticated"
        response.status = 200
    else:
        response.body = "OoPs SoMeThInG wEnT wRoNg"
        response.status = 418
    return response

# Get a list of all the students in the school specified
# school_id: The unique identifier for the school
@get('/availableVM')
def available_vm_list():
    return container_helper.available_vm_list()
