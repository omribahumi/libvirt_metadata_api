import re


def fix_indent(s):
    """
    Because of the way XML works, and the fact that cloud-init's user-data is usually a YAML document,
    fixing the user-data indentation is important. This function strips off the un-wanted indentation from user-data.

    Example: for the given XML document:

    <domain ...>
        <metadata>
            <userdata>
                #cloud-config
                key: value
                key2: value2
                key3:
                  subkey1: value
                  subkey2: value2
            </userdata>
        </metadata>
    </domain>

    This function will take "\n            #cloud-config\n            key: value\n            key2: value2\n            key3:\n              subkey1: value\n              subkey2: value2\n        "
    and return "#cloud-config\nkey: value\nkey2: value2\nkey3:\n  subkey1: value\n  subkey2: value2"

    :param s: input string to fix indentation on
    :type s: str
    :return: properly indented string
    :rtype: str
    """

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
