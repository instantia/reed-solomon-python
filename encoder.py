#!/usr/bin/env python3.5

import math
import numpy as np;

from rs import ReedSolomon

DATA_CHUNKS = 8
PARITY_CHUNKS = 4
TOTAL_CHUNKS = int(DATA_CHUNKS + PARITY_CHUNKS)


class Encoder:
    def main(self):
        source = open("source.jpg", 'rb')
        source.seek(0, 2)

        source_size = source.tell()
        chunk_size = math.ceil(source_size / DATA_CHUNKS)
        buffer_size = int(chunk_size * DATA_CHUNKS)

        source.seek(0)
        source_bytes = bytearray(source.read())

        chunks = [
            bytearray(chunk_size)
                for x in range(DATA_CHUNKS)
        ]

        for i in range(DATA_CHUNKS):
            for j in range(chunk_size):
                if i * chunk_size + j < len(source_bytes):
                    chunks[i][j] = source_bytes[i * chunk_size + j]

        rs = ReedSolomon(DATA_CHUNKS, PARITY_CHUNKS, chunk_size)
        chunks = rs.encode(chunks)

        for i in range(TOTAL_CHUNKS):
            encoded = open("encoded/chunk_" + str(i) + ".dat", 'wb')
            encoded.write(bytes(chunks[i]))
            encoded.close()

        source.close()

if __name__ == "__main__":
    encoder = Encoder()
    encoder.main()
