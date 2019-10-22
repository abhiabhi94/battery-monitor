#### Battery-Monitor for Linux

This currently works on Python 3

To use:

- Just `clone` this repository
- Install [`ACPI`](https://en.wikipedia.org/wiki/Advanced_Configuration_and_Power_Interface)
- Navigate to the directory where you cloned this repository and run

```python
python battery-monitor.py # In case you want the notifications for default values(50, 30, 10, 5).
python battery-monitor.py X Y Z # In case you want notification when battery is at X%, Y%, Z%, you can give as many values as you wish
```

- Stop the program using `Keyboard Interrupt`(`Ctrl+C`)

- To make this program a part of `startup application` `search` `startup application` on your machine and add the contents of the `file` `cmd.txt`(inside the directory where you cloned this).

- To make changes to the percentages when you want notification, you can just edit the file `data.json` (inside the directory where you cloned this) appropriately.
