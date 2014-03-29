import re


def fix_indent(s):
    if s[0] != '\n':
        return s

    match = re.match('\s+', s[1:])
    if not match:
        return s

    spaces = match.group(0)
    lines = s.split("\n")

    if lines[0] != '' or not re.match('^\s+$', lines[-1]):
        return s

    if not all((line.startswith(spaces) for line in lines[1:-1])):
        return s

    return "\n".join((line[len(spaces):] for line in lines[1:-1]))
