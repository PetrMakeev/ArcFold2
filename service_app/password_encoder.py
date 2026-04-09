import os
import base64
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class PasswordEncoder:
    """
    Класс для кодирования и декодирования паролей с использованием 
    имени Windows-компьютера в качестве ключа шифрования
    """
    
    def __init__(self, computer_name: Optional[str] = None):
        """
        Инициализация энкодера
        
        Args:
            computer_name: Опциональное имя компьютера. 
                          Если не указано, будет использовано текущее имя компьютера
        """
        self.computer_name = computer_name or self._get_computer_name()
        self._key = self._create_key_from_computer_name(self.computer_name)
        self._cipher_suite = Fernet(self._key)
    
    @staticmethod
    def _get_computer_name() -> str:
        """Получение имени компьютера Windows"""
        return os.environ.get('COMPUTERNAME', 'DEFAULT_COMPUTER_NAME')
    
    @staticmethod
    def _create_key_from_computer_name(computer_name: str) -> bytes:
        """Создание криптографического ключа из имени компьютера"""
        password = computer_name.encode('utf-8')
        
        # Используем первые 16 байт имени компьютера как соль
        salt = computer_name[:16].encode('utf-8').ljust(16, b'\0')
        
        # Создаем ключ с использованием PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def encode(self, password_string: str) -> str:
        """
        Кодирование строки пароля
        
        Args:
            password_string: Пароль для кодирования
            
        Returns:
            Закодированная строка пароля
        """
        encoded_bytes = self._cipher_suite.encrypt(password_string.encode('utf-8'))
        encoded_string = base64.urlsafe_b64encode(encoded_bytes).decode('utf-8')
        return encoded_string
    
    def decode(self, encoded_password: str) -> str:
        """
        Декодирование строки пароля
        
        Args:
            encoded_password: Закодированный пароль
            
        Returns:
            Декодированный оригинальный пароль
        """
        encrypted_bytes = base64.urlsafe_b64decode(encoded_password.encode('utf-8'))
        decrypted_bytes = self._cipher_suite.decrypt(encrypted_bytes)
        return decrypted_bytes.decode('utf-8')
    
    def get_computer_name_used(self) -> str:
        """Получение имени компьютера, использованного для создания ключа"""
        return self.computer_name


# # Пример использования:
# if __name__ == "__main__":
#     # Создание экземпляра энкодера
#     encoder = PasswordEncoder()
    
#     # Тестовый пароль
#     original_password = "my_secret_password_123"
    
#     print(f"Имя компьютера: {encoder.get_computer_name_used()}")
#     print(f"Оригинальный пароль: {original_password}")
    
#     # Кодируем пароль
#     encoded = encoder.encode(original_password)
#     print(f"Закодированный пароль: {encoded}")
    
#     # Декодируем пароль
#     decoded = encoder.decode(encoded)
#     print(f"Декодированный пароль: {decoded}")
    
    # # Проверяем, что все работает правильно
    # print(f"Совпадают: {original_password == decoded}")