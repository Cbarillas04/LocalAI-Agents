from shared.usage_tracking import UsageTracking

tracker = UsageTracking()

monthly_total = tracker.get_monthly_usage()

print("Credits used this month:", monthly_total)