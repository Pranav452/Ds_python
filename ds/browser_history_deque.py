# browser_history_deque.py

from collections import deque

class BrowserHistory:
    def __init__(self, max_size=5):
        self.history = deque(maxlen=max_size)
        self.forward_stack = deque()

    def add_page(self, url):
        self.forward_stack.clear()
        self.history.append(url)

    def go_back(self):
        if len(self.history) > 1:
            last_page = self.history.pop()
            self.forward_stack.append(last_page)

    def go_forward(self):
        if self.forward_stack:
            next_page = self.forward_stack.pop()
            self.history.append(next_page)

    def get_history(self):
        return list(self.history)

    def get_forward_stack(self):
        return list(self.forward_stack)
