from enum import Enum

class GenericErrorCodes(tuple,Enum):
    BAD_REQUEST = (400,"Bad Request")
    NOT_AUTHORIZED = (401,"Not Authorized")
    NOT_FOUND = (404,"Not found")
    NOT_ACCEPTABLE = (406,"Not acceptable")
    VALIDATION = (471,"Validation error")
    INTERNAL_SERVER_ERROR = (500,"Internal Server Error")

error_codes = {}
for e in [GenericErrorCodes]:
    for field in e:
        error_codes[field[0]] = field