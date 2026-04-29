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
    <b>💬 Select the chat you want to customize:</b>

choose-setting =
    <b>⚙️ Select the setting you are interested in:</b>

    <i>NOTE: When the "Dynamic ban time" setting is disabled, the ban time is generated randomly from 30 seconds to 2 minutes</i>

on = ✔️ On
off = ✘ Off

send-violation-msg =
    📨 Sending a ban message: { $violation_status }
    
turn-dynamic-violation-msg =
    ⏱️ Dynamic ban time: { $dynamic_violation_status }

current-setting-status =
    <b>📌 Current setting status for the chat <i>{ $chat_name }</i></b>
    Status: <code>{ $status }</code>

    <i>✅ All data is saved automatically</i>

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
    <i>Something went wrong. Please try again later.</i>

error-permission =
    <b>🚫 Access Denied</b>
    You don't have permission to use this command.

chats-not-found =
    <b>🔍 Chats not found</b>
    <i>Most likely, you did not add the bot to your chat.</i>

## Confirmation
confirm-yes = ✅ Confirm
confirm-no = ❌ Cancel
confirm-prompt = <b>❓ Are you sure you want to proceed?</b>

settings-btn = ⚙️ Settings
support-btn = 🆘 Bot support
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
    <b>🚫 Hello, { $user }.</b> You have been removed from the group because <i>this chat is used only for comments.</i>
    <b>⚠️ Please do not join this chat or add anyone else.</b> Please only comment on posts. Otherwise, the time limit will increase with each attempt to enter (if the group owner has not disabled this setting).
    <b>⏰ The limit will be lifted in</b> <code>{ $duration_msg }</code>

failed-to-ban =
    <b>⚠️ Failed to ban user</b>
    <i>Reason (from Telegram):</i> <code>{ e }</code>

cannot-get-owner =
    <b>⚠️ Failed to get group owner</b>

data-not-saved =
    <b>💾 Failed to save/create chat settings</b>

cannot-count-join-attempt =
    Failed to count attempt to join group

status-was-not-updated =
    Failed to update status

## Restriction notifications in private messages

restriction-notification-title =
    <b>🚫 Restriction Notification</b>

restriction-notification =
    <b>🚫 Hello, { $user }!</b> You have received a restriction in the chat <b>{ $chat_name }</b>.
    
    <b>📋 Restriction Details:</b>
    • <b>Restriction will be lifted in:</b> <code>{ $duration_msg }</code>
    • <b>Administrator:</b> { $admin }
    • <b>Reason:</b> <i>{ $reason }</i>
    
    <b>⚠️ Important:</b> Repeated violations may result in increased restriction time.

restriction-notification-no-admin =
    <b>🚫 Hello, { $user }!</b> You have received a restriction in the chat <b>{ $chat_name }</b>.
    
    <b>📋 Restriction Details:</b>
    • <b>Restriction will be lifted in:</b> <code>{ $duration_msg }</code>
    • <b>Reason:</b> <i>{ $reason }</i>
    
    <b>⚠️ Important:</b> Repeated violations may result in increased restriction time.

reason =
    Entering the chat or inviting other participants to it is prohibited.

not = No