import re  # Regular expressions
import string
import sys
from unidecode import unidecode


class Slugifier(object):
    def __init__(self):
        self.to_lower = True
        self.safe_chars = string.ascii_letters + string.digits  # "a...zA...Z0...9"
        self.separator_char = '-'

    def slugify(self, text):
        if sys.version_info[0] == 2:  # Python 2.x
            if not isinstance(text, unicode):
                text = text.decode('utf8', 'ignore')
        else:  # Python 3.x
            if not isinstance(text, str):
                text = text.decode('utf8', 'ignore')
        text = unidecode(text)

        # Lower case if specified
        if self.to_lower:
            text = text.lower()

        # Replace one or more unsafe chars with one separator char
        # Compile regular expression once
        if not hasattr(self, 'compiled_expression'):
            expression = '[^' + self.safe_chars + ']+'
            self.compiled_expression = re.compile(expression)
        # Substitute unsafe chars using compiled expression
        text = self.compiled_expression.sub(self.separator_char, text)
        # Strip leading and trailing separator chars
        text = text.strip(self.separator_char)

        return text

