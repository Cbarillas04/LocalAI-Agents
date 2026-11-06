from shared.usage_tracking import UsageTracking

tracker = UsageTracking()
print("Usage tracker initialized successfully.")

tracker.create_usage(
    credits_used=1,
    usage_type="estimated",
    endpoint="search",
    request_status="success"
)

print("Usage recorded successfully.")

monthly_total = tracker.get_monthly_usage()
print("Credits used this month:", monthly_total)