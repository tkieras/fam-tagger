from pprint import pprint


class Logger():
    def __init__(self):
        pass

    def log(self, entry):
        pprint(entry)

    def warning(self, msg, obj=None):
        entry = {"type" : "WARNING",
                "message" : msg,
                "object" : obj}
        self.log(entry)

    def error(self, msg, obj=None):
        entry = {"type" : "ERROR",
                "message" : msg,
                "object" : obj}
        self.log(entry)
        raise RuntimeError(msg)

    def report(self, msg, obj=None):
        entry = {"type" : "REPORT",
                "message" : msg,
                "object": obj}
        self.log(entry)
