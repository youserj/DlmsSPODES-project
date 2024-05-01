from typing import Self


class ByteBuffer:
    buf: memoryview

    """Object class wrapping a byte array and allowing manipulation"""
    def __init__(self, buffer: memoryview):
        self.buf = buffer
        """ the data buffer """
        self.pos = 0
        """ current position """

    @classmethod
    def allocate(cls, size: int) -> Self:
        """return instance with creating buffer"""
        return cls(memoryview(bytearray(size)))

    @classmethod
    def wrap(cls, data: bytes) -> Self:
        return cls(memoryview(data))

    def remaining(self, pos: int = None) -> int:
        """remaining bytes"""
        if pos is None:
            pos = self.pos
        return len(self.buf) - pos

    def _check_space(self, space: int, pos: int = None):
        """check whether this buffer has enough `space` left for r/w op"""
        if not pos:
            pos = self.pos
        if self.remaining(pos) < space:
            raise BufferError(F"{self} not enough more {space=}")

    def read(self, length: int = 1) -> memoryview:
        """return view to position, increase position"""
        ret = self.read_pos(self.pos, length)
        self.pos += length
        return ret

    def read_pos(self,
                 pos: int,
                 length: int = 1) -> memoryview:
        """return view to position"""
        self._check_space(length)
        ret = self.buf[pos: pos + length]
        return ret

    def write(self,
              value: memoryview | bytes,
              length: int = None) -> int:
        """keep data to position, increase position"""
        self.pos += (length := self.write_pos(value, self.pos, length))
        return length

    def write_pos(self,
                  value: memoryview | bytes,
                  pos: int,
                  length: int = None) -> int:
        """keep data to position, return length data"""
        if not length:
            length = len(value)
        self._check_space(length, pos)
        self.buf[pos: pos + length] = value
        return length

    def put_int(self, value: int) -> int:
        """put builtin int, increase position"""
        self._check_space(1)
        self.buf[self.pos] = value
        self.pos += 1
        return 1

    def get_uint(self, length: int) -> int:
        """get INTEGER, increase position"""
        return int.from_bytes(self.read(length), 'big')

    def get_uint_pos(self,
                     pos: int,
                     length: int) -> int:
        """get INTEGER"""
        return int.from_bytes(self.read_pos(pos, length), 'big')

    def get_uint8(self) -> int:
        """get integer8, increase position"""
        return self.read(1)[0]

    def get(self) -> bytes:
        """get one byte, increase position"""
        return bytes(self.read(1))

    def __bytes__(self, length=0):
        return bytes(self.buf)

    def slice(self) -> Self:
        """slice the buffer at current position. return new class"""
        return self.__class__(self.buf[self.pos:])

    def frozen(self) -> Self:
        """return instance with not writable buffer"""
        return self.__class__(memoryview(bytes(self)))

    def __len__(self):
        return len(self.buf)

    def __str__(self):
        return F"{self.__class__.__name__}[{len(self)}]: pos={self.pos}, frozen={self.buf.readonly}"
