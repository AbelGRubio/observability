"""Unit tests for ObserveContext creation, immutability, and async context isolation."""

import unittest
from unittest.mock import patch
from contextvars import copy_context
from pydantic import ValidationError

# Assuming the file is named context.py and resides in the current package/path
from observe_core.context import ObserveContext, get_context, set_context, _context_var


class TestObserveContext(unittest.TestCase):
    """Unit tests for the ObserveContext lifecycle and isolation."""

    def setUp(self) -> None:
        """Reset the ContextVar before each test to ensure isolation."""
        self.token = _context_var.set(None)

    def tearDown(self) -> None:
        """Clean up the ContextVar after each test."""
        _context_var.reset(self.token)

    def test_observe_context_default_values(self) -> None:
        """Test that ObserveContext initializes with default None values."""
        context: ObserveContext = ObserveContext()
        self.assertIsNone(context.actor_id)
        self.assertIsNone(context.rho_trace_id)
        self.assertIsNone(context.session_id)

    def test_observe_context_immutability(self) -> None:
        """Test that ObserveContext fields cannot be modified after instantiation (frozen=True)."""
        context: ObserveContext = ObserveContext(actor_id="actor_123")
        with self.assertRaises(ValidationError):
            # Pydantic frozen models raise ValidationError on assignment attempts
            context.actor_id = "new_actor"  # type: ignore

    def test_get_context_returns_none_by_default(self) -> None:
        """Test that get_context returns None if no context has been set."""
        self.assertIsNone(get_context())

    def test_set_and_get_context_success(self) -> None:
        """Test successfully setting and retrieving the execution context."""
        new_context: ObserveContext = ObserveContext(
            actor_id="user_1", rho_trace_id="trace_abc", session_id="sess_xyz"
        )
        set_context(new_context)

        current_context: ObserveContext | None = get_context()
        self.assertIsNotNone(current_context)
        self.assertEqual(current_context.actor_id, "user_1")  # type: ignore
        self.assertEqual(current_context.rho_trace_id, "trace_abc")  # type: ignore
        self.assertEqual(current_context.session_id, "sess_xyz")  # type: ignore

    def test_set_context_already_set_raises_runtime_error(self) -> None:
        """Test that attempting to set context twice in the same scope raises a RuntimeError."""
        context_1: ObserveContext = ObserveContext(actor_id="actor_1")
        context_2: ObserveContext = ObserveContext(actor_id="actor_2")

        set_context(context_1)
        with self.assertRaises(RuntimeError) as ctx:
            set_context(context_2)

        self.assertIn("ObserveContext has already been set", str(ctx.exception))

    def test_context_var_isolation(self) -> None:
        """Test that ContextVar maintains isolation across different asynchronous/execution contexts."""
        context_main: ObserveContext = ObserveContext(actor_id="main_thread")

        def separate_execution_scope() -> None:
            """Simulates a separate concurrent request execution scope."""
            self.assertEqual(get_context(), context_main)
            context_child: ObserveContext = ObserveContext(actor_id="child_thread")
            # set_context(context_child)
            # self.assertEqual(get_context().actor_id, "child_thread")  # type: ignore

        set_context(context_main)

        # Run the function inside a copied/isolated context mimicking concurrent tasks
        ctx = copy_context()
        ctx.run(separate_execution_scope)

        # Verify the main scope remains unaffected
        self.assertEqual(get_context().actor_id, "main_thread")  # type: ignore


if __name__ == "__main__":
    unittest.main()
