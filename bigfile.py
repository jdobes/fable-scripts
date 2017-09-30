from collections import OrderedDict

from config import DEBUG


# http://fabletlcmod.com/wiki/doku.php?id=file_formats:big
class BigFile:
    def __init__(self, data):
        self.data = data
        self.data_len = len(data)
        if self.data[0:4] != "BIGB":
            raise ValueError("Not a BIG archive!")
        self.p = 0
        self._read_header()
        self.i_to_identifier = {}

    def _read_bytes(self, count):
        if self.p >= self.data_len or self.p + count > self.data_len:
            return None
        r = self.data[self.p:self.p + count]
        self.p += count
        return bytearray(r)

    def _read_header(self):
        self._read_bytes(16)

    def _read_string(self, length=0, modifier=False):
        chars = []
        i = 0

        # Read chars
        while True:
            if length:
                c = self._read_bytes(1)
                i += 1
                chars.append(c.decode("ascii"))
                # Fixed length string
                if i == length:
                    break
            elif modifier:
                c = self._read_bytes(1)
                # NULL limited string
                if not any(c):
                    break
                chars.append(c.decode("ascii"))
            else:
                c = self._read_bytes(2)
                # NULL limited string
                if not any(c):
                    break
                chars.append(c.decode("utf_16_le"))

        result = "".join(chars)
        return result

    def _read_4byte_int(self):
        data = self._read_bytes(4)
        return int("%x%x%x%x" % (data[3], data[2], data[1], data[0]), 16)

    def _read_item(self):
        texts = []
        sound_file_len = 0
        sound_file = ""
        speaker_len = 0
        speaker = ""
        identifier = ""
        modifier = ""

        text_choices = self._read_4byte_int()
        # Some magical limits
        if 0 < text_choices < 10:
            what = "group"
            for _ in range(text_choices):
                i_num = self._read_4byte_int()
                linked_identifier = self.i_to_identifier[i_num]
                texts.append(linked_identifier)

            identifier_len = self._read_4byte_int()
            if identifier_len:
                identifier = self._read_string(length=identifier_len)
        else:
            what = "text"
            # Rollback
            self.p -= 4

            texts.append(self._read_string())

            sound_file_len = self._read_4byte_int()
            if sound_file_len:
                sound_file = self._read_string(length=sound_file_len)

            speaker_len = self._read_4byte_int()
            if speaker_len:
                speaker = self._read_string(length=speaker_len)

            identifier_len = self._read_4byte_int()
            if identifier_len:
                identifier = self._read_string(length=identifier_len)

            modifier_count = self._read_4byte_int()
            for _ in range(modifier_count):
                self._read_4byte_int()  # Not sure what this means
                modifier += self._read_string(modifier=True)

        if DEBUG:
            if what == "text":
                print("Text: '%s'" % texts[0])
                print("Sound file length: '%d'" % sound_file_len)
                print("Sound file: '%s'" % sound_file)
                print("Speaker length: '%d'" % speaker_len)
                print("Speaker: '%s'" % speaker)
            else:
                print("Text groups: '%s'" % ", ".join(texts))
            print("Identifier length: '%d'" % identifier_len)
            print("Identifier: '%s'" % identifier)
            print("Modifier: '%s'" % modifier)

        return what, identifier, texts

    def get_items(self):
        items = OrderedDict()
        i = 0
        while True:
            i += 1
            if DEBUG:
                print("ID: %d" % i)
            what, identifier, texts = self._read_item()
            self.i_to_identifier[i] = identifier
            if what == "text":
                items[identifier] = texts[0]
            else:
                items[identifier] = texts

            # Test
            if i > 26809:
                break

        return items
