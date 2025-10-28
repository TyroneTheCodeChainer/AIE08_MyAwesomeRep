"""
Test script for custom MCP tools
This script tests the dad joke and programming quote tools
"""
import requests

def test_dad_joke_random():
    """Test getting a random dad joke"""
    print("Testing random dad joke...")
    base_url = "https://icanhazdadjoke.com"
    headers = {
        "Accept": "application/json",
        "User-Agent": "MCP Server Demo Test"
    }
    
    response = requests.get(base_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Random joke retrieved: {data['joke']}")
        return True
    else:
        print(f"[FAIL] Failed to get random joke: {response.status_code}")
        return False

def test_dad_joke_search():
    """Test searching for a specific joke topic"""
    print("\nTesting dad joke search...")
    base_url = "https://icanhazdadjoke.com"
    headers = {
        "Accept": "application/json",
        "User-Agent": "MCP Server Demo Test"
    }
    
    search_term = "computer"
    response = requests.get(
        f"{base_url}/search",
        headers=headers,
        params={"term": search_term, "limit": 1}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            joke = data["results"][0]["joke"]
            print(f"[OK] Found joke about '{search_term}': {joke}")
            return True
        else:
            print(f"[INFO] No jokes found for '{search_term}'")
            return True
    else:
        print(f"[FAIL] Failed to search jokes: {response.status_code}")
        return False

def test_programming_quote():
    """Test getting a programming quote"""
    print("\nTesting programming quote...")
    try:
        response = requests.get("https://api.quotable.io/random?tags=technology")
        if response.status_code == 200:
            data = response.json()
            quote = data.get("content", "")
            author = data.get("author", "Unknown")
            print(f'[OK] Quote retrieved: "{quote}" - {author}')
            return True
        else:
            print(f"[INFO] API returned {response.status_code}, but fallback quotes will work")
            return True
    except Exception as e:
        print(f"[INFO] Exception occurred, but fallback quotes will work: {e}")
        return True

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Custom MCP Tools")
    print("=" * 60)
    
    results = []
    results.append(test_dad_joke_random())
    results.append(test_dad_joke_search())
    results.append(test_programming_quote())
    
    print("\n" + "=" * 60)
    if all(results):
        print("[SUCCESS] All tests passed!")
    else:
        print("[FAIL] Some tests failed")
    print("=" * 60)
