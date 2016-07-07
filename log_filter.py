import argparse
import re
from datetime import datetime


class LogLine:
    """
    Parses a line in a log file for easier manipulation.

    Attributes:
        line (str): The entire line in the log file
        time (datetime): The date and time of the log
        log_level (str): The severity of the log
        module (str): The origin module that created the log
    """
    time, log_level, module = None, None, None
    datetime_format = '%Y-%m-%d %H:%M:%S,%f'

    def __init__(self, line):
        """
        Parses a line in a log file.  Sets the time, log_level, and module attributes if any exist in the log.
        If an attribute does not exist in the line then it is set to None.

        Args:
            line (str): The entire log
        """
        self.line = line
        pattern = "^((\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d),(\d\d\d) - )?(.+) - (.+) - .+"
        match = re.match(pattern, line)
        if match is not None:
            temp_date = match.group(2)
            # I'm guessing this group is milliseconds? Unclear...
            temp_milliseconds = match.group(3)
            self.log_level = match.group(4)
            self.module = match.group(5)
            if temp_date is not None and temp_milliseconds is not None:
                temp_milliseconds = int(temp_milliseconds) * 1000
                self.time = datetime.strptime("%s,%s" % (temp_date, temp_milliseconds), self.datetime_format)

    def __repr__(self):
        return repr((self.time, self.log_level, self.module))

    def match_date(self, string):
        """
        Checks to see if a date string is at the front this object's time attribute when cast as a string.
        Returns a boolean based on the result

        Args:
            string (str): The string to match against the date attribute
        """
        if self.time is None:
            return False
        match = re.match("^%s.*" % string, self.time.strftime(self.datetime_format))
        if match is None:
            return False
        else:
            return True


# Define arguments
main_description = (
    "Filters a log file based on date, log level, and/or origin module. "
    "The results can then be sorted in order of one of the three previously mentioned "
    "values. Results are written to a file - \'outlog.txt\'"
)
log_level_help = "Filter logs based on level of severity."
module_help = "Filter logs based on the origin module"
date_help = (
    "Filter logs based on the date. This script will accept inputs as granular as "
    "the microsecond or as general as the year. "
    "Must be in the format of \'yyyy-mm-dd hh:mm:ss,fff\'. "
    "Examples: \'2016\', \'2016-06-07\', \'2016-06-07 02:12:12,111\'"
)
sort_value_help = "Sorts results of your filters or the entire log file if no filters are given."


def date_input(string):
    """
    Parses the date argument to ensure proper format. Raises an ArgumentTypeError if the 'string' is not acceptable.

    Args:
         string (str): The date string to be parsed
    """
    pattern = "^\d\d\d\d(-\d\d(-\d\d( \d\d(:\d\d(:\d\d(,\d\d\d)?)?)?)?)?)?$"
    match = re.match(pattern, string)
    if match is None:
        raise argparse.ArgumentTypeError("%s is not a proper date format!\n\n%s" % (string, date_help))
    return string

parser = argparse.ArgumentParser(description=main_description)
parser.add_argument('--log_level', choices=['DEBUG', 'INFO', 'WARNING'], help=log_level_help)
parser.add_argument('--module', help=module_help)
parser.add_argument('--date', help=date_help, type=date_input)
parser.add_argument('--sort_value', choices=['time', 'log_level', 'module'], help=sort_value_help)
args = parser.parse_args()

# Read input
logs = []
with open("input_log.txt", "r") as input_file:
    for line in input_file:
        logs.append(LogLine(line))

# Sort logs
if args.sort_value is not None:
    temp_logs = []
    for log in logs:
        if args.sort_value == "log_level" and log.log_level is not None:
            temp_logs.append(log)
        elif args.sort_value == "time" and log.time is not None:
            temp_logs.append(log)
        elif args.sort_value == "module" and log.module is not None:
            temp_logs.append(log)
    if args.sort_value == "log_level":
        logs = sorted(temp_logs, key=lambda x: x.log_level)
    elif args.sort_value == "time":
        logs = sorted(temp_logs, key=lambda x: x.time)
    else:
        logs = sorted(temp_logs, key=lambda x: x.module)

# Filter logs
filtered_output = ""
for log in logs:
    if args.log_level is not None and args.log_level != log.log_level:
        continue
    if args.module is not None and args.module != log.module:
        continue
    if args.date is not None and not log.match_date(args.date):
        continue
    filtered_output = "%s%s" % (filtered_output, log.line)

# Output results
output_file = open("outlog.txt", "w")
# Clear output.txt before writing results
output_file.seek(0)
output_file.truncate()
output_file.write(filtered_output)
output_file.close()
