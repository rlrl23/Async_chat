"""Check the value of port"""

class Port:
    def __init__(self):
        """Set default value of port"""
        self.port=7777

    def __get__(self, instance, value):
        """Get the value of port"""
        return self.port

    def __set__(self, instance, value):
        """Check the value of port"""
        if isinstance(value, int) and value>=0:
            self.port = value
            print('Port is correct')
        else:
            print('ValueError, порт должен быть положительным и целым числом')
            print('Использован порт по умолчанию - 7777')
