import logging
import logging.handlers

# import src.ansi_color_fix
import os
# os.system('')

class Logger:
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    consoleLogLevel = DEBUG
    fileLogLevel = DEBUG

    # loggerPath = "log"
    loggerPath = os.path.abspath("log")
    existedLoggers = {}

    @classmethod
    def init(cls, name):
        cls.logger = logging.getLogger(name)
        cls.logger.setLevel(cls.DEBUG)
        # fileHandler = logging.FileHandler("cone.log")
        if not os.path.exists(cls.loggerPath):
            os.makedirs(cls.loggerPath)
        fileHandler = logging.handlers.TimedRotatingFileHandler(cls.loggerPath + "\\cone.log", when = "midnight", delay = True)

        fileHandler.setLevel(cls.fileLogLevel)

        consoleHandler = logging.StreamHandler()
        # consoleHandler.setLevel(logging.WARNING)
        consoleHandler.setLevel(cls.consoleLogLevel)

        # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fileFormatter = logging.Formatter('[%(levelname)s] %(asctime)s | %(name)s:%(lineno)d | %(message)s')
        
        fileHandler.setFormatter(fileFormatter)
        
        consoleFormatter = logging.Formatter("%(message)s")
        consoleHandler.setFormatter(consoleFormatter)

        cls.logger.addHandler(fileHandler)
        cls.logger.addHandler(consoleHandler)

    @classmethod
    def getLogger(cls, name):
        if name in cls.existedLoggers:
            return cls.existedLoggers[name]
        else:
            cls.init(name)
            cls.existedLoggers[name] = cls.logger
            return cls.existedLoggers[name]


if __name__ == "__main__":
    logger = Logger.getLogger(__name__)
    logger.debug("\033[1;36m" + "[ STATE ]" + "\033[0m")
    logger.debug("\x1b[6;30;42m" + 'Success!' + "\x1b[0m")

    logger.info("\033[0m"    + "[ NORMAL  ]")
    logger.info("\033[1;30m" + "[ BLACK   ]")
    logger.info("\033[1;31m" + "[ RED     ]")
    logger.info("\033[1;32m" + "[ GREEN   ]")
    logger.info("\033[1;33m" + "[ YELLOW  ]")
    logger.info("\033[1;34m" + "[ BLUE    ]")
    logger.info("\033[1;35m" + "[ MAGENTA ]")
    logger.info("\033[1;36m" + "[ CYAN    ]")
    logger.info("\033[1;37m" + "[ WHITE   ]")
    logger.info("\033[1m"    + "[ BOLD    ]")
