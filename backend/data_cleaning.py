from utils02 import *

DISCORD_SERVER_ID = os.getenv('DISCORD_SERVER_ID')

filepath = '../data' #### Update if needed
filename_raw = f'{DISCORD_SERVER_ID}_selected_channels_messages.json' #### Update if needed
filename_cleaned = 'Discord_all_messages_cleaned'
messages = load_json(filename_raw, filepath)
filtered_messages = filter_messages(messages)
save_to_json(filtered_messages, filename=filename_cleaned, path=filepath)