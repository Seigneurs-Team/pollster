from dataclasses import dataclass


@dataclass
class Levels:
    Debug: str = 'debug'
    Info: str = 'info'
    Warning: str = 'warning'
    Error: str = 'error'
    Critical: str = 'critical'