from abc import ABC, abstractmethod


class BaseExecutor(ABC):
    """
    Базовый интерфейс исполнителя сделок.

    Реализации:
    - PaperExecutor
    - LiveExecutor
    """


    @abstractmethod
    def open_position(self, *args, **kwargs):
        """
        Открытие позиции.
        """
        pass


    @abstractmethod
    def close_position(
        self,
        price: float,
        reason: str = "Закрытие позиции",
    ):
        """
        Закрытие позиции.
        """
        pass


    @abstractmethod
    def update(
        self,
        price: float,
    ):
        """
        Обновление цены.
        """
        pass


    @property
    @abstractmethod
    def in_position(self):
        """
        Есть ли открытая позиция.
        """
        pass
