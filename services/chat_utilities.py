from llama_index.core.base.llms.types import ChatMessage, MessageRole

from llm_factory.get_llm import get_ollama_llm


def get_answer(model_name, chat_history):
    llm = get_ollama_llm(model_name)

    #always prepend a system message
    messages = [
        ChatMessage(role = MessageRole.SYSTEM,content="You are a helpful chat assistant")
    ]

    #Append the rest of the chat history
    messages.extend(
        ChatMessage(role=msg["role"],content=msg["content"])
        for msg in chat_history
    )
    response = llm.chat(messages=messages)
    return response.message.content