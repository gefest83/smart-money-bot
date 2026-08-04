from abc import ABC, abstractmethod


class BaseExecutor(ABC):
    """
    Базовый интерфейс исполнителя сделок.

    Реализации:
    - PaperExecutor
    - LiveExecutor
    """


    @abstractmethod
    def open_position(
        self,
        signal,
        amount: float,
    ):
        """
        Открытие позиции.
        """
        pass


    @abstractmethod
    def close_position(
        self,
        price: float,
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