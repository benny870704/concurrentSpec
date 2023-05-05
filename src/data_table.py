import re
import prettytable as pt

class DataTable:
    @classmethod
    def is_data_table(cls, string):
        try:
            cls.__check_data_table_is_valid(cls, string)
            return True
        except:
            return False

    def __init__(self, data_table_string):
        self.__check_data_table_is_valid(data_table_string)
        self.data_table_string = data_table_string

    def __repr__(self) -> str:
        return f"DataTable({len(self.to_list())}x{len(self.to_list()[0])})"

    def __check_data_table_is_valid(self, table_string: str):
        if table_string is not None:
            if table_string.find('|') == -1: raise Exception("Do not contain data table.") 

            data_rows = re.split(r'\|\s*\n\s*\|\s*', table_string)
            rows = [row.strip().split('|') for row in data_rows]

            for index, row in enumerate(rows[:]):
                rows[index] = [re.sub(r'^[ \t]+|[ \t]+$', '', variable, flags=re.MULTILINE) for variable in row if variable != ""]

            keys = rows[0]
            for values in rows[1:]:
                if len(values) != len(keys):
                    raise Exception("Cannot parse table correctly.")
                
    def to_list(self):
        data_rows = re.split(r'\|\s*\n\s*\|\s*', self.data_table_string)
        rows = [row.strip().split('|') for row in data_rows]

        for index, row in enumerate(rows[:]):
            rows[index] = [re.sub(r'^[ \t]+|[ \t]+$', '', variable, flags=re.MULTILINE) for variable in row if variable != ""]
        return rows
    
    def to_list_of_dict(self):
        data_table = []
        rows = self.to_list()

        keys = rows[0]
        for values in rows[1:]:
            data = {}
            for key, value in zip(keys, values):
                data[key] = value
            data_table.append(data)
        
        return data_table
    
    def to_list_of_key_to_values(self):
        data_table = []
        rows = self.to_list()

        data = {}
        keys = rows[0]
        for values in rows[1:]:
            for key, value in zip(keys, values):
                if key in data: data[key].append(value)
                else: data[key] = [value]
        data_table.append(data)
        
        return data_table
    
    def get_string(self):
        rows = self.to_list()
        table = pt.PrettyTable()
        table.set_style(pt.MSWORD_FRIENDLY)
        table.field_names = rows[0]
        table.add_rows(rows[1:])
        return table.get_string() + "\n"
    
    def get_pretty_string(self, indent = "    "):
        return "".join([indent + row + "\n" for row in self.get_string().splitlines()])
    
    def pretty(self, indent = "    "):
        print(self.get_pretty_string(indent))
        
