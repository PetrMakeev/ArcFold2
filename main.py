import ctypes
import sys

from gui_app.main import main   



 
if __name__ == "__main__":
    # Проверка, запущено ли приложение с правами администратора
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    # Перезапуск приложения с правами администратора
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " " + " ".join(sys.argv), None, 1)
        sys.exit() 
           
    main() 