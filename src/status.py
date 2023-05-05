from enum import Enum

class Status(Enum):
    """
    * untested: Initial state before executing.
    * passed: A scenario/scenario outline/background was executed and passed.
    * failed: Failures occurs during executing steps or setup.
    * undefined: No step definition implemented.
    """
    untested = 0
    passed = 1
    failed = 2
    undefined = 3

    def __eq__(self, other_status) -> bool:
        if isinstance(other_status, str):
            return self.name == other_status
        return super(Status, self).__eq__(other_status)
    