from langgraph.graph import MessagesState, StateGraph
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash', api_key=os.getenv('GEMINI_API_KEY'))

class State(MessagesState):
    pass

def chatbot_node(state: State):
    system_msg = {
        "role": "system",
        "content": (
            "You are a trade analyzing assistant. "
            "Given the trade information, your task is to decide whether the trade is worth copying or not"
            "Output 'COPY' or 'PASS' based on the decision."
        ),
    }
    response = llm.invoke([system_msg] + state["messages"])
    return {"messages": [response]}

graph = StateGraph(State)
graph.set_entry_point("chatbot_node")
graph.add_node("chatbot_node", chatbot_node)

compiled_graph = graph.compile()

if __name__ == "__main__":
    response = compiled_graph.invoke({"messages": [{"role": "user", "content": "Who is Walter White?"}]})
    print(response)
    print(response["messages"][-1].content)