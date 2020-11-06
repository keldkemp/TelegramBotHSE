import logging


class Logging:

    def input_log(self, error):
        logging.basicConfig(filename='ErrorLog.log', level=logging.ERROR)
        logging.error(error)
