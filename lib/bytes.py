import base64
import json

class Bytes:
    @staticmethod
    def str_to_bytes(string: str):
        """
        converts string data to bytes
        @returns: string bytes
        """
        return string.encode("utf-8")

    @staticmethod
    def object_to_bytes(obj: object):
        """
        coverts object to bytes
        @returns: object bytes
        """
        return json.dumps(obj).encode('utf-8')
