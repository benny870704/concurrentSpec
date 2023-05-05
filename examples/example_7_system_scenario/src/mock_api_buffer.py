from exploratoryTool.src.connection_domain import ConnectionDomain

class MockAPIBuffer(ConnectionDomain):

    def __init__(self) -> None:
        self.requests = []
        self.request_index = 0

    def add_request(self, request):
        self.requests.append(request)

    def pop_request(self):
        if len(self.requests) > self.request_index:
            self.request_index += 1
            return self.requests[self.request_index - 1]

    def get_all_requests(self):
        return self.requests
