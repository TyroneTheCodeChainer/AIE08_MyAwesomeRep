from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient
import os
from dice_roller import DiceRoller
import requests
import random

load_dotenv()

mcp = FastMCP("mcp-server")
client = TavilyClient(os.getenv("TAVILY_API_KEY"))

@mcp.tool()
def web_search(query: str) -> str:
    """Search the web for information about the given query"""
    search_results = client.get_search_context(query=query)
    return search_results

@mcp.tool()
def roll_dice(notation: str, num_rolls: int = 1) -> str:
    """Roll the dice with the given notation"""
    roller = DiceRoller(notation, num_rolls)
    return str(roller)

@mcp.tool()
def get_dad_joke(search_term: str = "") -> str:
    """
    Get a random dad joke or search for jokes about a specific topic.

    Args:
        search_term: Optional keyword to search for jokes about a specific topic.
                    Leave empty for a completely random joke.

    Returns:
        A dad joke as a string.
    """
    base_url = "https://icanhazdadjoke.com"
    headers = {
        "Accept": "application/json",
        "User-Agent": "MCP Server Demo (https://github.com/AI-Maker-Space/AIE8-MCP-Session)"
    }

    try:
        if search_term:
            # Search for jokes with the given term
            response = requests.get(
                f"{base_url}/search",
                headers=headers,
                params={"term": search_term, "limit": 1}
            )
            response.raise_for_status()
            data = response.json()

            if data["results"]:
                joke = data["results"][0]["joke"]
                return f"Found a joke about '{search_term}':\n\n{joke}"
            else:
                return f"No jokes found about '{search_term}'. Try another topic!"
        else:
            # Get a random joke
            response = requests.get(base_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            return f"Random Dad Joke:\n\n{data['joke']}"

    except requests.exceptions.RequestException as e:
        return f"Error fetching joke: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

@mcp.tool()
def get_programming_quote() -> str:
    """
    Get a random programming-related quote from a curated collection.

    Returns:
        A programming quote with attribution.
    """
    try:
        # Using the quotable.io API for programming quotes
        response = requests.get("https://api.quotable.io/random?tags=technology")
        response.raise_for_status()
        data = response.json()

        quote = data.get("content", "")
        author = data.get("author", "Unknown")

        return f'"{quote}"\n\n— {author}'

    except requests.exceptions.RequestException as e:
        # Fallback quotes if API fails
        fallback_quotes = [
            '"Talk is cheap. Show me the code."\n\n— Linus Torvalds',
            '"Programs must be written for people to read, and only incidentally for machines to execute."\n\n— Harold Abelson',
            '"Any fool can write code that a computer can understand. Good programmers write code that humans can understand."\n\n— Martin Fowler'
        ]
        return random.choice(fallback_quotes)
    except Exception as e:
        return f"Error fetching quote: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
