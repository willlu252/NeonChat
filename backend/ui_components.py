# ui_components.py
# Contains functions for rendering specific UI parts like chat messages

import streamlit as st
import os
from PIL import Image # Import PIL for image handling
import base64 # For potential inline image display if needed

def render_message(msg, idx):
    """Renders a single chat message in a structured container."""
    role = msg.get('role', 'unknown')
    content = msg.get('content', '')
    msg_type = msg.get('type', 'text')
    avatar = "🧑" if role == "user" else "🤖"
    prompt_for_image = msg.get('prompt', '') # Get prompt if it's an image message

    # Use st.chat_message for built-in styling
    with st.chat_message(name=role, avatar=avatar): # Use name parameter for role
        # Render content based on type
        if msg_type == 'text':
            st.markdown(content) # Streamlit handles markdown rendering well

        elif msg_type == 'image':
            image_path = msg.get('image_path', content if isinstance(content, str) else None)
            # Add context text if it's a user message with an image path
            if role == 'user' and isinstance(content, str) and content != image_path:
                 st.markdown(content) # Display the text part of the user message

            if image_path and os.path.exists(image_path):
                try:
                    # Display the actual image with a more compact size
                    st.image(image_path, caption=f"Prompt: {prompt_for_image}" if prompt_for_image else None, width=400)
                    # Add download button for the generated image
                    if role == 'assistant': # Only show download for generated images
                        with open(image_path, "rb") as file:
                            st.download_button(
                                label="💾 Download Image",
                                data=file,
                                file_name=f"generated_image_{idx}.png",
                                mime="image/png",
                                key=f"download_img_btn_{idx}"
                            )
                except Exception as e:
                    st.error(f"Error displaying image {image_path}: {e}")
            elif role == 'assistant': # If assistant response is image type but path invalid
                st.warning(f"Image file not found or path invalid: {image_path}")
                if isinstance(content, str) and content != image_path: # Show error text if available
                     st.text(content)


        elif msg_type == 'audio':
            st.markdown("**Audio Generation Result:**")
            st.info("(Audio placeholder)") # Placeholder
            # In a real implementation, you might use st.audio(audio_bytes_or_path)
            st.text(content) # Show placeholder text

        elif msg_type == 'video':
            st.markdown("**Video Generation Result:**")
            st.info("(Video placeholder)") # Placeholder
            # In a real implementation, you might use st.video(video_bytes_or_path)
            st.text(content) # Show placeholder text

        else:
            # Fallback for unknown types or user messages that might have a type
            # but aren't image type
            if role != 'user' or msg_type != 'image':
                 st.markdown(content)

# Note: Clipboard functionality is omitted for simplicity in this version.
# Libraries like streamlit-copy-to-clipboard can be added if needed.
