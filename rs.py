import numpy as np;
from galois import Galois


class ReedSolomon(object):
    def __init__(self, data_chunk_count, parity_chunk_count, chunk_size):
        self.data_chunk_count = data_chunk_count
        self.parity_chunk_count = parity_chunk_count
        self.total_chunk_count = data_chunk_count + parity_chunk_count
        self.chunk_size = chunk_size
        self.generated_matrix = self.generate_matrix()
        self.matrix_rows = self.generated_matrix[self.data_chunk_count:self.total_chunk_count]

    def encode(self, chunks):
        outputs = self.code_chunks(chunks,
                                   self.chunk_size,
                                   self.parity_chunk_count,
                                   self.data_chunk_count,
                                   self.matrix_rows)

        return np.concatenate((chunks, outputs), axis=0)

    def decode(self, chunks, chunk_present):
        data_missing_count = 0
        parity_missing_count = 0
        for i in range(len(chunk_present)):
            if not chunk_present[i]:
                if i < self.data_chunk_count:
                    data_missing_count += 1
                else:
                    parity_missing_count += 1

        if data_missing_count == 0 and parity_missing_count == 0:
            return chunks

        if data_missing_count + parity_missing_count > self.parity_chunk_count:
            raise ValueError('Not enough chunks for decode!')

        sub_matrix = np.zeros(shape=(self.data_chunk_count, self.data_chunk_count), dtype=np.int)
        sub_chunks = [
            bytearray(self.chunk_size)
                for x in range(self.data_chunk_count)
        ]
        sub_matrix_row = 0
        for i in range(self.total_chunk_count):
            if sub_matrix_row >= self.data_chunk_count:
                break
            if chunk_present[i]:
                for j in range(self.data_chunk_count):
                    sub_matrix[sub_matrix_row][j] = self.generated_matrix[i][j]
                sub_chunks[sub_matrix_row] = chunks[i]
                sub_matrix_row += 1

        decode_matrix = self.invert_matrix(sub_matrix)

        matrix_rows = [None] * self.parity_chunk_count

        # outputs = []
        # second_outputs = []
        if data_missing_count > 0:
            output_count = 0
            for i in range(self.data_chunk_count):
                if not chunk_present[i]:
                    matrix_rows[output_count] = decode_matrix[i]
                    output_count += 1

            outputs = self.code_chunks(sub_chunks,
                                       self.chunk_size,
                                       output_count,
                                       self.data_chunk_count,
                                       matrix_rows)

        if parity_missing_count > 0:
            output_count = 0
            for i in range(self.data_chunk_count, self.total_chunk_count):
                if not chunk_present[i]:
                    matrix_rows[output_count] = self.matrix_rows[i - self.data_chunk_count]
                    output_count += 1

            second_outputs = self.code_chunks(chunks,
                                       self.chunk_size,
                                       output_count,
                                       self.data_chunk_count,
                                       matrix_rows)

        data_i = 0
        parity_i = 0
        for i in range(len(chunk_present)):
            if not chunk_present[i]:
                if i < self.data_chunk_count:
                    chunks[i] = outputs[data_i]
                    data_i += 1
                else:
                    chunks[i] = second_outputs[parity_i]
                    parity_i += 1

        return chunks

    def generate_matrix(self):
        matrix = self.generate_vander(self.total_chunk_count, self.data_chunk_count)
        sub_matrix = matrix[0:self.data_chunk_count]

        # invert matrix
        right_matrix = self.invert_matrix(sub_matrix)

        right_cols = len(right_matrix[0])
        result = np.zeros(shape=(len(matrix), right_cols), dtype=np.int)
        for i in range(len(matrix)):
            for j in range(right_cols):
                value = 0
                for k in range(len(matrix[0])):
                    value ^= Galois.multiply(matrix[i][k], right_matrix[k][j])
                result[i][j] = value

        return result

    @staticmethod
    def code_chunks(chunks, chunk_size, output_count, input_count, matrix_rows):
        outputs = [
            bytearray(chunk_size)
                for x in range(output_count)
        ]
        for i in range(chunk_size):
            for j in range(output_count):
                matrix_row = matrix_rows[j]
                value = 0
                for k in range(input_count):
                    value ^= Galois.multiply(matrix_row[k], chunks[k][i])
                    outputs[j][i] = value

        return outputs

    @staticmethod
    def invert_matrix(matrix):
        original_rows = len(matrix)
        original_cols = len(matrix[0])

        identity_matrix = ReedSolomon.identity(original_rows)
        concat_matrix = np.concatenate((matrix, identity_matrix), axis=1)

        rows = len(concat_matrix)
        cols = len(concat_matrix[0])
        for i in range(rows):
            if concat_matrix[i][i] == 0:
                for k in range(i + 1, rows):
                    if concat_matrix[k][i] != 0:
                        ReedSolomon.swap_rows(concat_matrix, k, i)
                        break

            if concat_matrix[i][i] == 0:
                raise ValueError('Matrix is singular!')

            if concat_matrix[i][i] != 1:
                scale = Galois.divide(1, concat_matrix[i][i])
                for j in range(cols):
                    concat_matrix[i][j] = Galois.multiply(concat_matrix[i][j], scale)

            for j in range(i + 1, rows):
                if concat_matrix[j][i] != 0:
                    scale = concat_matrix[j][i]
                    for k in range(cols):
                        concat_matrix[j][k] ^= Galois.multiply(scale, concat_matrix[i][k])

        for i in range(rows):
            for j in range(i):
                if concat_matrix[j][i] != 0:
                    scale = concat_matrix[j][i]
                    for k in range(cols):
                        concat_matrix[j][k] ^= Galois.multiply(scale, concat_matrix[i][k])

        # sub
        result_matrix = concat_matrix[:, [i for i in range(original_cols, cols)]]

        return result_matrix

    @staticmethod
    def swap_rows(matrix, i, j):
        temp = np.copy(matrix[i])
        matrix[i] = matrix[j]
        matrix[j] = temp

        return matrix

    @staticmethod
    def identity(size):
        result = np.zeros(shape=(size, size), dtype=np.int)
        for i in range(size):
            result[i][i] = 1

        return result

    @staticmethod
    def generate_vander(rows, cols):
        result = np.zeros(shape=(rows, cols), dtype=np.int)

        for i in range(rows):
            for j in range(cols):
                result[i][j] = Galois.get_exp(i, j)

        return result