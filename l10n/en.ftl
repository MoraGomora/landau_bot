## General messages
hello-msg =
    <b>👋 Hello! Welcome to the bot.</b>
    Here you can see your restrictions in chats where the bot is present, as well as configure the bot for your chats.
    Below, you can select the item you're interested in.

    Select what interests you:

hello-owner =
    <b>👊 Hello, owner!</b>
    You have full access to bot administration.

choose-chat =
    Select the chat you want to customize:

choose-setting =
    Select the setting you are interested in:

on = On
off = Off

send-violation-msg =
    Sending a ban message: { $violation_status }
    
turn-dynamic-violation-msg =
    Dynamic ban time: { $dynamic_violation_status }

current-setting-status =
    The current status of this setting is: { $status }

    <i>All data is saved automatically</i>

## Admin messages
ping-msg =
    <b>🏓 Pong!</b>
    Bot is up and running.

stats-msg =
    <b>📊 Bot Statistics</b>
    <b>Status</b>: 🟢 Online
    <b>PC Specs</b>: sh*t (<tg-spoiler><i>just kidding ha ha</i></tg-spoiler>)

## Media messages
media-msg =
    <b>🫡 Nice media!</b>
    Thanks for sharing.

## Error messages
error-generic =
    <b>❌ Error</b>
    Something went wrong. Please try again later.

error-permission =
    <b>🚫 Access Denied</b>
    You don't have permission to use this command.

chats-not-found =
    Your chats were not found. Most likely, you did not add the bot to your chat.

## Confirmation
confirm-yes = ✅ Confirm
confirm-no = ❌ Cancel
confirm-prompt = Are you sure you want to proceed?

settings-btn = Settings
support-btn = Bot support
back-btn = ⬅️ Back

duration-hours =
    { $hours ->
        [one] { $hours } hour
       *[other] { $hours } hours
    }

duration-minutes =
    { $minutes ->
        [one] { $minutes } minute
       *[other] { $minutes } minutes
    }

duration-seconds =
    { $seconds ->
        [one] { $seconds } second
       *[other] { $seconds } seconds
    }

violation-msg =
    Hello, { $user }. You have been removed from the group because this chat is used only for comments.
    Please do not join this chat or add anyone else. Please only comment on posts. Otherwise, the time limit will increase with each attempt to enter.
    The limit will be lifted in { $duration_msg }

failed-to-ban =
    Failed to ban user. Reason (from Telegram): { e }

cannot-get-owner =
    Failed to get group owner

data-not-saved =
    Failed to save/create chat settings

cannot-count-join-attempt =
    Failed to count attempt to join group

status-was-not-updated =
    Failed to update status