## Student Name: Joshua Keppo
## Student ID: 21091752

"""
Task B: Event Registration with Waitlist (Stub)
In this lab, you will design and implement an Event Registration with Waitlist system using an LLM assistant as your primary programming collaborator. 
You are asked to implement a Python module that manages registration for a single event with a fixed capacity. 
The system must:
•	Accept a fixed capacity.
•	Register users until capacity is reached.
•	Place additional users into a FIFO waitlist.
•	Automatically promote the earliest waitlisted user when a registered user cancels.
•	Prevent duplicate registrations.
•	Allow users to query their current status.

The system must ensure that:
•	The number of registered users never exceeds capacity.
•	Waitlist ordering preserves FIFO behavior.
•	Promotions occur deterministically under identical operation sequences.

The module must preserve the following invariants:
•	A user may not appear more than once in the system.
•	A user may not simultaneously exist in multiple states.
•	The system state must remain consistent after every operation.

The system must correctly handle non-trivial scenarios such as:
•	Multiple cancellations in sequence.
•	Users attempting to re-register after canceling.
•	Waitlisted users canceling before promotion.
•	Capacity equal to zero.
•	Simultaneous or rapid consecutive operations.
•	Queries during state transitions.

The output consists of the updated registration state and ordered lists of registered and waitlisted users after each operation.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict
import time
import re


class DuplicateRequest(Exception):
    """Raised if a user tries to register but is already registered or waitlisted."""
    pass


class NotFound(Exception):
    """Raised if a user cannot be found for cancellation."""
    pass


@dataclass(frozen=True)
class UserStatus:
    """
    state:
      - "registered"
      - "waitlisted"
      - "none"
    position: 1-based waitlist position if waitlisted; otherwise None
    """
    state: str
    position: Optional[int] = None


class EventRegistration:
    """
    Event registration system with deterministic ordering, waitlist management, 
    accessible notifications, and configurable notification throttling.
    """

    USER_ID_PATTERN = re.compile(r"^[A-Za-z0-9]{1,12}$")

    def __init__(self, capacity: int, notification_window: int = 600) -> None:
        """
        Args:
            capacity: Maximum number of registered users (>= 0)
            notification_window: Minimum seconds between notifications per user
        """
        if capacity < 0:
            raise ValueError("Capacity must be non-negative")

        self.capacity = capacity
        self._registered: List[str] = []
        self._waitlist: List[str] = []
        self._users: set[str] = set()
        self._last_notification: Dict[str, float] = {}
        self.notification_window = notification_window
        self.messages: List[str] = []  # Stores accessible messages for each action

    def _validate_user_id(self, user_id: str) -> None:
        if not isinstance(user_id, str):
            raise ValueError("user_id must be a string")
        if not self.USER_ID_PATTERN.fullmatch(user_id):
            raise ValueError("Invalid user_id")

    def _can_notify(self, user_id: str) -> bool:
        """Check if enough time passed to send notification."""
        now = time.time()
        last = self._last_notification.get(user_id, 0)
        if now - last >= self.notification_window:
            self._last_notification[user_id] = now
            return True
        return False

    def _notify(self, user_id: str, message: str) -> None:
        """Record an accessible message if notification allowed."""
        if self._can_notify(user_id):
            full_message = f"User {user_id}: {message}"
            self.messages.append(full_message)

    def _promote(self) -> None:
        """Promote earliest waitlisted user until capacity is filled."""
        while len(self._registered) < self.capacity and self._waitlist:
            user = self._waitlist.pop(0)
            self._registered.append(user)
            self._notify(user, "Promoted from waitlist to registered")

    def register(self, user_id: str) -> UserStatus:
        """Register a user or place them on waitlist if full."""
        self._validate_user_id(user_id)

        if user_id in self._users:
            raise DuplicateRequest("User already registered or waitlisted")

        self._users.add(user_id)

        # Deterministic registration
        if len(self._registered) < self.capacity:
            self._registered.append(user_id)
            self._notify(user_id, "Successfully registered for the event")
            return UserStatus("registered")

        self._waitlist.append(user_id)
        self._notify(user_id, f"Added to waitlist at position {len(self._waitlist)}")
        return UserStatus("waitlisted", len(self._waitlist))

    def cancel(self, user_id: str) -> None:
        """Cancel a registration or waitlist entry, promoting waitlisted users if needed."""
        self._validate_user_id(user_id)

        if user_id in self._registered:
            self._registered.remove(user_id)
            self._users.remove(user_id)
            self._notify(user_id, "Cancelled registration successfully")
            self._promote()
            return

        if user_id in self._waitlist:
            pos = self._waitlist.index(user_id) + 1
            self._waitlist.remove(user_id)
            self._users.remove(user_id)
            self._notify(user_id, f"Cancelled waitlist position {pos}")
            return

        raise NotFound("User not found")

    def status(self, user_id: str) -> UserStatus:
        """Return user's current status."""
        self._validate_user_id(user_id)

        if user_id in self._registered:
            return UserStatus("registered")
        if user_id in self._waitlist:
            pos = self._waitlist.index(user_id) + 1
            return UserStatus("waitlisted", pos)
        return UserStatus("none")

    def get_registered(self) -> List[str]:
        """Return a copy of registered users."""
        return list(self._registered)

    def get_waitlist(self) -> List[str]:
        """Return a copy of waitlisted users."""
        return list(self._waitlist)

    def set_capacity(self, new_capacity: int) -> None:
        """Update event capacity and promote waitlisted users if possible."""
        if new_capacity < 0:
            raise ValueError("Capacity must be non-negative")
        self.capacity = new_capacity
        self._promote()

    def snapshot(self) -> dict:
        """Return deterministic snapshot of internal state for debugging/tests."""
        return {
            "capacity": self.capacity,
            "registered": list(self._registered),
            "waitlist": list(self._waitlist),
            "messages": list(self.messages),
        }