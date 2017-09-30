from collections import OrderedDict

from config import DEBUG


# http://fabletlcmod.com/wiki/doku.php?id=file_formats:big
class BigFile:
    def __init__(self, data):
        self.data = data
        self.data_len = len(data)
        self.p = 0
        self.version = None
        self.bank_address = None
        self.banks_count = None
        self.bank_name = None
        self.bank_id = None
        self.entries_in_bank = None
        self.bank_index_start = None
        self.bank_index_size = None
        self.bank_block_size = None
        self._read_header()
        self.i_to_identifier = {}

    def _read_bytes(self, count):
        if self.p >= self.data_len or self.p + count > self.data_len:
            return None
        r = self.data[self.p:self.p + count]
        self.p += count
        return bytearray(r)

    def _read_string(self, length=0, utf16le=False):
        chars = []
        i = 0

        # Just for sure
        if length and utf16le:
            raise AttributeError("Only ascii strings can have fixed length.")

        # Read chars
        while True:
            if not utf16le:
                if length:
                    c = self._read_bytes(1)
                    i += 1
                    # Don't save NULLs
                    if any(c):
                        chars.append(c.decode("ascii"))
                    # Fixed length string
                    if i == length:
                        break
                else:
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

    def _read_header(self):
        # BIGB
        file_sign = self._read_string(length=4)
        if file_sign != "BIGB":
            raise ValueError("Not a BIG file!")
        # Version
        self.version = self._read_string(length=4)
        # Bank address
        self.bank_address = self._read_4byte_int()
        # Unknown
        self._read_bytes(4)

        # Read bank
        p_save = self.p
        self.p = self.bank_address
        self.banks_count = self._read_4byte_int()
        self.bank_name = self._read_string()
        self.bank_id = self._read_4byte_int()
        self.entries_in_bank = self._read_4byte_int()
        self.bank_index_start = self._read_4byte_int()
        self.bank_index_size = self._read_4byte_int()
        self.bank_block_size = self._read_4byte_int()
        self.p = p_save

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

            texts.append(self._read_string(utf16le=True))

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
                modifier += self._read_string()

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

    def get_header(self):
        header = {'version': self.version, 'bank_address': self.bank_address, 'banks_count': self.banks_count,
                  'bank_name': self.bank_name, 'bank_id': self.bank_id, 'entries_in_bank': self.entries_in_bank,
                  'bank_index_start': self.bank_index_start, 'bank_index_size': self.bank_index_size,
                  'bank_block_size': self.bank_block_size}
        return header

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
