from shared.web_search import WebSearch

web = WebSearch()

# Search the web test input
results = web.search(
    query = "Current midterm news as of November 5th",
    max_results = 5
)

# Check recorded usage
monthly_total = web.usage_tracker.get_monthly_usage()
print("Monthly credits used:", monthly_total)

# Display usage history
history = web.usage_tracker.get_usage_history()

for record in history:
    print(record)