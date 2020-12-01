import logging

class GenericReader():
    def __init__(self, name):
        self.name = name
        self.values = self.offset = self.scale = self.missing = None
        self.filenames = {}

    def show_info(self, internal_key, variable):
        try:
            logging.debug(internal_key + ' dimensions: ' + str(variable.dimensions) + ' size=' + str(variable.size))
        except:
            pass
