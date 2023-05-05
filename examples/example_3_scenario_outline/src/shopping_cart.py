class ShoppingCart:
    def __init__(self) -> None:
        self.items = []

    def get_items(self):
        return self.items

    def get_items_count(self):
        return len(self.items)

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item):
        self.items.remove(item)
        