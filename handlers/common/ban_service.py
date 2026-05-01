import time
import random

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
            await self.container.logger.adebug(
                "Chat user record already exists in the database. Retrieving info from Redis",
                chat_id=chat_id,
                member_id=member_id,
                content_type=content_type
            )

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
        
        await self.container.logger.adebug(
            "Chat user record created successfully",
            chat_id=chat_id,
            member_id=member_id,
            content_type=content_type
        )
        
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
                await self.container.logger.adebug(
                    "Previous violation data retrieved successfully",
                    chat_id=chat_id,
                    member_id=member_id,
                    duration=data.duration,
                    until=data.until
                )

                return data.duration
            
            await self.container.logger.aerror(
                "Failed to retrieve previous violation data",
                chat_id=chat_id,
                member_id=member_id
            )
        
        return None
    
    def _duration_to_time(self, duration: int) -> int:
        return int(time.time()) + duration
    
    async def _save_violation_data(
        self,
        member_id: int,
        chat_id: int,
        duration: int,
        content_type: str
    ) -> tuple[bool, int | None]:
        """Сохраняет данные о нарушении. Возвращает (успех, до_скольки_секунд)."""
        until = self._duration_to_time(duration)
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
            return False
        
        await self.container.logger.ainfo(
            "New data about user violation saved successfully. Starting ban...",
            chat_id=chat_id,
            member_id=member_id,
            content_type=content_type
        )
        
        return True
    
    async def _perform_ban(
        self,
        member_id: int,
        chat_id: int,
        duration: int,
        content_type: str
    ) -> bool:
        """Выполняет бан в Telegram."""
        processing = await self._set_status(
            member_id, chat_id, Status.PROCESSING, "restrict"
        )
        if not processing:
            return False
        
        try:
            ban_until = self._duration_to_time(duration)

            await self.container.logger.ainfo(
                "Attempting to ban member in Telegram",
                chat_id=chat_id,
                member_id=member_id,
                content_type=content_type,
                current_time=int(time.time()),
                until_timestamp=ban_until,
                difference=ban_until - int(time.time())
            )

            banned = await self.bot.ban_chat_member(
                chat_id, member_id,
                ban_until
            )

            return banned
        except (TelegramBadRequest, Exception) as e:
            await self.container.logger.aerror(
                "Failed to ban member",
                chat_id=chat_id,
                content_type=content_type,
                member=member_id,
                error=str(e),
                until_timestamp=duration
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
            await self.container.logger.aerror(
                "Failed to count join attempt for user after ban",
                chat_id=chat_id,
                member_id=member_id
            )

            await self.bot.send_message(
                chat_id,
                self.container.translator.call("cannot-count-join-attempt")
            )
            return False
        
        await self.container.logger.ainfo(
            "Join attempt counted successfully after ban",
            chat_id=chat_id,
            member_id=member_id,
            total_attempts=attempt
        )
        
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
            await self.container.logger.adebug(
                "Sending violation message is disabled in settings. Skipping sending message...",
                chat_id=chat_id
            )

            return
        
        user = self.container.translator.mention(member_id, member_name)
        duration_msg = self.container.translator.duration(duration)
        
        await self.container.logger.ainfo(
            "Sending violation message to the chat...",
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
            await self.container.logger.adebug(
                "Violation message sent successfully. Shedule deleting message task...",
                chat_id=chat_id,
                member_id=member_id,
                message_id=msg.message_id
            )

            self.container.memory.set(chat_id, msg.message_id)

    async def _delete_message_task(
            self,
            chat_id: int,
            member_id: int
    ) -> bool:
        id = self.container.memory.get(chat_id)

        if not id:
            await self.container.logger.aerror(
                "Message ID was not found on memory. Maybe, the violation message was not sent",
                chat_id=chat_id,
                member_id=member_id
            )
            return False
        
        await self.container.logger.adebug(
            "Scheduling task to delete violation message after ban",
            chat_id=chat_id,
            member_id=member_id,
            message_id=id
        )

        self.container.task_manager.shedule(
            f"delete_msg:{chat_id}:{member_id}",
            lambda: self.bot.delete_message(
                chat_id,
                id
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
        
        if not await self._set_status(
            member_id, chat_id, Status.PENDING, "restrict"
        ):
            return
        
        # 3. Получаем предыдущую длительность и рассчитываем новую (если настройка "Динамическое время бана" включена)
        if await self.container.services.settings.get_has_send_dynamic_violation_time(chat_id):
            await self.container.logger.adebug(
                "Dynamic violation time is enabled. Calculating new ban duration based on previous violation data...",
                chat_id=chat_id,
                member_id=member_id,
                content_type=content_type
            )
            
            prev_duration = await self._get_previous_duration(member_id, chat_id)
            duration = next_ban_duration(prev_duration)

            # 4. Сохраняем данные о нарушении
            success = await self._save_violation_data(
                member_id, chat_id, duration, content_type
            )

            if not success:
                await self._set_status(member_id, chat_id, Status.FAILED, "failed")
                await self.container.logger.aerror(
                    "Failed to save violation data. Aborting ban...",
                    chat_id=chat_id,
                    member_id=member_id,
                    content_type=content_type
                )

                return
        else:
            await self.container.logger.adebug(
                "Dynamic violation time is disabled. Randomly generating ban duration...",
                chat_id=chat_id,
                member_id=member_id,
                content_type=content_type
            )

            duration = random.randint(35, 120)
        
        # 5. Выполняем бан в Telegram
        if not await self._perform_ban(
            member_id, chat_id, duration, content_type
        ):
            # Обработка ошибки
            await self.container.logger.aerror(
                "Failed to ban member in Telegram",
                chat_id=chat_id,
                member_id=member_id,
                content_type=content_type
            )

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
                await self.container.logger.aerror(
                    "Failed to schedule violation message deleting task",
                    chat_id=chat_id,
                    member_id=member_id
                )

                return
            
            await self.container.logger.ainfo(
                "Ban process completed successfully",
                chat_id=chat_id,
                member_id=member_id,
                duration=duration
            )

            self.container.memory.delete(chat_id)
        else:
            await self.container.logger.aerror(
                "Failed to finalize ban process",
                chat_id=chat_id,
                member_id=member_id
            )

            await self._set_status(member_id, chat_id, Status.FAILED, "failed")
            await self.bot.send_message(
                chat_id,
                self.container.translator.call(
                    "failed-to-ban",
                    e="Failed to finalize ban process"
                )
            )
