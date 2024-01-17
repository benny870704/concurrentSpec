import unittest
import traceback

class SilentTestResult(unittest.TestResult):
    def addError(self, test, err):
        pass

    def addFailure(self, test, err):
        pass

    def addSuccess(self, test):
        pass

    def startTest(self, test):
        pass

    def stopTest(self, test):
        pass
    
class ShortTracebackResult(unittest.TextTestResult):
    def addError(self, test, err):
        exc_type, exc_value, tb = err
        traceback_message = traceback.format_exception(exc_type, exc_value, tb)
        
        # Omit the first line of the traceback
        for index, line in enumerate(traceback_message):
            if "RuntimeError:" in line:
                traceback_message = traceback_message[index:]
                break
        
        # Convert the list of strings back to a single string
        traceback_str = ''.join(traceback_message)
        # Add the failure to the list of failures with the modified traceback
        self.errors.append((test, traceback_str))

        raise err[1]
    
    def addFailure(self, test, err):
        exc_type, exc_value, tb = err
        self.failures.append((test, self._exc_info_to_string(err, test)))
