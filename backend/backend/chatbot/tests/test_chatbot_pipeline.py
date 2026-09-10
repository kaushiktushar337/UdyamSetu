import unittest
from chatbot.schemas import ChatRequest, RetrievedDocument
from chatbot.context_builder import ContextBuilder
from chatbot.conversation_manager import ConversationManager
from chatbot.chat_service import ChatService

class FakeGenerator:
    model = "test-model"
    def __init__(self):
        self.calls = []
    def generate(self, user_message, context="", history=None):
        self.calls.append({"message": user_message, "context": context, "history": history or []})
        return "Grounded test answer"

class ChatbotPipelineTests(unittest.TestCase):
    def setUp(self):
        self.docs = [
            RetrievedDocument(1, "MSME Schemes", "Relevant scheme information", 0.91),
            RetrievedDocument(2, "Low relevance", "Ignore this", 0.10),
        ]
        self.memory = ConversationManager(database_url=None, max_history=10)
        self.generator = FakeGenerator()
        self.service = ChatService(
            retriever=lambda q: self.docs,
            context_builder=ContextBuilder(threshold=0.35, max_chars=1000),
            memory=self.memory,
            generator=self.generator,
        )

    def test_context_filters_low_similarity(self):
        context, used = ContextBuilder(threshold=0.35).build(self.docs)
        self.assertEqual(len(used), 1)
        self.assertIn("MSME Schemes", context)
        self.assertNotIn("Low relevance", context)

    def test_full_chat_response_pipeline(self):
        response = self.service.chat(ChatRequest(message="What MSME help is available?"))
        self.assertEqual(response.answer, "Grounded test answer")
        self.assertTrue(response.used_context)
        self.assertEqual(len(response.sources), 1)
        self.assertEqual(self.generator.calls[0]["history"], [])

    def test_conversation_memory(self):
        first = self.service.chat(ChatRequest(message="Tell me about MSME support"))
        second = self.service.chat(ChatRequest(message="What about eligibility?", conversation_id=first.conversation_id))
        self.assertEqual(first.conversation_id, second.conversation_id)
        history = self.generator.calls[1]["history"]
        self.assertGreaterEqual(len(history), 2)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[1]["role"], "assistant")

    def test_empty_message_rejected(self):
        with self.assertRaises(ValueError):
            self.service.chat(ChatRequest(message="   "))

if __name__ == "__main__":
    unittest.main()
