from enum import Enum

class ExecuteState(str, Enum):
    EXECUTED = 'executed'
    ERROR = 'error'
    SKIP = 'skip'
    NOT_EXECUTED = 'not_executed'