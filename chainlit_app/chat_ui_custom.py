# UI customization
@cl.on_ui_update
async def update_ui():
    # Update header settings
    await cl.update_header(
        title="FreelanceX AI Assistant",
        logo="🤖",
        favicon="🤖"
    )
    
    # Configure chat settings
    await cl.update_chat_settings(
        dark_mode=True,
        chat_position="center",
        collapsed_sidebar=False
    )

    # Configure message settings
    await cl.update_message_settings(
        avatar_shape="circle",
        enable_copy_button=True,
        show_time=True
    )
