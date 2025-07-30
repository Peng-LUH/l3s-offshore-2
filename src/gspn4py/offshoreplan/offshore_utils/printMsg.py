import datetime

def printMsg(text, loglevel=0):
    target_log_level = 1

    if loglevel <= target_log_level:
        current_time = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
        print(f"[{current_time}] {text}")

# Example usage:
# print_msg("Hello, World!", is_debug=True)
