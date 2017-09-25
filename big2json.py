#!/usr/bin/python

import sys
import json

# http://fabletlcmod.com/wiki/doku.php?id=file_formats:big
class BigArchive:
    def __init__(self, data):
        self.data = data
        self.data_len = len(data)
        if self.data[0:4] != "BIGB":
            raise ValueError("Not a BIG archive!")
        self.p = 0
        self._read_header()
        self.chunks = self._split_data()

    def _read_bytes(self, count):
        if self.p >= self.data_len or self.p + count > self.data_len:
            return None
        r = self.data[self.p:self.p + count]
        self.p += count
        return bytearray(r)

    def _read_header(self):
        self._read_bytes(16)

    def _split_data(self):
        chunks = []
        buff = []
        last_bytes = []
        while True:
            r = self._read_bytes(1)
            if r is None:
                break
            buff.extend(r)
            last_bytes.extend(r)
            # Shift
            if len(last_bytes) > 4:
                last_bytes = last_bytes[1:]
            if len(last_bytes) == 4 and not any(last_bytes):
                chunks.append(buff)
                buff = []
        if buff:
            chunks.append(buff)
        return chunks

    def _read_string(self, chunk, idx, label=False):
        chars = []
        while True:
            c = bytearray(chunk[idx:idx + 2])
            idx += 2
            # Both bytes null
            if not any(c):
                break
            if label:
                chars.append(c.decode("ascii", errors="ignore"))
            else:
                chars.append(c.decode("utf_16_le", errors="ignore"))
        result = "".join(chars)
        return result, idx 

    def _read_item(self, chunk):
        idx = 0
        text, idx = self._read_string(chunk, idx)
        # Something
        idx += 4
        sound_file, idx = self._read_string(chunk, idx, label=True)
        speaker, idx = self._read_string(chunk, idx, label=True)
        identifier, idx = self._read_string(chunk, idx, label=True)
        return identifier, text

    def get_items(self):
        items = {}
        for chunk in self.chunks:
            identifier, text = self._read_item(chunk)
            if identifier:
               items[identifier] = text
        return items


big = BigArchive(sys.stdin.read())
#print(len(big.get_items()))
print(json.dumps(big.get_items(), indent=4, ensure_ascii=False, sort_keys=True).encode("utf_8"))

