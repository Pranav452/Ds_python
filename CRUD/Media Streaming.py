    # main.py

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
import random

# --- Abstract Base Classes ---

class MediaContent(ABC):
    def __init__(self, title: str, category: str, premium: bool = False):
        self.title = title
        self.category = category
        self.premium = premium
        self.ratings = []

    @abstractmethod
    def play(self):
        pass

    @abstractmethod
    def get_duration(self) -> int:
        pass

    @abstractmethod
    def get_file_size(self) -> float:
        pass

    @abstractmethod
    def calculate_streaming_cost(self) -> float:
        pass

    def add_rating(self, rating: int):
        if 1 <= rating <= 5:
            self.ratings.append(rating)

    def get_average_rating(self) -> float:
        if not self.ratings:
            return 0.0
        return sum(self.ratings) / len(self.ratings)

    def is_premium_content(self) -> bool:
        return self.premium

class StreamingDevice(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def stream_content(self, content: MediaContent):
        pass

    @abstractmethod
    def adjust_quality(self, quality: str):
        pass

    def get_device_info(self) -> str:
        return f"Device: {self.name}"

    def check_compatibility(self, content: MediaContent) -> bool:
        # For simplicity, all devices are compatible with all content
        return True

# --- Concrete Media Content Classes ---

class Movie(MediaContent):
    def __init__(self, title, duration, resolution, genre, director, file_size, premium=False):
        super().__init__(title, "Movie", premium)
        self.duration = duration  # in minutes
        self.resolution = resolution
        self.genre = genre
        self.director = director
        self.file_size = file_size  # in GB

    def play(self):
        return f"Playing movie: {self.title} ({self.resolution})"

    def get_duration(self):
        return self.duration

    def get_file_size(self):
        return self.file_size

    def calculate_streaming_cost(self):
        base = 2.0
        if self.premium:
            base *= 2
        return base + 0.1 * self.duration

class TVShow(MediaContent):
    def __init__(self, title, episodes, seasons, current_episode, file_size, premium=False):
        super().__init__(title, "TVShow", premium)
        self.episodes = episodes
        self.seasons = seasons
        self.current_episode = current_episode
        self.file_size = file_size

    def play(self):
        return f"Playing TV Show: {self.title} S{self.seasons}E{self.current_episode}"

    def get_duration(self):
        return self.episodes * 45  # assume 45 min per episode

    def get_file_size(self):
        return self.file_size

    def calculate_streaming_cost(self):
        base = 1.5
        if self.premium:
            base *= 2
        return base + 0.05 * self.episodes

class Podcast(MediaContent):
    def __init__(self, title, episode_number, transcript_available, duration, file_size, premium=False):
        super().__init__(title, "Podcast", premium)
        self.episode_number = episode_number
        self.transcript_available = transcript_available
        self.duration = duration
        self.file_size = file_size

    def play(self):
        return f"Playing Podcast: {self.title} Episode {self.episode_number}"

    def get_duration(self):
        return self.duration

    def get_file_size(self):
        return self.file_size

    def calculate_streaming_cost(self):
        base = 1.0
        if self.premium:
            base *= 2
        return base + 0.02 * self.duration

class Music(MediaContent):
    def __init__(self, title, artist, album, lyrics_available, duration, file_size, premium=False):
        super().__init__(title, "Music", premium)
        self.artist = artist
        self.album = album
        self.lyrics_available = lyrics_available
        self.duration = duration
        self.file_size = file_size

    def play(self):
        return f"Playing Music: {self.title} by {self.artist}"

    def get_duration(self):
        return self.duration

    def get_file_size(self):
        return self.file_size

    def calculate_streaming_cost(self):
        base = 0.5
        if self.premium:
            base *= 2
        return base + 0.01 * self.duration

# --- Concrete Streaming Device Classes ---

class SmartTV(StreamingDevice):
    def __init__(self):
        super().__init__("SmartTV")

    def connect(self):
        return "SmartTV connected with 4K support and surround sound."

    def stream_content(self, content: MediaContent):
        return f"Streaming '{content.title}' on SmartTV in 4K."

    def adjust_quality(self, quality: str):
        return f"SmartTV quality set to {quality}."

class Laptop(StreamingDevice):
    def __init__(self):
        super().__init__("Laptop")

    def connect(self):
        return "Laptop connected with headphone support."

    def stream_content(self, content: MediaContent):
        return f"Streaming '{content.title}' on Laptop."

    def adjust_quality(self, quality: str):
        return f"Laptop quality set to {quality}."

class Mobile(StreamingDevice):
    def __init__(self):
        super().__init__("Mobile")

    def connect(self):
        return "Mobile connected with battery optimization."

    def stream_content(self, content: MediaContent):
        return f"Streaming '{content.title}' on Mobile."

    def adjust_quality(self, quality: str):
        return f"Mobile quality set to {quality}."

class SmartSpeaker(StreamingDevice):
    def __init__(self):
        super().__init__("SmartSpeaker")

    def connect(self):
        return "SmartSpeaker connected with voice control."

    def stream_content(self, content: MediaContent):
        return f"Streaming '{content.title}' audio on SmartSpeaker."

    def adjust_quality(self, quality: str):
        return f"SmartSpeaker audio quality set to {quality}."

# --- User Class ---

class User:
    def __init__(self, name: str, subscription: str = "Free"):
        self.name = name
        self.subscription = subscription  # Free, Premium, Family
        self.watch_history: List[MediaContent] = []
        self.preferences: Dict[str, Any] = {}
        self.parental_control = False

    def add_to_history(self, content: MediaContent):
        self.watch_history.append(content)

    def set_preferences(self, **kwargs):
        self.preferences.update(kwargs)

    def enable_parental_control(self):
        self.parental_control = True

    def disable_parental_control(self):
        self.parental_control = False

    def get_watch_time(self):
        return sum(content.get_duration() for content in self.watch_history)

# --- Streaming Platform Class ---

class StreamingPlatform:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.contents: List[MediaContent] = []
        self.devices: List[StreamingDevice] = []

    def add_user(self, user: User):
        self.users[user.name] = user

    def add_content(self, content: MediaContent):
        self.contents.append(content)

    def add_device(self, device: StreamingDevice):
        self.devices.append(device)

    def recommend_content(self, user: User) -> List[MediaContent]:
        # Simple recommendation: based on category in preferences
        preferred = user.preferences.get("category")
        if preferred:
            recs = [c for c in self.contents if c.category == preferred and (not user.parental_control or not c.is_premium_content())]
        else:
            recs = [c for c in self.contents if not user.parental_control or not c.is_premium_content()]
        return recs[:3]  # top 3

    def stream(self, user: User, device: StreamingDevice, content: MediaContent):
        if content.is_premium_content() and user.subscription == "Free":
            return "Upgrade to Premium to watch this content."
        if user.parental_control and content.is_premium_content():
            return "Content blocked by parental controls."
        user.add_to_history(content)
        return device.stream_content(content)

    def get_analytics(self, user: User):
        total_time = user.get_watch_time()
        return f"{user.name} has watched {total_time} minutes in total."

    def filter_content(self, user: User):
        if user.parental_control:
            return [c for c in self.contents if not c.is_premium_content()]
        return self.contents

# --- Example Test Cases ---

if __name__ == "__main__":
    # Create platform
    platform = StreamingPlatform()

    # Add contents
    m1 = Movie("Inception", 148, "4K", "Sci-Fi", "Nolan", 2.5, premium=True)
    m2 = Movie("Toy Story", 90, "HD", "Animation", "Lasseter", 1.2)
    tv1 = TVShow("Friends", 24, 1, 5, 5.0)
    p1 = Podcast("Python Bytes", 10, True, 30, 0.1)
    mu1 = Music("Imagine", "John Lennon", "Imagine", True, 3, 0.02)

    for c in [m1, m2, tv1, p1, mu1]:
        platform.add_content(c)

    # Add devices
    tv = SmartTV()
    laptop = Laptop()
    mobile = Mobile()
    speaker = SmartSpeaker()
    for d in [tv, laptop, mobile, speaker]:
        platform.add_device(d)

    # Add user
    user = User("Alice", "Free")
    user.set_preferences(category="Movie")
    platform.add_user(user)

    # Test recommendations
    recs = platform.recommend_content(user)
    print("Recommendations:", [c.title for c in recs])

    # Try to stream premium content on Free
    print(platform.stream(user, tv, m1))  # Should ask to upgrade

    # Stream non-premium content
    print(platform.stream(user, laptop, m2))  # Should work

    # Enable parental control and try to stream premium
    user.enable_parental_control()
    print(platform.stream(user, tv, m1))  # Should block

    # Analytics
    print(platform.get_analytics(user))

    # Ratings
    m2.add_rating(5)
    m2.add_rating(4)
    print(f"Average rating for {m2.title}: {m2.get_average_rating()}")

    # Device info
    print(tv.get_device_info())
    print(tv.connect())
    print(tv.adjust_quality("Ultra HD"))
