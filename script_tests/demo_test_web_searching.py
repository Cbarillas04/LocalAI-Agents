from shared.web_search import WebSearch

web = WebSearch()
'''
# Search the web test input
results = web.search(
    query = "Current midterm news as of November 6th, more specifically on mississippi.",
    max_results = 5
)
'''
web.usage_tracker.get_monthly_usage = lambda: 1000
try:
    web.client.search("test query")
except ValueError as err:
    print("Over monthly usage", err)

'''
# Check recorded usage
monthly_total = web.usage_tracker.get_monthly_usage()
print("Monthly credits used:", monthly_total)

# Display usage history
history = web.usage_tracker.get_usage_history()

for record in history:
    print(record)
'''