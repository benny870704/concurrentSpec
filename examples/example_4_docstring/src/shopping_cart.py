class ShoppingCart:
    def __init__(self) -> None:
        self.items = []

    def get_items(self):
        return self.items

    def get_items_count(self):
        return len(self.items)

    def add_item(self, name, description=""):
        item = Item(name, description)
        self.items.append(item)

    def remove_item(self, name):
        for item in self.items[:]:
            if item.get_name() == name:
                self.items.remove(item)

    def items_info(self):
        return "".join([item.get_info() for item in self.items])

class Item:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def get_name(self):
        return self.name

    def get_description(self):
        return self.description
    
    def get_info(self):
        return f"{self.name}: {self.description}\n"
    