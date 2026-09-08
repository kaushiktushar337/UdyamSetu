from chatbot.chat_service import ChatService
from chatbot.schemas import ChatRequest

def main():
    service = ChatService()
    conversation_id = None
    print("UdyamSetu Chatbot CLI. Type 'exit' to quit.")
    while True:
        text = input("\nYou: ").strip()
        if text.lower() in {"exit", "quit"}:
            break
        response = service.chat(ChatRequest(message=text, conversation_id=conversation_id))
        conversation_id = response.conversation_id
        print("\nUdyamSetu:", response.answer)
        if response.sources:
            print("Sources:", ", ".join(s["title"] for s in response.sources))

if __name__ == "__main__":
    main()
