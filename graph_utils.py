import streamlit as st
from langchain_community.chains import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
from langchain_openai import ChatOpenAI

@st.cache.resource(show_spinner=False)
def initialize_resources(api_key: str):
    graph = Neo4jGraph(url=st.secrets["NEO4J_URI"], 
    username=st.secrets["NEO4J_USER"], 
    password=st.secrets["NEO4J_PASSWORD"],
    enhanced_schema=True,
    )
    graph.refresh_schema()
    chain = GraphCypherQAChain.from_llm(
        llm=ChatOpenAI(api_key=api_key, model="gpt-4o-mini", temperature=0), 
        graph=graph,
        verbose=True,
        show_intermediate_steps=True,
        allow_dangerous_content=True,
        )
    return graph, chain

def guery_graph(chain: GraphCypherQAChain, query: str):
    result = chain.invoke({"query": query})["result"]
    return result 