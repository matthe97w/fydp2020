class SessionInfo:

    def __init__(self, container_id, client_ip, source_port, destination_ip, destination_port):
        self.container_id = container_id
        self.client_ip = client_ip
        self.source_port = source_port
        self.destination_ip = destination_ip
        self.destination_port = destination_port