from setuptools import setup, find_packages

setup(name="server_chat_tcp_ip",
      version="0.8.7",
      description="server",
      author="Liubov Ilinykh",
      author_email="lrlr2393@gmail.com",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex'],
      url="https://github.com/rlrl23/Async_chat",

      )
