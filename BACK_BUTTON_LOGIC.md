# Универсальная логика для кнопки Back

## Описание

Реализована универсальная система навигации для кнопки "Back" (Назад), которая автоматически отслеживает историю переходов между состояниями и позволяет пользователю вернуться к предыдущему меню.

## Архитектура

### 1. Сервис навигации (`navigation.py`)

Модуль содержит три основных компонента:

- **NavigationState** - Enum со всеми возможными состояниями навигации:
  - `MAIN_MENU` - главное меню
  - `CHAT_SETTINGS` - выбор чата для настроек
  - `CHAT_CONFIRM_SETTINGS` - меню настроек выбранного чата

- **NavigationContext** - хранит информацию о текущей навигации:
  - `current_state` - текущее состояние
  - `previous_state` - предыдущее состояние
  - `data` - дополнительные данные (например, ID чата)

- **NavigationService** - сервис для управления навигацией:
  - `set_navigation()` - устанавливает контекст навигации в FSM
  - `get_navigation()` - получает контекст из FSM
  - `update_previous_state()` - обновляет предыдущее состояние
  - `get_previous_state()` - получает предыдущее состояние

### 2. Универсальный обработчик Back (`back.py`)

Обработчик кнопки "Back" теперь:

1. Удаляет текущее сообщение
2. Получает контекст навигации из FSM
3. В зависимости от предыдущего состояния показывает соответствующее меню:
   - Если `previous_state == MAIN_MENU` → показывает главное меню и очищает состояние
   - Если `previous_state == CHAT_SETTINGS` → показывает меню выбора чата
   - Если `previous_state == CHAT_CONFIRM_SETTINGS` → показывает меню настроек

### 3. Обновленные обработчики

Все обработчики (start.py, choose_chat.py, settings.py) теперь:

1. Используют `NavigationService` для установки контекста навигации при переходе между меню
2. Добавляют кнопку "Back" в клавиатуру (используя `is_back=True` параметр)
3. Сохраняют необходимые данные в FSM для восстановления состояния при нажатии Back

## Поток навигации

```
/start → Главное меню (MAIN_MENU)
  ↓
"Settings" → Выбор чата (CHAT_SETTINGS, previous_state = MAIN_MENU)
  ↓
Выбрать чат → Меню настроек (CHAT_CONFIRM_SETTINGS, previous_state = CHAT_SETTINGS)
  ↓ (Back)
Вернуться → Выбор чата (CHAT_SETTINGS, previous_state = MAIN_MENU)
  ↓ (Back)
Вернуться → Главное меню (MAIN_MENU)
```

## Использование в новых обработчиках

Для добавления нового меню с поддержкой Back:

1. Добавьте новое состояние в `NavigationState` enum:
   ```python
   NEW_STATE = "new_state"
   ```

2. При переходе в новое состояние используйте:
   ```python
   data = await state.get_data()
   NavigationService.set_navigation(
       data,
       current_state=NavigationState.NEW_STATE,
       previous_state=NavigationState.PREVIOUS_STATE,
       extra_data={"key": "value"}  # опционально
   )
   await state.update_data(**data)
   ```

3. Добавьте кнопку Back в клавиатуру:
   ```python
   get_some_keyboard(
       is_back=True,
       back_text=container.translator.call("back-btn")
   )
   ```

## Преимущества

- ✅ Единый механизм навигации для всех меню
- ✅ Автоматическое отслеживание истории переходов
- ✅ Простое добавление новых состояний и переходов
- ✅ Восстановление данных при возврате назад
- ✅ Поддержка логирования навигации
- ✅ Обработка ошибок и исключений

## Заключение

Модуль был создан с помощью **Copilot**
