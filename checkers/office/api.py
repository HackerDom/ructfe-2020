import requests

from google.protobuf.json_format import MessageToJson
import proto.office_pb2 as pb


class Api:
    def __init__(self, host: str):
        self.host = host
        self.url = f"http://{self.host}"
        self.session = requests.Session()

    def create_doc(self, req: pb.CreateDocumentRequest) -> requests.Response:
        d = MessageToJson(req)
        r = self.session.post(f"{self.url}/docs/create", data=d)
        return r

    def list_doc(self, req: pb.ListDocumentsRequest) -> requests.Response:
        d = MessageToJson(req)
        r = self.session.post(f"{self.url}/docs/list", data=d)
        return r

    def execute_doc(self, req: pb.ExecuteRequest) -> requests.Response:
        d = MessageToJson(req)
        r = self.session.post(f"{self.url}/docs/execute", data=d)
        return r
