import win32serviceutil
import win32service
import win32api
import win32con
import win32event
import servicemanager
import subprocess
import sys
import os

SERVICE_NAME = 'ArcFoldMonitorService'

def install_service():
    """
    Устанавливает службу ArcFoldMonitorService.
    """
    try:
        module_path = os.path.abspath(__file__)
        win32serviceutil.InstallService(
            None,
            SERVICE_NAME,
            SERVICE_NAME,
            displayName="ArcFold Monitor Service",
            description="Monitors and restarts ArcFoldService.exe if it is not running.",
            startType=win32service.SERVICE_AUTO_START,
            exeName=module_path
        )
        print(f"Служба {SERVICE_NAME} успешно установлена.")
    except Exception as e:
        print(f"Ошибка при установке службы: {e}")

def uninstall_service():
    """
    Удаляет службу ArcFoldMonitorService.
    """
    try:
        win32serviceutil.RemoveService(SERVICE_NAME)
        print(f"Служба {SERVICE_NAME} успешно удалена.")
    except Exception as e:
        print(f"Ошибка при удалении службы: {e}")

def start_service():
    """
    Запускает службу ArcFoldMonitorService.
    """
    try:
        win32serviceutil.StartService(SERVICE_NAME)
        print(f"Служба {SERVICE_NAME} успешно запущена.")
    except Exception as e:
        print(f"Ошибка при запуске службы: {e}")

def stop_service():
    """
    Останавливает службу ArcFoldMonitorService.
    """
    try:
        win32serviceutil.StopService(SERVICE_NAME)
        print(f"Служба {SERVICE_NAME} успешно остановлена.")
    except Exception as e:
        print(f"Ошибка при остановке службы: {e}")

def service_status():
    """
    Проверяет состояние службы ArcFoldMonitorService.
    """
    try:
        status = win32serviceutil.QueryServiceStatus(SERVICE_NAME)
        if status[1] == win32service.SERVICE_RUNNING:
            print(f"Служба {SERVICE_NAME} запущена.")
        elif status[1] == win32service.SERVICE_STOPPED:
            print(f"Служба {SERVICE_NAME} остановлена.")
        else:
            print(f"Служба {SERVICE_NAME} в состоянии: {status[1]}")
    except Exception as e:
        print(f"Ошибка при проверке состояния службы: {e}")

def is_service_installed():
    """
    Проверяет, установлена ли служба ArcFoldMonitorService.
    """
    try:
        win32serviceutil.QueryServiceStatus(SERVICE_NAME)
        print(f"Служба {SERVICE_NAME} установлена.")
        return True
    except Exception as e:
        print(f"Служба {SERVICE_NAME} не установлена.")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Использование: python ArcFoldServiceManager.py [install|uninstall|start|stop|status|check]")
        sys.exit(1)

    action = sys.argv[1].lower()

    if action == 'install':
        install_service()
    elif action == 'uninstall':
        uninstall_service()
    elif action == 'start':
        start_service()
    elif action == 'stop':
        stop_service()
    elif action == 'status':
        service_status()
    elif action == 'check':
        is_service_installed()
    else:
        print("Неизвестная команда. Используйте install, uninstall, start, stop, status или check.")