from enum import StrEnum


class SupportedDocumentFileExtensions(StrEnum):
    PDF = "pdf"
    DOCX = "docx"
    DOC = "doc"
    GIF = "gif"
    JPG = "jpg"
    JPEG = "jpeg"
    PNG = "png"
    PPT = "ppt"
    PPTX = "pptx"
    RTF = "rtf"
    TXT = "txt"
    XLS = "xls"
    XLSX = "xlsx"

    @staticmethod
    def list():
        return list(SupportedDocumentFileExtensions.__members__.values())
