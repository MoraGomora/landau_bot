"""
Модуль управления навигацией и историей переходов между состояниями.
"""
from enum import Enum
from typing import Optional
from dataclasses import dataclass


class NavigationState(str, Enum):
    """Перечисление возможных состояний навигации."""
    MAIN_MENU = "main_menu"
    CHAT_SETTINGS = "chat_settings"
    CHAT_CONFIRM_SETTINGS = "chat_confirm_settings"


@dataclass
class NavigationContext:
    """Контекст для хранения информации о навигации."""
    current_state: NavigationState
    previous_state: Optional[NavigationState] = None
    data: dict = None

    def __post_init__(self):
        if self.data is None:
            self.data = {}

    def to_dict(self) -> dict:
        """Преобразует контекст в словарь для сохранения в FSM."""
        return {
            "current_state": self.current_state.value,
            "previous_state": self.previous_state.value if self.previous_state else None,
            "data": self.data
        }

    @staticmethod
    def from_dict(data: dict) -> "NavigationContext":
        """Создает контекст из словаря."""
        current_state = NavigationState(data.get("current_state", NavigationState.MAIN_MENU.value))
        previous_state_str = data.get("previous_state")
        previous_state = NavigationState(previous_state_str) if previous_state_str else None
        
        return NavigationContext(
            current_state=current_state,
            previous_state=previous_state,
            data=data.get("data", {})
        )


class NavigationService:
    """Сервис для управления навигацией."""

    @staticmethod
    def set_navigation(
        state_data: dict,
        current_state: NavigationState,
        previous_state: Optional[NavigationState] = None,
        extra_data: dict = None
    ) -> None:
        """
        Устанавливает контекст навигации в FSM данные.
        
        Args:
            state_data: Данные FSM контекста
            current_state: Текущее состояние навигации
            previous_state: Предыдущее состояние навигации
            extra_data: Дополнительные данные для сохранения
        """
        nav_context = NavigationContext(
            current_state=current_state,
            previous_state=previous_state,
            data=extra_data or {}
        )
        state_data["navigation"] = nav_context.to_dict()

    @staticmethod
    def get_navigation(state_data: dict) -> NavigationContext:
        """
        Получает контекст навигации из FSM данных.
        
        Args:
            state_data: Данные FSM контекста
            
        Returns:
            NavigationContext: Контекст навигации
        """
        nav_data = state_data.get("navigation")
        if nav_data:
            return NavigationContext.from_dict(nav_data)
        return NavigationContext(current_state=NavigationState.MAIN_MENU)

    @staticmethod
    def update_previous_state(
        state_data: dict,
        previous_state: NavigationState
    ) -> None:
        """
        Обновляет предыдущее состояние в контексте навигации.
        
        Args:
            state_data: Данные FSM контекста
            previous_state: Новое предыдущее состояние
        """
        nav_context = NavigationService.get_navigation(state_data)
        nav_context.previous_state = previous_state
        state_data["navigation"] = nav_context.to_dict()

    @staticmethod
    def get_previous_state(state_data: dict) -> Optional[NavigationState]:
        """Получает предыдущее состояние из контекста навигации."""
        nav_context = NavigationService.get_navigation(state_data)
        return nav_context.previous_state
