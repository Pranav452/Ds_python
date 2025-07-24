# social_media_analytics.py

from collections import Counter, defaultdict

# Example data
users = [
    {"id": 1, "name": "Alice", "followers": 120},
    {"id": 2, "name": "Bob", "followers": 80},
    {"id": 3, "name": "Charlie", "followers": 200},
]

posts = [
    {"id": 101, "user_id": 1, "content": "Hello world!", "likes": 15, "tags": ["intro", "hello"]},
    {"id": 102, "user_id": 2, "content": "Python is awesome!", "likes": 30, "tags": ["python", "coding"]},
    {"id": 103, "user_id": 1, "content": "Check out my new blog.", "likes": 25, "tags": ["blog", "python"]},
    {"id": 104, "user_id": 3, "content": "Good morning!", "likes": 10, "tags": ["morning", "hello"]},
    {"id": 105, "user_id": 2, "content": "Learning data structures.", "likes": 20, "tags": ["python", "learning"]},
    {"id": 106, "user_id": 3, "content": "Follow me for more!", "likes": 50, "tags": ["follow", "intro"]},
]

# 1. Most Popular Tags
all_tags = []
for post in posts:
    all_tags.extend(post["tags"])
tag_counter = Counter(all_tags)
most_common_tags = tag_counter.most_common()
print("Most Popular Tags:")
for tag, count in most_common_tags:
    print(f"{tag}: {count}")
print()

# 2. User Engagement Analysis (total likes per user)
user_likes = defaultdict(int)
for post in posts:
    user_likes[post["user_id"]] += post["likes"]
print("Total Likes Per User:")
for user in users:
    print(f"{user['name']}: {user_likes[user['id']]}")
print()

# 3. Top Posts by Likes
sorted_posts = sorted(posts, key=lambda x: x["likes"], reverse=True)
print("Top Posts by Likes:")
for post in sorted_posts:
    user_name = next(user["name"] for user in users if user["id"] == post["user_id"])
    print(f"Post ID {post['id']} by {user_name}: {post['likes']} likes")
print()

# 4. User Activity Summary
user_summary = {}
for user in users:
    user_posts = [post for post in posts if post["user_id"] == user["id"]]
    total_likes = sum(post["likes"] for post in user_posts)
    summary = {
        "posts_count": len(user_posts),
        "total_likes": total_likes,
        "followers": user["followers"]
    }
    user_summary[user["name"]] = summary

print("User Activity Summary:")
for name, summary in user_summary.items():
    print(f"{name}: Posts={summary['posts_count']}, Likes={summary['total_likes']}, Followers={summary['followers']}")
