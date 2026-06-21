import os
import re

# Files to process
files = [
    "templates/base.html",
    "templates/marketplace/home.html",
    "templates/marketplace/register.html",
    "templates/marketplace/login.html",
    "templates/includes/language_switcher.html",
    "templates/marketplace/about_us.html",
    "templates/marketplace/contact.html",
    "templates/marketplace/profile.html"
]

# Comprehensive emoji patterns
emoji_patterns = [
    # Transport emojis
    ('🚗', 'Car'),
    ('🚙', 'Car'),
    ('🚕', 'Car'),
    ('🚘', 'Car'),
    ('🚖', 'Car'),
    ('🚐', 'Car'),
    ('🚌', 'Car'),
    ('🚍', 'Car'),
    ('🚎', 'Car'),
    ('🚓', 'Car'),
    ('🚔', 'Car'),
    ('🚑', 'Car'),
    ('🚒', 'Car'),
    ('🚛', 'Car'),
    ('🚜', 'Car'),
    
    # Other emojis to remove completely
    ('🔍', ''),
    ('⭐', ''),
    ('🌟', ''),
    ('🔥', ''),
    ('💯', ''),
    ('🎯', ''),
    ('🏆', ''),
    ('👑', ''),
    ('💰', ''),
    ('🛒', ''),
    ('✅', ''),
    ('❌', ''),
    ('⚠️', ''),
    ('❗', ''),
    ('❓', ''),
    ('💡', ''),
    ('📌', ''),
    ('📱', ''),
    ('💻', ''),
    ('🖥️', ''),
    ('📷', ''),
    ('🎥', ''),
    ('📹', ''),
    ('🔒', ''),
    ('🔓', ''),
    ('🔑', ''),
    ('❤️', ''),
    ('💔', ''),
    ('👍', ''),
    ('👎', ''),
    ('👏', ''),
    ('🙌', ''),
    ('🤝', ''),
    ('🎉', ''),
    ('🎊', ''),
    ('✨', ''),
    ('🌈', ''),
    ('☀️', ''),
    ('💫', ''),
    ('🔹', ''),
    ('🔸', ''),
    ('▶️', ''),
    ('◀️', ''),
    ('⬆️', ''),
    ('⬇️', ''),
    ('🚀', ''),
    ('📢', ''),
    ('🔔', ''),
    ('💬', ''),
    ('📝', ''),
    ('📄', ''),
    ('📁', ''),
    ('📂', ''),
    ('📅', ''),
    ('📆', ''),
    ('⏰', ''),
    ('⌚', ''),
    ('📞', ''),
    ('📠', ''),
    ('📨', ''),
    ('📩', ''),
]

def remove_emojis(text):
    # Replace specific emojis
    for emoji, replacement in emoji_patterns:
        text = text.replace(emoji, replacement)
    
    # Remove any remaining emoji characters using regex
    # This matches most emoji characters
    emoji_regex = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"  # Enclosed characters
        "]+",
        flags=re.UNICODE
    )
    
    text = emoji_regex.sub('', text)
    return text

# Process each file
for file_path in files:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Show original content length
        original_len = len(content)
        content = remove_emojis(content)
        new_len = len(content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Processed: {file_path} (removed {original_len - new_len} characters)")
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")

print("\n✅ All emojis removed!")