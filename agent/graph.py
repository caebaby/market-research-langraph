from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langgraph import Graph

def research_agent(state):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    
    prompt = ChatPromptTemplate.from_template("""
    Conduct comprehensive ICP research for:
    {business_context}
    
    Provide deep psychological insights and customer analysis.
    """)
    
    response = llm.invoke(prompt.format(business_context=state["input"]))
    return {"output": response.content}

# Create the graph
graph = Graph()
graph.add_node("research", research_agent)
graph.set_entry_point("research")
graph.set_finish_point("research")
