from core.container import AppContainer


def get_status_label(container: AppContainer, is_enabled: bool) -> str:
    """Возвращает локализованный статус (включено/отключено)."""
    return container.translator.call("on" if is_enabled else "off")