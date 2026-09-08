import unittest
from chatbot.db_schema import resolve_embedding_column, resolve_model_column

class FakeCursor:
    def __init__(self, cols): self.cols = cols
    def execute(self, *args, **kwargs): pass
    def fetchall(self): return [(c,) for c in self.cols]

class SchemaTests(unittest.TestCase):
    def test_embedding_without_model_name(self):
        c = FakeCursor({'id','document_id','embedding','created_at'})
        self.assertEqual(resolve_embedding_column(c), 'embedding')
        self.assertIsNone(resolve_model_column(c))

    def test_embedding_vector_with_model_name(self):
        c = FakeCursor({'id','document_id','embedding_vector','model_name'})
        self.assertEqual(resolve_embedding_column(c), 'embedding_vector')
        self.assertEqual(resolve_model_column(c), 'model_name')

if __name__ == '__main__': unittest.main()
