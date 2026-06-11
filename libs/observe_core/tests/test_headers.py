"""Unit tests for ObserveHeaders parsing rules and header validation behavior."""

import unittest
from pydantic import ValidationError

# Assuming the file is named headers.py
from observe_core.headers import (
    ObserveHeaders,
    HEADER_BEDROCK_ACTOR_ID,
    HEADER_BEDROCK_RHO_TRACE_ID,
    HEADER_BEDROCK_SESSION_ID,
    HEADER_BEDROCK_STREAMING,
)


class TestObserveHeaders(unittest.TestCase):
    """Unit tests for HTTP header mapping and Pydantic validation parsing."""

    def test_headers_default_values(self) -> None:
        """Test that ObserveHeaders instantiates with expected defaults when no headers are supplied."""
        headers: ObserveHeaders = ObserveHeaders()
        self.assertIsNone(headers.actor_id)
        self.assertIsNone(headers.baggage)
        self.assertIsNone(headers.rho_trace_id)
        self.assertIsNone(headers.session_id)
        self.assertFalse(headers.streaming)

    def test_headers_parsing_with_lowercase_validation_aliases(self) -> None:
        """Test that fields are successfully populated using standard lowercase ASGI/FastAPI headers."""
        input_data = {
            HEADER_BEDROCK_ACTOR_ID.lower(): "actor_low",
            HEADER_BEDROCK_RHO_TRACE_ID.lower(): "rho_low",
            HEADER_BEDROCK_SESSION_ID.lower(): "session_low",
            HEADER_BEDROCK_STREAMING.lower(): "false",
        }

        headers: ObserveHeaders = ObserveHeaders.model_validate(input_data)

        self.assertEqual(headers.actor_id, "actor_low")
        self.assertEqual(headers.rho_trace_id, "rho_low")
        self.assertEqual(headers.session_id, "session_low")
        self.assertFalse(headers.streaming)

    def test_headers_invalid_streaming_boolean_type(self) -> None:
        """Test that passing an invalid non-boolean value to the streaming header raises a ValidationError."""
        input_data = {
            HEADER_BEDROCK_STREAMING.lower(): "not-a-boolean"
        }

        with self.assertRaises(ValidationError):
            ObserveHeaders.model_validate(input_data)


if __name__ == "__main__":
    unittest.main()
