from aiogram import Router
from aiogram.types import ChatMemberUpdated, ChatMemberOwner
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import ChatMemberUpdatedFilter, JOIN_TRANSITION, LEAVE_TRANSITION

from core.container import AppContainer


router = Router(name="bot_lifecycle")


async def update_dialog(
    status: bool,
    update: ChatMemberUpdated,
    container: AppContainer
) -> None:
    result = await container.services.settings.change_has_chat_dialog(
        update.chat.id,
        status
    )
    if not result:
        await container.logger.aerror(
            "Failed to change \"has_dialog_status\" value for this chat. Settings not found",
            chat_id=update.chat.id
        )
        return
    
    await container.logger.ainfo(
        "\"has_chat_dialog\" for chat changed successfully",
        chat_id=update.chat.id,
        new_value=result.has_chat_dialog
    )


@router.my_chat_member(
    ChatMemberUpdatedFilter(JOIN_TRANSITION)
)
async def bot_join(
    update: ChatMemberUpdated, container: AppContainer
) -> None:
    await container.logger.ainfo(
        "Bot entered to the chat by user",
        chat_id=update.chat.id,
        user_id=update.from_user.id
    )

    if await container.services.settings.is_available(update.chat.id):
        await update_dialog(True, update, container)
        return

    try:
        admins = await update.bot.get_chat_administrators(update.chat.id)
        owner = next(m for m in admins if isinstance(m, ChatMemberOwner))

        if not owner:
            await container.logger.aerror(
                "\"Owner\" object is empty. Maybe, owner of this chat is in anonymous mode",
                chat_id=update.chat.id
            )
            await update.answer(
                container.translator.call(
                    "cannot-get-owner"
                )
            )
            return
        
        # created = await container.services.chat_owner.create_or_update(
        #     owner.user.id,
        #     update.chat.id,
        #     update.chat.id
        # )
        # if not created:
        #     return
        
        # await container.logger.ainfo(
        #     "Chat owner record created successfully",
        #     chat_id=update.chat.id,
        #     owner_id=owner.user.id,
        #     owner_full_name=owner.user.full_name
        # )

        result = await container.services.settings.create(
            chat_id=update.chat.id,
            chat_name=update.chat.full_name,
            owner_id=owner.user.id
        )

        if not result:
            await container.logger.ainfo(
                "Settings for this chat is available",
                chat_id=update.chat.id
            )
            return
        
        await container.logger.ainfo(
            "Settings for this chat created successfully. Creating chat owner record...",
            chat_id=update.chat.id
        )
    except TelegramBadRequest as e:
        await container.logger.aerror(
            "Failed to check admins in chat",
            chat_id=update.chat.id,
            error=str(e)
        )
        return
    

@router.my_chat_member(
    ChatMemberUpdatedFilter(LEAVE_TRANSITION)
)
async def bot_leave(
    update: ChatMemberUpdated, container: AppContainer
) -> None:
    await container.logger.ainfo(
        "Bot was kicked or leave from chat",
        chat_id=update.chat.id
    )

    await update_dialog(False, update, container)