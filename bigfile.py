from collections import OrderedDict

from config import DEBUG

TEXT_ITEM_TYPE = 0
GROUP_TEXT_ITEM_TYPE = 1


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
        self.item_types_count = None
        self.item_types = None
        self.i_to_identifier = {}
        self.items = OrderedDict()
        # Parse
        self._read_header()
        self._read_index()

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
        return int("%02x%02x%02x%02x" % (data[3], data[2], data[1], data[0]), 16)

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

        # Read bank info
        self.p = self.bank_address
        self.banks_count = self._read_4byte_int()
        self.bank_name = self._read_string()
        self.bank_id = self._read_4byte_int()
        self.entries_in_bank = self._read_4byte_int()
        self.bank_index_start = self._read_4byte_int()
        self.bank_index_size = self._read_4byte_int()
        self.bank_block_size = self._read_4byte_int()

    def _read_index(self):
        self.p = self.bank_index_start
        self.item_types_count = self._read_4byte_int()
        self.item_types = {}
        item_sum = 0
        for _ in range(self.item_types_count):
            item_type = self._read_4byte_int()
            item_count = self._read_4byte_int()
            item_sum += item_count
            self.item_types[item_type] = item_count

        # Sanity check
        if item_sum != self.entries_in_bank:
            raise AssertionError("Incorrect number of items.")

        for _ in range(self.entries_in_bank):
            magic_number = self._read_4byte_int()
            item_id = self._read_4byte_int()
            item_type_1 = self._read_4byte_int()
            item_size = self._read_4byte_int()
            item_start = self._read_4byte_int()
            item_type_2 = self._read_4byte_int()
            symbol_len = self._read_4byte_int()
            symbol = self._read_string(length=symbol_len)

            self.i_to_identifier[item_id] = symbol

            # Not sure what is this/don't care
            a1 = self._read_4byte_int()
            a2 = self._read_4byte_int()
            a3 = self._read_4byte_int()
            if item_type_1 == TEXT_ITEM_TYPE:
                a4 = self._read_4byte_int()
            else:
                a4 = None

            # Sanity check
            if item_type_1 not in self.item_types or item_type_2 not in self.item_types:
                raise ValueError("Invalid type.")

            if DEBUG:
                print("")
                print("Magic number: '%s'" % magic_number)
                print("Item ID: '%s'" % item_id)
                print("Item type 1: '%s'" % item_type_1)
                print("Item size: '%s'" % item_size)
                print("Item start: '%s'" % item_start)
                print("Item type 2: '%s'" % item_type_2)
                print("Symbol length: '%s'" % symbol_len)
                print("Symbol: '%s'" % symbol)
                print("?1: '%s'" % a1)
                print("?2: '%s'" % a2)
                print("?3: '%s'" % a3)
                print("?4: '%s'" % a4)

            # Read item
            save_p = self.p
            self.p = item_start
            texts = self._read_item(item_type_1)
            if item_type_1 == TEXT_ITEM_TYPE:
                self.items[symbol] = texts[0]
            elif item_type_1 == GROUP_TEXT_ITEM_TYPE:
                self.items[symbol] = texts
            self.p = save_p

    def _read_item(self, item_type):
        texts = []
        sound_file_len = None
        sound_file = None
        speaker_len = None
        speaker = None
        identifier_len = None
        identifier = None
        modifier = None

        if item_type == GROUP_TEXT_ITEM_TYPE:
            text_choices = self._read_4byte_int()
            for _ in range(text_choices):
                i_num = self._read_4byte_int()
                linked_identifier = self.i_to_identifier[i_num]
                texts.append(linked_identifier)

        elif item_type == TEXT_ITEM_TYPE:
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
            if modifier_count:
                modifier = ""
            for _ in range(modifier_count):
                self._read_4byte_int()  # Not sure what this means
                modifier += self._read_string()

        if DEBUG:
            if item_type == TEXT_ITEM_TYPE:
                print("Text: '%s'" % texts[0])
                print("Sound file length: '%s'" % sound_file_len)
                print("Sound file: '%s'" % sound_file)
                print("Speaker length: '%s'" % speaker_len)
                print("Speaker: '%s'" % speaker)
                print("Identifier length: '%s'" % identifier_len)
                print("Identifier: '%s'" % identifier)
                print("Modifier: '%s'" % modifier)
            elif item_type == GROUP_TEXT_ITEM_TYPE:
                print("Text groups: '%s'" % ", ".join(texts))

        return texts

    def get_header(self):
        return {'version': self.version, 'bank_address': self.bank_address, 'banks_count': self.banks_count,
                'bank_name': self.bank_name, 'bank_id': self.bank_id, 'entries_in_bank': self.entries_in_bank,
                'bank_index_start': self.bank_index_start, 'bank_index_size': self.bank_index_size,
                'bank_block_size': self.bank_block_size}

    def get_index(self):
        return {'item_types_count': self.item_types_count, 'item_types': self.item_types}

    def get_items(self):
        return {self.bank_name: self.items}
