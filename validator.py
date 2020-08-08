from .yesbank_parser import YesBankParser
from .parser import Parser

class Validator:
    def __init__(self):
        self.__map = dict()
        self.__map['yesbank.in'] = YesBankParser

    def get_parser_obj(self, key: str):
        if key in self.__map:
            return self.__map[key]
        else:
            return Parser