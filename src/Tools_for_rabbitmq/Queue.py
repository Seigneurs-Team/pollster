from dataclasses import dataclass


@dataclass
class Queue:
    poll_queue: str = 'poll_queue'
    poll_queue_callback: str = 'poll_queue_callback'
    ping_queue: str = 'ping_queue'