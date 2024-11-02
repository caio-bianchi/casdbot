from enum import Enum

class FormatType(Enum):
    TEXT = 1
    JSON = 2
    HTML = 3
    URL_ENCONDING = 4


class FileType(Enum):
    PDF = 1
    PNG = 2
    JPG = 3
    JPEG = 4

class ContactInfo:
    def __init__(self, name: str, phone_number: str, email: str) -> None:
        self.name = name
        self.phone_number = phone_number
        self.email = email
    def format_phone_number() -> str:
        pass

class TextMessage:
    def __init__(self, content: str, format: FormatType) -> None:
        self.content = content
        self.format = FormatType
    def format_message() -> str:
        pass

    def format_template() -> str:
        pass

class FileMessage:
    def __init__(self, path: str, type: FileType) -> None:
        self.path = path
        self.type = type

class MessageInfo:
    def __init__(self, text: TextMessage, files: FileMessage, contact: ContactInfo) -> None:
        self.text = text
        self.files = files
        self.contact = contact


