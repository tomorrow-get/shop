class UsernameConverter:
    regex='[0-9a-zA-Z_-]{5,20}'
    def to_python(self, value):
        return value
class MobileConverter:
    regex=r'1[3-9]\d{9}'
    def to_python(self, value):
        return str(value)
class UuidConverter:
    regex='[\w-]+'
    def to_python(self, value):
        return str(value)