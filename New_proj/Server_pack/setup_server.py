import sys
from cx_Freeze import setup, Executable

build_exe_options = {"packages": ["os"], "excludes": ["tkinter"]}
setup(name="myscript",
      version="0.0.1",
      description="My Hello World application!",
      options={"build_exe": build_exe_options},
      executables=[Executable("myscript.py")])

