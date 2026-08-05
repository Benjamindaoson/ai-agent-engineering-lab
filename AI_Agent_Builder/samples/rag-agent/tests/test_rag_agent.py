from __future__ import annotations

import unittest

from rag_agent import answer


class RagAgentTests(unittest.TestCase):
    def test_returns_grounded_answer_for_rag_query(self) -> None:
        response = answer("RAG retrieval evaluation")
        self.assertIn("RAG systems", response)

    def test_returns_no_grounded_answer_when_missing_context(self) -> None:
        response = answer("payroll invoice workflow")
        self.assertEqual(response, "No grounded answer found.")


if __name__ == "__main__":
    unittest.main()

