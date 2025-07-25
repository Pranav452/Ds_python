from collections import Counter
import re

class TextAnalyzer:
    def __init__(self, text):
        self.text = text
        self.text_lower = text.lower()

    def get_character_frequency(self, include_spaces=False):
        if not include_spaces:
            filtered = self.text.replace(" ", "")
        else:
            filtered = self.text
        return dict(Counter(filtered))

    def get_word_frequency(self, min_length=1):
        words = re.findall(r'\b\w+\b', self.text_lower)
        filtered_words = [w for w in words if len(w) >= min_length]
        return dict(Counter(filtered_words))

    def get_sentence_length_distribution(self):
        sentences = re.split(r'[.!?]+', self.text)
        sentences = [s.strip() for s in sentences if s.strip()]
        lengths = [len(re.findall(r'\b\w+\b', s)) for s in sentences]
        distribution = dict(Counter(lengths))
        avg = sum(lengths) / len(lengths) if lengths else 0
        return {
            "distribution": distribution,
            "average_length": avg,
            "longest": max(lengths) if lengths else 0,
            "shortest": min(lengths) if lengths else 0
        }

    def find_common_words(self, n=10, exclude_common=True):
        common_english = {
            "the", "is", "in", "and", "to", "of", "a", "for", "on", "with", "as", "by", "an", "at", "from", "that", "this", "it"
        }
        words = re.findall(r'\b\w+\b', self.text_lower)
        if exclude_common:
            words = [w for w in words if w not in common_english]
        freq = Counter(words)
        return freq.most_common(n)

    def get_reading_statistics(self):
        words = re.findall(r'\b\w+\b', self.text)
        sentences = re.split(r'[.!?]+', self.text)
        sentences = [s.strip() for s in sentences if s.strip()]
        char_count = len(self.text)
        word_count = len(words)
        sentence_count = len(sentences)
        avg_word_length = sum(len(w) for w in words) / word_count if word_count else 0
        # Average reading speed: 200 words per minute
        reading_time_min = word_count / 200 if word_count else 0
        return {
            "character_count": char_count,
            "word_count": word_count,
            "sentence_count": sentence_count,
            "average_word_length": avg_word_length,
            "estimated_reading_time_minutes": reading_time_min
        }

    def compare_with_text(self, other_text):
        words1 = set(re.findall(r'\b\w+\b', self.text_lower))
        words2 = set(re.findall(r'\b\w+\b', other_text.lower()))
        common = words1 & words2
        total = words1 | words2
        similarity = len(common) / len(total) if total else 0
        return {
            "common_words": common,
            "similarity_score": similarity
        }

# Sample usage
if __name__ == "__main__":
    sample_text = (
        "Python is a high-level, interpreted programming language. "
        "It is widely used for web development, data analysis, artificial intelligence, and more. "
        "Python's simple syntax makes it easy to learn."
    )
    analyzer = TextAnalyzer(sample_text)

    print("Character frequency:", analyzer.get_character_frequency())
    print("Word frequency:", analyzer.get_word_frequency())
    print("Sentence length distribution:", analyzer.get_sentence_length_distribution())
    print("Most common words:", analyzer.find_common_words())
    print("Reading statistics:", analyzer.get_reading_statistics())

    other_text = (
        "Java is also a popular programming language. "
        "It is used for building enterprise applications and Android apps."
    )
    print("Comparison with another text:", analyzer.compare_with_text(other_text))
