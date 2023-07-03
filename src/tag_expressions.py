class TagExpressions:
    def __init__(self):
        self.filter_tags = []

    def add_filter_tags(self, tags: list):
        for condition in tags:
            if len(condition) == 1 and condition[0].find(',') != -1:
                temp = [tag for tag in condition[0].split(',') if tag != '']
                for index, tag in enumerate(temp):
                    temp[index] = self.normalize_tag(tag)
                self.filter_tags.append(temp)
            elif len(condition) == 1 and condition[0].find(',') == -1:
                self.filter_tags.append([self.normalize_tag(condition[0])])
            else:
                temp = []
                for index, tag in enumerate(condition):
                    temp[index] = self.normalize_tag(tag)
                self.filter_tags.append(temp)

    def normalize_tag(self, tag: str):
        if tag.startswith('@'):
            return tag[1:]
        elif tag.startswith('~@'):
            return f"~{tag[2:]}"
        return tag

    def match(self, tags):
        check_list = []
        for expression in self.filter_tags:
            check_list.append(self.__match_an_expression(expression, tags))
        return all(check_list) and any(check_list)

    def __match_an_expression(self, expression: list, tags: list):
        for tag in expression:
            if not tag.startswith('~') and tag in tags:
                return True
            elif tag.startswith('~') and tag[1:] not in tags:
                return True
        return False