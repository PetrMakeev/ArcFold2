del ArcFold.exe
del ArcFoldService.exe
del dist\Arc*
pyinstaller --name ArcFoldService --onefile --noconsole --add-data "icons;icons" --icon="icons/monitor.ico" service.py
pyinstaller --name ArcFold --onefile --noconsole --add-data "icons;icons" --icon="icons/archive.ico" main.py
copy dist\Arc*.exe .