from enum import Enum
from datetime import datetime
from collections import Counter
from dataclasses import dataclass


class ProductStatus(Enum):
    WAITING = "Ожидает проверки"
    VERIFIED = "Проверен ✅"
    FAILED = "Не прошел проверку ❌"
    EXPIRED = "Время проверки истекло ⏰"


@dataclass
class BasketItem:
    product_name: str
    status: ProductStatus = ProductStatus.WAITING
    verified_at: datetime | None = None
    verification_attempts: int = 0


class Basket:

    def __init__(self):
        self.items: list[BasketItem] = []
        self.current_item: BasketItem | None = None

    def add_item(self, product_name: str) -> None:
        """Добавление товара (имитация сканирования штрих-кода)

        :param str product_name: Назваие товара
        """
        item = BasketItem(product_name)
        self.items.append(item)
        self.current_item = item

    def verify_current_item(self) -> bool:
        """Подтверждение проверки текущего товара.

        :return bool: True, если подтверждение успешно, иначе - False
        """
        if not self.current_item:
            return False

        self.current_item.status = ProductStatus.VERIFIED
        self.current_item.verified_at = datetime.now()
        self.current_item = None

        return True

    def fail_current_item(self) -> None:
        """Обработка товара, не прошедшего проверку."""
        if not self.current_item:
            return

        self.current_item.verification_attempts += 1
        if self.current_item.verification_attempts >= 3:
            self.current_item.status = ProductStatus.FAILED
            self.current_item = None

    def get_verified_counts(self) -> Counter:
        """Возвращает количество проверенных товаров каждого типа.

        :return Counter: объект Counter, количество проверенных товаров каждого типа
        """
        verified_items = [item.product_name for item in self.items if item.status == ProductStatus.VERIFIED]
        return Counter(verified_items)
