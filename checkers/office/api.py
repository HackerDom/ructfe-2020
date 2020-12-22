import requests

from google.protobuf.json_format import MessageToJson, Parse
import proto.office_pb2 as pb


class Api:
    def __init__(self, host: str):
        self.host = host
        self.url = f"http://{self.host}"
        self.session = requests.Session()

    def create_doc(self, req: pb.CreateDocumentRequest) -> (pb.CreateDocumentResponse, str):
        try:
            d = MessageToJson(req)
            r = self.session.post(f"{self.url}/docs/create", data=d)
            resp = pb.CreateDocumentResponse()
            return Parse(r.text, resp), None
        except Exception as e:
            return None, str(e)

    def list_doc(self, req: pb.ListDocumentsRequest) -> (pb.ListDocumentsResponse, str):
        try:
            d = MessageToJson(req)
            r = self.session.post(f"{self.url}/docs/list", data=d)
            return Parse(r.text, pb.ListDocumentsResponse()), None
        except Exception as e:
            return None, str(e)

    def execute_doc(self, req: pb.ExecuteRequest) -> (pb.ExecuteResponse, str):
        try:
            d = MessageToJson(req)
            r = self.session.post(f"{self.url}/docs/execute", data=d)
            resp = pb.ExecuteResponse()
            return Parse(r.text, resp), None
        except Exception as e:
            return None, str(e)

    def login(self, req: pb.LoginRequest) -> (pb.LoginResponse, str):
        try:
            d = MessageToJson(req)
            r = self.session.post(f"{self.url}/users/login", data=d)
            resp = pb.LoginResponse()
            return Parse(r.text, resp), None
        except Exception as e:
            return None, str(e)

    def register(self, req: pb.RegisterRequest) -> (pb.RegisterResponse, str):
        try:
            d = MessageToJson(req)
            r = self.session.post(f"{self.url}/users/register", data=d)
            resp = pb.RegisterResponse()
            return Parse(r.text, resp), None
        except Exception as e:
            return None, str(e)

    def list_users(self, req: pb.ListRequest) -> (pb.ListResponse, str):
        try:
            d = MessageToJson(req)
            r = self.session.post(f"{self.url}/users/list", data=d)
            resp = pb.ListResponse()
            return Parse(r.text, resp), None
        except Exception as e:
            return None, str(e)
