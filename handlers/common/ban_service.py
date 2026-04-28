import time
import random
from datetime import datetime

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

from core.container import AppContainer
from models import Violation
from enums import Status
from .utils import next_ban_duration, today


class BanService:
    """Сервис для управления баном пользователей в чате."""
    
    def __init__(self, bot: Bot, container: AppContainer):
        self.bot = bot
        self.container = container
    
    async def _ensure_chat_user(
        self,
        member_id: int,
        member_name: str,
        chat_id: int,
        content_type: str
    ) -> bool:
        """Проверяет наличие пользователя, создаёт если нужно."""
        if await self.container.services.chat_user.is_available(member_id, chat_id):
            return True
        
        created = await self.container.services.chat_user.create(
            member_id,
            member_name,
            chat_id
        )
        
        if not created:
            await self.container.logger.aerror(
                "Failed to create chat user",
                chat_id=chat_id,
                member_id=member_id,
                content_type=content_type
            )
            return False
        
        return True
    
    async def _set_status(
        self,
        member_id: int,
        chat_id: int,
        status: Status,
        operation: str
    ) -> bool:
        """Устанавливает статус с логированием ошибок."""
        result = await self.container.services.chat_user.set_status(
            member_id,
            chat_id,
            status
        )
        
        if not result:
            await self.container.logger.aerror(
                f"Failed to set status for member {operation} in the chat",
                chat_id=chat_id,
                member_id=member_id
            )
            await self.bot.send_message(
                chat_id,
                self.container.translator.call("status-was-not-updated")
            )
        
        return result
    
    async def _get_previous_duration(
        self,
        member_id: int,
        chat_id: int
    ) -> int | None:
        """Получает предыдущую длительность бана."""
        if await self.container.services.chat_user.has_violation(
            member_id, chat_id, today()
        ):
            data = await self.container.services.chat_user.get_violation_data(
                member_id,
                chat_id,
                today()
            )
            if data:
                return data.duration
        
        return None
    
    async def _save_violation_data(
        self,
        member_id: int,
        chat_id: int,
        duration: int,
        content_type: str
    ) -> tuple[bool, int]:
        """Сохраняет данные о нарушении. Возвращает (успех, до_скольки_секунд)."""
        until = int(time.time()) + duration
        violation = Violation(duration=duration, until=until)
        
        result = await self.container.services.chat_user.set_violation_data(
            member_id,
            chat_id,
            today(),
            violation
        )
        
        if not result:
            await self.container.logger.aerror(
                "Failed to write a new data about user",
                chat_id=chat_id,
                member_id=member_id,
                content_type=content_type
            )
            return False, 0
        
        await self.container.logger.ainfo(
            "New data about user violation saved successfully. Starting ban...",
            chat_id=chat_id,
            member_id=member_id,
            content_type=content_type
        )
        
        return True, until
    
    async def _perform_ban(
        self,
        member_id: int,
        chat_id: int,
        until: int,
        content_type: str
    ) -> bool:
        """Выполняет бан в Telegram."""
        processing = await self._set_status(
            member_id, chat_id, Status.PROCESSING, "restrict"
        )
        if not processing:
            return False
        
        try:
            banned = await self.bot.ban_chat_member(
                chat_id, member_id,
                datetime.fromtimestamp(until)
            )
            return bool(banned)
        
        except TelegramBadRequest as e:
            await self.container.logger.aerror(
                "Failed to ban member",
                chat_id=chat_id,
                content_type=content_type,
                member=member_id,
                error=str(e)
            )
            return False
    
    async def _finalize_ban(
        self,
        member_id: int,
        chat_id: int,
        member_name: str,
        duration: int
    ) -> bool:
        """Завершает бан: добавляет попытку входа, отправляет сообщение."""
        counting = await self._set_status(
            member_id, chat_id, Status.COUNTING, "counting"
        )
        if not counting:
            return False
        
        # Добавляем попытку входа
        attempt = await self.container.services.chat_user.add_join_attempt(
            member_id, chat_id
        )
        if not attempt:
            await self.bot.send_message(
                chat_id,
                self.container.translator.call("cannot-count-join-attempt")
            )
            return False
        
        # Устанавливаем статус DONE
        done = await self._set_status(member_id, chat_id, Status.DONE, "done")
        if not done:
            return False
        
        # Отправляем сообщение о нарушении
        await self._send_violation_message(
            chat_id, member_id, member_name, duration
        )
        
        return True
    
    async def _send_violation_message(
        self,
        chat_id: int,
        member_id: int,
        member_name: str,
        duration: int
    ) -> None:
        """Отправляет сообщение о нарушении в чат."""
        if not await self.container.services.settings.get_has_send_violation_msg(
            chat_id
        ):
            return
        
        user = self.container.translator.mention(member_id, member_name)
        duration_msg = self.container.translator.duration(duration)
        
        await self.container.logger.ainfo(
            "Member banned successfully. Counting join attempts...",
            chat_id=chat_id,
            member=member_id
        )
        
        msg = await self.bot.send_message(
            chat_id,
            self.container.translator.call(
                "violation-msg",
                user=user,
                duration_msg=duration_msg
            )
        )
        
        if msg:
            self.container.memory.set(chat_id, msg.message_id)

    async def _delete_message_task(
            self,
            chat_id: int,
            member_id: int
    ) -> bool:
        if not self.container.memory.get(chat_id):
            await self.container.logger.aerror(
                "Message ID was not found on memory. Maybe, the violation message was not sent",
                chat_id=chat_id,
                member_id=member_id
            )
            return False
        
        ids = self.container.memory.get(chat_id)
        
        self.container.task_manager.shedule(
            f"delete_msg:{chat_id}:{member_id}",
            lambda: self.bot.delete_message(
                chat_id,
                ids
            ),
            30
        )
            
        await self.container.logger.adebug(
            "Deleting violation message task created successfully for user in the chat",
            chat_id=chat_id,
            member_id=member_id
        )

        return True
    
    async def ban_member(
        self,
        chat_id: int,
        member_id: int,
        member_name: str,
        content_type: str
    ) -> None:
        """Основной метод банирования пользователя."""
        
        # 1. Проверяем/создаём пользователя
        await self.container.logger.adebug(
            "Getting info about user from Redis",
            chat_id=chat_id,
            member_id=member_id,
            content_type=content_type
        )
        
        if not await self._ensure_chat_user(
            member_id, member_name, chat_id, content_type
        ):
            return
        
        # 2. Устанавливаем статус PENDING
        if not await self._set_status(
            member_id, chat_id, Status.PENDING, "restrict"
        ):
            return
        
        # 3. Получаем предыдущую длительность и рассчитываем новую (если настройка "Динамическое время бана" включена)
        if await self.container.services.settings.get_has_send_dynamic_violation_time(chat_id):
            prev_duration = await self._get_previous_duration(member_id, chat_id)
            duration = next_ban_duration(prev_duration)
        else:
            duration = random.randint(30, 120)
        
        # 4. Сохраняем данные о нарушении
        success, until = await self._save_violation_data(
            member_id, chat_id, duration, content_type
        )
        if not success:
            return
        
        # 5. Выполняем бан в Telegram
        if not await self._perform_ban(
            member_id, chat_id, until, content_type
        ):
            # Обработка ошибки
            await self._set_status(member_id, chat_id, Status.FAILED, "failed")
            await self.bot.send_message(
                chat_id,
                self.container.translator.call(
                    "failed-to-ban",
                    e="Telegram error"
                )
            )
            return
        
        # 6. Завершаем бан
        finalized = await self._finalize_ban(member_id, chat_id, member_name, duration)
        if finalized:
            result = await self._delete_message_task(chat_id, member_id)

            if not result:
                return
            
            self.container.memory.delete(chat_id)
