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
from typing import List, Optional
import re


class DuplicateRequest(Exception):
    """Raised if a user tries to register but is already registered or waitlisted."""
    pass


class NotFound(Exception):
    """Raised if a user cannot be found for cancellation (if required by handout)."""
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
    Students must implement this class per the lab handout.
    Deterministic ordering is required (e.g., FIFO waitlist, predictable registration order).
    """

    USER_ID_PATTERN = re.compile(r"^[A-Za-z0-9]{1,12}$")

    def __init__(self, capacity: int) -> None:
        """
        Args:
            capacity: maximum number of registered users (>= 0)
        """
        # TODO: Initialize internal data structures

        if capacity < 0:
            raise ValueError("Capacity must be greater than zero")

        self.capacity = capacity
        self._registered: List[str] = []
        self._waitlist: List[str] = []
        self._users: set[str] = set()

        raise NotImplementedError("EventRegistration.__init__ not implemented yet")
    
    def _validate_user_id(self, user_id: str) -> None:
        if not isinstance(user_id, str):
            raise ValueError("user_id must be a string")

        if not self.USER_ID_PATTERN.fullmatch(user_id):
            raise ValueError("Invalid user_id")
        
    def _promote(self) -> None:
        """
        Promote waitlisted users until capacity is filled or waitlist empty.
        Ensures invariant C8.
        """
        while len(self._registered) < self.capacity and self._waitlist:
            user = self._waitlist.pop(0)
            self._registered.append(user)

    

    def register(self, user_id: str) -> UserStatus:
        """
        Register a user:
          - if capacity available -> registered
          - else -> waitlisted (FIFO)

        Raises:
            DuplicateRequest if user already exists (registered or waitlisted)
        """
        # TODO: Implement per lab handout

        self._validate_user_id(user_id)

        if user_id in self._users:
            raise DuplicateRequest("User already registered or waitlisted")

        self._users.add(user_id)

        if len(self._registered) < self.capacity:
            self._registered.append(user_id)
            return UserStatus("registered")

        self._waitlist.append(user_id)

        return UserStatus("waitlisted", len(self._waitlist))
    
        raise NotImplementedError("register not implemented yet")

    def cancel(self, user_id: str) -> None:
        """
        Cancel a user:
          - if registered -> remove and promote earliest waitlisted user (if any)
          - if waitlisted -> remove from waitlist
          - behavior when user not found depends on handout (raise NotFound or ignore)

        Raises:
            NotFound (if required by handout)
        """
        # TODO: Implement per lab handout

        self._validate_user_id(user_id)

        if user_id not in self._users:
            raise NotFound("User not found")

        if user_id in self._registered:
            self._registered.remove(user_id)
            self._users.remove(user_id)
            self._promote()
            return

        if user_id in self._waitlist:
            self._waitlist.remove(user_id)
            self._users.remove(user_id)
            return

        raise NotFound("User not found")
    
        raise NotImplementedError("cancel not implemented yet")

    def status(self, user_id: str) -> UserStatus:
        """
        Return status of a user:
          - registered
          - waitlisted with position (1-based)
          - none
        """
        # TODO: Implement per lab handout

        self._validate_user_id(user_id)

        if user_id in self._registered:
            return UserStatus("registered")

        if user_id in self._waitlist:
            pos = self._waitlist.index(user_id) + 1
            return UserStatus("waitlisted", pos)

        return UserStatus("none")
    
        raise NotImplementedError("status not implemented yet")
    
    def get_registered(self) -> List[str]:
        """Return copy of registered users."""
        return list(self._registered)

    def get_waitlist(self) -> List[str]:
        """Return copy of waitlisted users."""
        return list(self._waitlist)

    def snapshot(self) -> dict:
        """
        (Optional helper for debugging/tests)
        Return a deterministic snapshot of internal state.
        """
        # TODO: Implement if required/allowed

        return {
            "capacity": self.capacity,
            "registered": list(self._registered),
            "waitlist": list(self._waitlist),
        }

        raise NotImplementedError("snapshot not implemented yet")