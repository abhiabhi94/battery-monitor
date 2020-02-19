#### Battery-Monitor for Linux

This currently works on Python 3

To use:

- Just `clone` this repository
- Install [`ACPI`](https://en.wikipedia.org/wiki/Advanced_Configuration_and_Power_Interface)
- Navigate to the directory where you cloned this repository and run

```python
python battery-monitor.py # In case you want the notifications for default values(50, 30, 10, 5).
python battery-monitor.py -n X Y Z # In case you want notification when battery is at X%, Y%, Z%, you can give as many values as you wish
python battery-monitor.py -s # In case you want a beep sound alongside the visual notification
python battery-monitor.py -d # In case you want continuous notifications when the battery is discharging.(extremely useful for people with faulty batteries)
python battery-monitory.py -h # This will give you all the information required to run the file
```

- Stop the program using `Keyboard Interrupt`(`Ctrl+C`)

- To make this program a part of `startup application` `search` `startup application` on your machine and add the contents of the `file` `cmd.txt`(inside the directory where you cloned this).

- To make changes to the percentages when you want notification, you may run the command again with the arguments of your choice or maybe edit the file `cmd.txt` (inside the directory where you cloned this) appropriately.
**Note**: In this case you will also have to change the contents of the command that you passed to the startup application.

- Thanks to the creator of the beep sound which was picked up from https://freesound.org/people/thisusernameis/sounds/426888/
