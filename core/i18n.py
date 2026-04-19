import html

from fluent.runtime import FluentLocalization

from models import BanTime


class Translator:

    def __init__(self, l10n: FluentLocalization) -> None:
        self.l10n = l10n

    def _split_duration(self, seconds: int) -> BanTime:
        hours = seconds // 3600
        seconds %= 3600

        minutes = seconds // 60
        seconds %= 60

        return BanTime(
            hours=hours,
            minutes=minutes,
            seconds=seconds
        )

    def duration(self, seconds: int) -> str:
        parts = self._split_duration(seconds)
        result = []
        
        if parts.hours:
            result.append(self.call("duration-hours", **parts.model_dump(mode="json")))
        if parts.minutes:
            result.append(self.call("duration-minutes", **parts.model_dump(mode="json")))
        if parts.seconds:
            result.append(self.call("duration-seconds", **parts.model_dump(mode="json")))
        return " ".join(result)

    def mention(self, user_id: int, name: str):
        safe_name = html.escape(name)
        return f'<a href="tg://user?id={user_id}">{safe_name}</a>'

    def call(self, key: str, **kwargs) -> str:
        return self.l10n.format_value(key, kwargs)