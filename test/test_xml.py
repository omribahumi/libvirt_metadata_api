import unittest
import utils


class XmlTestCase(unittest.TestCase):
    def test_fix_indent(self):
        fixed_string = utils.xml.fix_indent("\n" +
                                            "            #cloud-config\n" +
                                            "            key: value\n" +
                                            "            key2: value2\n" +
                                            "            key3:\n" +
                                            "              subkey1: value\n" +
                                            "              subkey2: value2\n" +
                                            "        ")

        self.assertEqual(fixed_string, "#cloud-config\n" +
                                       "key: value\n" +
                                       "key2: value2\n"
                                       "key3:\n" +
                                       "  subkey1: value\n" +
                                       "  subkey2: value2")
