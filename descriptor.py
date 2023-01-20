class Port:
    def __init__(self):
        self.port=7777

    def __get__(self, instance, value):
        return self.port

    def __set__(self, instance, value):
        if isinstance(value, int) and value>=0:
            self.port = value
            print('Port is correct')
        else:
            print('ValueError, порт должен быть положительным и целым числом')
            print('Использован порт по умолчанию - 7777')
