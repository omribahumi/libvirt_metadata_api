import unittest
import utils


class XmlTestCase(unittest.TestCase):
    def test_fix_indent(self):
        original_string = ("\n" +
                           "            #cloud-config\n" +
                           "            key: value\n" +
                           "            key2: value2\n" +
                           "            key3:\n" +
                           "              subkey1: value\n" +
                           "              subkey2: value2\n" +
                           "        ")

        self.assertEqual(utils.xml.fix_indent(original_string), "#cloud-config\n" +
                                                                "key: value\n" +
                                                                "key2: value2\n"
                                                                "key3:\n" +
                                                                "  subkey1: value\n" +
                                                                "  subkey2: value2")

        self.assertEqual(utils.xml.fix_indent(original_string[1:]), original_string[1:])
        self.assertEqual(utils.xml.fix_indent("\n" + original_string.lstrip()), "\n" + original_string.lstrip())
        self.assertEqual(utils.xml.fix_indent(original_string.rstrip()), original_string.rstrip())

        original_split = original_string.split("\n")
        original_split[2] = original_split[2][1:]  # remove a space from the 3rd line
        self.assertEqual(utils.xml.fix_indent("\n".join(original_split)), "\n".join(original_split))


