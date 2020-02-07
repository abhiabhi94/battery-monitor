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

CMD_FILE = os.path.join(BASE_DIR, 'cmd.txt')
SOUND_FILE = os.path.join(BASE_DIR, os.path.join('sounds', 'beep4.wav'))
STARTUP_CMD = os.path.join(BASE_DIR, __file__)

DEFAULT_STATUS = [50, 30, 10, 5]
BATTERY_VALS = 'battery-values'
SOUND = 'sound'

last_state = None
last_status = None
state = {}
status = {}
# state['change'] = False
# status['change'] = False


def parse_args():
    """
    Parse and returns the command line arguments

    Returns
        args
    """

    parser = argparse.ArgumentParser(description="""
        Notify me at the when the battery reaches certain stages or
        when a charger is plugged or unplugged
        \nBy default: you will get notification when the battery reaches the percentages
        {} alongwith no sound.
        \nExample:
        If you want default options,
        use:    python3 battery-monitor.py
        \nIn case you want, sound alongside visual notification,
        use:    python3 battery-monitor.py -s
        \nIf you want notification when the battery is at a stage (5, 10, 100),
        use:    python3 battery-monitor.py -n 5 10 100
        """.format(DEFAULT_STATUS),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-n', '--notify', default=DEFAULT_STATUS, nargs='+',
                        type=int,
                        help="""Comma seperated values when you want notification
                            Note: Enter only integer values""")
    parser.add_argument('-d', '--notify-on-discharge', default=False, action='store_true',
                        help='Display notification along with a sound')
    parser.add_argument('-s', '--sound', default=False, action='store_true',
                        help='Display notification along with a sound')

    return parser.parse_args()


def write_command_to_file(choices):
    """
    Write the command to be executed to a file for the program
     to operate in the background.

    Returns
        None

    Params
        choices: str
        All the choices entered by the user.
    """

    # Extracts the first three characters from the version output e.g 3.5
    PY_VERSION = sys.version[:3]

    with open(CMD_FILE, 'w') as cmd_file:
        # f.write(f'python{PY_VERSION} {CMD_FILE}')
        cmd_file.write('python{} {}{}'.format(
            PY_VERSION, STARTUP_CMD, choices))


def make_cli_options(notify_status, sound_flag, notify_on_discharge_flag):
    """
    Returns
        choices: str
            Compatible for writing command to the text file
            so that they may be passed to the CLI

    Params
        notify_status: list
            The list of values for which notification will be provided
        sound_flag: bool
            Whether sound choice was used or not
        notify_on_discharge_flag: bool
            Keep notifing when battery is discharging.
    """

    choices = ' -n '

    for val in notify_status:
        choices += str(val) + ' '
    if sound_flag:
        choices += '-s '
    if notify_on_discharge_flag:
        choices += '-d'

    return choices


def prepocess_notify_args(val):
    """
    Returns:
        val: list
            The list of arguments for notification after
             they have been converted to integer format

    Params:
        val: list
            The list of arguments passed to the -n option on the CLI
    """
    val = [int(i) for i in val]

    if False in [False for i in val if i < 0 or i > 100]:
        sys.exit('Percentages should be between 0 and 100')

    return val


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


def notify_required(*args):
    """
    Returns: bool
        Whether the boolean product of all conditions is true or not

    Param: arguments
        Note: all arguments need to be boolean for them to be processed well.
    """
    result = False
    for arg in args:
        result = result or arg
    return result


def run_job(notify_status, sound_flag, notify_on_discharge_flag):
    """
    Runs the job for notifying the information about battery
    Returns
        None

    Params:
        notify_status: list
            The list containing integer values for which notification will be given.
        sound_flag: bool
            Whether sound is asked alongwith visual notification.
        notify_on_discharge_flag: bool
            Whether continous notification is required when battery is not charged.
    """
    while True:
        result = get_battery_info(sound_flag)
        if result:
            state['val'], status['val'], time_left, dest = result
            # notification = f'Battery {state['val']}, {status['val']}%, {time_left} {dest}'
            notification = 'Battery {}, {}%, {} {}'.format(
                state['val'], status['val'], time_left, dest)

            # Keep notifying if it is asked when battery is discharging
            # Notify once when there is a change in battery state(charging -> discharging)
            # Notify once if the state(current battery percentage) is among the values requested for
            if notify_required(notify_on_discharge_flag and state['val'].lower() == 'discharging',
                               has_state_changed(state['val']),
                               status['val'] in notify_status and has_status_changed(status['val'])):
                # if (notify_on_discharge_flag) or
                # (has_state_changed(state['val'])) or
                # (status['val'] in notify_status and has_status_changed(status['val'])):
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
    args = parse_args()

    notify_status = prepocess_notify_args(args.notify)

    choices = make_cli_options(notify_status, args.sound,
                               args.notify_on_discharge)

    write_command_to_file(choices)

    print("You will get notified when your battery percentage is: ", notify_status)

    run_job(notify_status, args.sound, args.notify_on_discharge)


if __name__ == "__main__":
    main()
