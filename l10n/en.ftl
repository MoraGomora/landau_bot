## General messages
hello-msg =
    <b>👋 Hello!</b>
    Welcome to the bot. Use /help to see available commands.

hello-owner =
    <b>👊 Hello, owner!</b>
    You have full access to bot administration.

help-msg =
    <b>📚 Available commands:</b>
    
    /start - Start the bot
    /help - Show this message

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

## Confirmation
confirm-yes = ✅ Confirm
confirm-no = ❌ Cancel
confirm-prompt = Are you sure you want to proceed?

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
