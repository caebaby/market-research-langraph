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
    return response.json().get("web", {}).get("results", [{"title": "Mock result"}])

class ToolBox:
    tools = {"web": web_search}

    @staticmethod
    def use(tool_name: str, input_str: str):
        return ToolBox.tools.get(tool_name, lambda x: x)(input_str)
