#!/usr/bin/env python3.5

from rs import ReedSolomon

DATA_CHUNKS = 8
PARITY_CHUNKS = 4
TOTAL_CHUNKS = int(DATA_CHUNKS + PARITY_CHUNKS)


class Decoder:
    def main(self):
        chunk_present = [False] * TOTAL_CHUNKS
        chunks = [None] * TOTAL_CHUNKS
        chunk_size = None
        for i in range(TOTAL_CHUNKS):
            try:
                encoded = open("encoded/chunk_" + str(i) + ".dat", 'rb')
                encoded.seek(0, 2)
                if not chunk_size:
                    chunk_size = encoded.tell()
                encoded.seek(0)
                chunks[i] = bytearray(encoded.read())
                chunk_present[i] = True
                encoded.close()
            except IOError as e:
                pass

        for i in range(TOTAL_CHUNKS):
            if not chunks[i]:
                chunks[i] = bytearray(chunk_size)

        rs = ReedSolomon(DATA_CHUNKS, PARITY_CHUNKS, chunk_size)
        chunks = rs.decode(chunks, chunk_present)

        buffer = bytearray(chunk_size * DATA_CHUNKS)
        for i in range(DATA_CHUNKS):
            for j in range(chunk_size):
                if chunks[i][j] != 0:
                    buffer[i * chunk_size + j] = chunks[i][j]

        # print(buffer)

        decoded = open("decoded.jpg", 'wb')
        decoded.write(bytes(buffer))
        decoded.close()

if __name__ == "__main__":
    decoder = Decoder()
    decoder.main()
