# core/tools.py

import os
import requests

def web_search(query: str):
    # Use your Brave Search API (replace with key)
    key = os.getenv("BRAVE_SEARCH_API_KEY")
    if not key:
        return "Add BRAVE_SEARCH_API_KEY to env"
    
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {"X-Subscription-Token": key}
    params = {"q": query, "count": 5}
    
    response = requests.get(url, headers=headers, params=params)
    results = response.json().get("web", {}).get("results", [])
    
    # Format results for agent consumption
    formatted_results = []
    for r in results:
        formatted_results.append(f"Title: {r.get('title', 'No title')}\nURL: {r.get('url', '')}\nDescription: {r.get('description', '')}\n")
    
    return "\n".join(formatted_results) if formatted_results else "No results found"

class ToolBox:
    tools = {"web": web_search, "web_search": web_search}  # Support both names
    
    @staticmethod
    def use(tool_name: str, input_str: str):
        return ToolBox.tools.get(tool_name, lambda x: f"Unknown tool: {tool_name}")(input_str)
    
    def execute(self, tool_name: str, params: dict):
        """Add execute method for StandardAgentNode compatibility"""
        if tool_name == "web_search":
            query = params.get("query", "")
            return self.use("web", query)
        else:
            return f"Unknown tool: {tool_name}"
