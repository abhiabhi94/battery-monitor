import subprocess as s
import re
from time import sleep
import sys
import argparse
import os
import json

COMMAND = 'acpi'
INTERVAL = 1  # the time for which the function stops

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(BASE_DIR, 'data.json')
CMD_FILE = os.path.join(BASE_DIR, 'cmd.txt')
SOUND_FILE = os.path.join(BASE_DIR, os.path.join('sounds', 'beep4.wav'))
STARTUP_CMD = os.path.join(BASE_DIR, __file__)

# Extracts the first three characters from the version output e.g 3.5
PY_VERSION = sys.version[:3]

try:
    with open(CMD_FILE, 'r') as cmd_file:
        pass
except FileNotFoundError:
    with open(CMD_FILE, 'w') as cmd_file:
        # f.write(f'python{PY_VERSION} {CMD_FILE}')
        cmd_file.write('python{} {}'.format(PY_VERSION, STARTUP_CMD))

DEFAULT_STATUS = [50, 30, 10, 5]
BATTERY_VALS = 'battery-values'
SOUND = 'sound'

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
    """
    Returns
        A boolean specifying whether state has changed or not

    Params
        current_state: str
            The current state of battery(charging/discharging)
    """
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
    """
    Returns
        A boolean depending upon whether status has changed or not from the last one

    Params
        current_status: int
            The current status of charging(e.g 40 or 30)
    """
    global last_status
    # print(current_status, last_status)
    if current_status != last_status:
        last_status = current_status
        return True
    last_status = current_status
    # print(current_status, last_state)
    return False


def notify(msg, sound_flag):
    """
    Sends a notification to the desktop
    Returns
        None

    Params
        msg: str
            The text which will be displayed in the notification bar.
        sound_flag : bool
            Whether sound has to been played alongside visual notification.
    """
    s.call(['notify-send', 'Battery Monitor', msg])
    if sound_flag:
        s.call(['paplay', SOUND_FILE])
    # s.call(['spd-say', 'We are done'])


def get_battery_info(sound_flag):
    """
    Returns
        A tuple stating the following information about the battery:
            state: Charging/Discharging
            status: % by which the battery is charged.
            time_left: Time required to charge/discharge fully
            dest: untill full/remaining

    Params
        sound_flag: bool
            Whether sound has to be played alongside visual notification.

    """
    output = s.check_output(COMMAND.split()).decode('utf-8')
    status = int(re.search(r'\d{1,3}%', output).group(0)[:-1])
    # print(output)
    if 'Full' in output:
        if has_state_changed('Charging'):
            notify('Battery full', sound_flag)
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


def run_job(notify_status, sound_flag):
    """
    Runs the job for notifying the information about battery
    Returns
        None

    Params:
        notify_status: list
            The list containing integer values for which notification will be given.
        sound_flag: bool
            Whether sound is asked alongwith visual notification.
    """
    while True:
        result = get_battery_info(sound_flag)
        if result:
            state['val'], status['val'], time_left, dest = result
            # notification = f'Battery {state['val']}, {status['val']}%, {time_left} {dest}'
            notification = 'Battery {}, {}%, {} {}'.format(
                state['val'], status['val'], time_left, dest)
            if has_state_changed(state['val']) or (status['val'] in notify_status and has_status_changed(status['val'])):
                # if has_changed(state['val']) or (status['val'] in notify_status and has_changed(status['val'])):
                notify(notification, sound_flag)
        sleep(INTERVAL)


def main():
    """
    Does the prepocessing to write arguments if given or load contents of a pre-saved file
    Run the job

    Returns
        None
    """
    try:
        with open(DATA_FILE, 'r') as data_file:
            content = json.load(data_file)
            # sys.exit(content)
            notify_status = content[BATTERY_VALS]
            sound_flag = content[SOUND]

    except FileNotFoundError:
        # This part will be executed when running for the first time
        # if correct arguments are passed

        parser = argparse.ArgumentParser(description=f"""
        Notify me at the when the battery reaches certain stages or 
        when a charger is plugged or unplugged
        \nBy default: you will get notification when the battery reaches the percentages
        {DEFAULT_STATUS} alongwith no sound.
        \nExample:
        If you want default options,
        use:    python3 battery-monitor.py
        \nIn case you want, sound alongside visual notification,
        use:    python3 battery-monitor.py -s
        \nIf you want notification when the battery is at a stage (5, 10, 100),
        use:    python3 battery-monitor.py -n 5 10 100
        """,
                                         formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument('-n', '--notify', default=DEFAULT_STATUS, nargs='+',
                            type=int,
                            help="""Comma seperated values when you want notification
                            Note: Enter only integer values""")
        parser.add_argument('-s', '--sound', default=False, action='store_true',
                            help='Display notification along with a sound')
        args = parser.parse_args()
        notify_status = [int(i) for i in args.notify]
        # print('Notify values>>>>>', notify_status)
        sound_flag = args.sound
        # print('Sound flag>>>>>', sound_flag)
        if False in [False for i in notify_status if i < 0 or i > 100]:
            sys.exit('Percentages should be between 0 and 100')

        notify_values = {}
        notify_values[BATTERY_VALS] = notify_status
        notify_values[SOUND] = sound_flag

        with open(DATA_FILE, 'w', encoding='utf-8') as data_file:
            json.dump(notify_values, data_file, ensure_ascii=False, indent=4)

        print("You will get notified when your battery percentage is: ", notify_status)

    run_job(notify_status, sound_flag)


if __name__ == "__main__":
    main()
