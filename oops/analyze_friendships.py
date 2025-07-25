def analyze_friendships():
    """
    Analyze friendship patterns across different social media platforms.
    """
    # Friend lists for each platform
    facebook_friends = {"alice", "bob", "charlie", "diana", "eve", "frank"}
    instagram_friends = {"bob", "charlie", "grace", "henry", "alice", "ivan"}
    twitter_friends = {"alice", "diana", "grace", "jack", "bob", "karen"}
    linkedin_friends = {"charlie", "diana", "frank", "grace", "luke", "mary"}

    # 1. Friends on all four platforms (intersection)
    all_four = facebook_friends & instagram_friends & twitter_friends & linkedin_friends

    # 2. Friends only on Facebook (not on any other)
    only_facebook = facebook_friends - (instagram_friends | twitter_friends | linkedin_friends)

    # 3. Friends on Instagram or Twitter but not both (symmetric difference)
    insta_or_twitter_not_both = instagram_friends ^ twitter_friends

    # 4. Total unique friends across all platforms (union)
    total_unique = facebook_friends | instagram_friends | twitter_friends | linkedin_friends

    # 5. Friends on exactly two platforms
    from collections import Counter
    all_friends = list(facebook_friends) + list(instagram_friends) + list(twitter_friends) + list(linkedin_friends)
    friend_counts = Counter(all_friends)
    exactly_two = {friend for friend, count in friend_counts.items() if count == 2}

    return {
        "all_four": all_four,
        "only_facebook": only_facebook,
        "insta_or_twitter_not_both": insta_or_twitter_not_both,
        "total_unique": total_unique,
        "exactly_two": exactly_two
    }

# Test the function and print results
result = analyze_friendships()
print("Friends on all four platforms:", result.get("all_four"))
print("Friends only on Facebook:", result.get("only_facebook"))
print("Friends on Instagram or Twitter but not both:", result.get("insta_or_twitter_not_both"))
print("Total unique friends across all platforms:", result.get("total_unique"))
print("Friends on exactly two platforms:", result.get("exactly_two"))
