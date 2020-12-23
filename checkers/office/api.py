import requests

from google.protobuf.json_format import MessageToJson, Parse
import proto.office_pb2 as pb
from errs import INVALID_FORMAT_ERR, FAILED_TO_CONNECT


class Api:
    def __init__(self, host: str):
        self.host = host
        self.url = f"http://{self.host}"
        self.session = requests.Session()

    def create_doc(self, req: pb.CreateDocumentRequest) -> (pb.CreateDocumentResponse, str):
        try:
            d = MessageToJson(req)
            r = self.session.post(f"{self.url}/docs/create", data=d)
        except Exception as e:
            print(e)
            return None, FAILED_TO_CONNECT
        try:
            return Parse(r.text, pb.CreateDocumentResponse()), None
        except Exception as e:
            print(e)
            return None, INVALID_FORMAT_ERR

    def list_doc(self, req: pb.ListDocumentsRequest) -> (pb.ListDocumentsResponse, str):
        try:
            d = MessageToJson(req)
            r = self.session.post(f"{self.url}/docs/list", data=d)
        except Exception as e:
            print(e)
            return None, FAILED_TO_CONNECT
        try:
            return Parse(r.text, pb.ListDocumentsResponse()), None
        except Exception as e:
            print(e)
            return None, INVALID_FORMAT_ERR

    def execute_doc(self, req: pb.ExecuteRequest) -> (pb.ExecuteResponse, str):
        try:
            d = MessageToJson(req)
            r = self.session.post(f"{self.url}/docs/execute", data=d)
        except Exception as e:
            print(e)
            return None, FAILED_TO_CONNECT
        try:
            return Parse(r.text, pb.ExecuteResponse()), None
        except Exception as e:
            print(e)
            return None, INVALID_FORMAT_ERR

    def login(self, req: pb.LoginRequest) -> (pb.LoginResponse, str):
        try:
            d = MessageToJson(req)
            r = self.session.post(f"{self.url}/users/login", data=d)
        except Exception as e:
            print(e)
            return None, FAILED_TO_CONNECT
        try:
            return Parse(r.text, pb.LoginResponse()), None
        except Exception as e:
            print(e)
            return None, INVALID_FORMAT_ERR

    def register(self, req: pb.RegisterRequest) -> (pb.RegisterResponse, str):
        try:
            d = MessageToJson(req)
            r = self.session.post(f"{self.url}/users/register", data=d)
        except Exception as e:
            print(e)
            return None, FAILED_TO_CONNECT
        try:
            return Parse(r.text, pb.RegisterResponse()), None
        except Exception as e:
            print(e)
            return None, INVALID_FORMAT_ERR

    def list_users(self, req: pb.ListRequest) -> (pb.ListResponse, str):
        try:
            d = MessageToJson(req)
            r = self.session.post(f"{self.url}/users/list", data=d)
        except Exception as e:
            print(e)
            return None, FAILED_TO_CONNECT
        try:
            return Parse(r.text, pb.ListResponse()), None
        except Exception as e:
            print(e)
            return None, INVALID_FORMAT_ERR
