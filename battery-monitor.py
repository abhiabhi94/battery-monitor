import subprocess as s
import re
from time import sleep
import sys
import os
import json

COMMAND = 'acpi'
INTERVAL = 1
# BASE_DIR = BASE_DIR = os.path.dirname(
#     os.path.dirname(os.path.abspath(__file__)))
CURRENT_DIR = os.getcwd()
DATA_FILE = 'data.json'
COMMAND_FILE = 'cmd.txt'
FILE_DATA = os.path.join(CURRENT_DIR, DATA_FILE)
FILE_COMMAND = os.path.join(CURRENT_DIR, COMMAND_FILE)
STARTUP_CMD = os.path.join(CURRENT_DIR, __file__)
# Extracts the first three characters from the version output e.g 3.5
PY_VERSION = sys.version[:3]
try:
    with open(FILE_COMMAND, 'r') as f:
        pass
except FileNotFoundError:
    with open(FILE_COMMAND, 'w') as f:
        # f.write(f'python{PY_VERSION} {FILE_COMMAND}')
        f.write('python{} {}'.format(PY_VERSION, STARTUP_CMD))

last_state = None
last_status = None
state = {}
status = {}
# state['change'] = False
# status['change'] = False


# def has_changed(current_val):
#     global state, status
#     status = state if type(current_val) == 'str' else status
#     print(status)
#     if status['change']:
#         status['change'] = not status['change']
#         return True
#     status['change'] =
#     print(status)
#     return False


def has_state_changed(current_state):
    global last_state
    # print(current_state, last_state)
    if current_state != last_state:
        last_state = current_state
        # notify(notification)
        return True
    last_state = current_state
    # print(current_state, last_state)
    return False


def has_status_changed(current_status):
    global last_status
    # print(current_status, last_status)
    if current_status != last_status:
        last_status = current_status
        return True
    last_status = current_status
    # print(current_status, last_state)
    return False


def is_status_requested(status):
    if status in notify_status:
        return True
    return False


def notify(msg):
    s.call(['notify-send', 'Battery Monitor', msg])
    # s.call(['spd-say', 'We are done'])


def get_battery_info(INTERVAL):
    output = s.check_output(COMMAND.split()).decode('utf-8')
    status = int(re.search(r'\d{1,3}%', output).group(0)[:-1])
    print(output)
    if 'Full' in output:
        if has_state_changed('Charging'):
            notify('Battery full')
        return None
    else:
        try:
            time_left = re.search(r'\d{0,2}:\d{0,2}:\d{0,2}', output).group(0)
        except AttributeError:
            time_left = "Rate couldn't be determined"
        if 'Charging' in output:
            state = 'Charging'
            dest = 'until full'
        else:
            state = 'Discharging'
            dest = 'remaining'

    return state, status, time_left, dest


def run_job(notify_status):
    while True:
        result = get_battery_info(INTERVAL)
        if result:
            state['val'], status['val'], time_left, dest = result
            # notification = f'Battery {state['val']}, {status['val']}%, {time_left} {dest}'
            notification = 'Battery {}, {}%, {} {}'.format(
                state['val'], status['val'], time_left, dest)
            if has_state_changed(state['val']) or (status['val'] in notify_status and has_status_changed(status['val'])):
                # if has_changed(state['val']) or (status['val'] in notify_status and has_changed(status['val'])):
                notify(notification)
        sleep(INTERVAL)


if __name__ == "__main__":
    try:
        with open(FILE_DATA, 'r') as f:
            content = json.load(f)
            # sys.exit(content)
            notify_status = content['notify_values']
    except FileNotFoundError:
        with open(FILE_DATA, 'w', encoding='utf-8') as f:
            notify_status = [int(i) for i in sys.argv[1:]]
            if False in [False for i in notify_status if i < 0 or i > 100]:
                sys.exit('Percentages should be between 0 and 100')
            if not notify_status:
                notify_status = [50, 30, 10, 5]
            notify_values = {}
            notify_values['notify_values'] = notify_status
            json.dump(notify_values, f, ensure_ascii=False, indent=4)
    except ValueError:
        print('Please give percentages when you want notifications as arguments in integer format separated by space')

    print("You will get notified when your battery percentage is: ", notify_status)
    run_job(notify_status)
