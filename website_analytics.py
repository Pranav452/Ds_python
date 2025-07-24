# website_analytics.py

# Example visitor sets for each day (replace with your actual data)
monday_visitors = {"alice", "bob", "carol", "dave"}
tuesday_visitors = {"bob", "carol", "eve", "frank"}
wednesday_visitors = {"carol", "dave", "frank", "grace"}

# 1. Unique Visitors Across All Days
unique_visitors = monday_visitors | tuesday_visitors | wednesday_visitors
print("1. Unique Visitors Across All Days:", unique_visitors)
print("   Total:", len(unique_visitors))

# 2. Returning Visitors on Tuesday (visited both Monday and Tuesday)
returning_tuesday = monday_visitors & tuesday_visitors
print("\n2. Returning Visitors on Tuesday:", returning_tuesday)

# 3. New Visitors Each Day (not seen on previous days)
new_monday = monday_visitors
new_tuesday = tuesday_visitors - monday_visitors
new_wednesday = wednesday_visitors - (monday_visitors | tuesday_visitors)
print("\n3. New Visitors Each Day:")
print("   Monday:", new_monday)
print("   Tuesday:", new_tuesday)
print("   Wednesday:", new_wednesday)

# 4. Loyal Visitors (visited all three days)
loyal_visitors = monday_visitors & tuesday_visitors & wednesday_visitors
print("\n4. Loyal Visitors (all three days):", loyal_visitors)

# 5. Daily Visitor Overlap Analysis
print("\n5. Daily Visitor Overlap Analysis:")
print("   Monday & Tuesday:", monday_visitors & tuesday_visitors)
print("   Tuesday & Wednesday:", tuesday_visitors & wednesday_visitors)
print("   Monday & Wednesday:", monday_visitors & wednesday_visitors)
