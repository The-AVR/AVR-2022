from enum import Enum, auto


class ConnectionState(Enum):
    connecting = auto()
    connected = auto()
    disconnecting = auto()
    disconnected = auto()
    failure = auto()
