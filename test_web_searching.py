from shared.web_search import WebSearch

web = WebSearch()

# Search the web test input
results = web.search(
    query = "Current midterm news as of November 3rd",
    max_results = 5
)

for result in results:
    print("\nTitle:", result["title"])
    print("URL:", result["url"])
    print("Content:", result["content"])
    print("*" * 60)