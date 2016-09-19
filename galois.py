from galois_tables import LOG_TABLE, EXP_TABLE


class Galois(object):
    def __init__(self):
        pass

    @staticmethod
    def multiply(x, y):
        if x == 0 or y == 0:
            return 0

        return EXP_TABLE[LOG_TABLE[x] + LOG_TABLE[y]]

    @staticmethod
    def divide(x, y):
        if y == 0:
            raise ValueError('Divided by zero!')
        if x == 0:
            return 0

        diff_log = LOG_TABLE[x] - LOG_TABLE[y]
        if diff_log < 0:
            diff_log += 255

        return EXP_TABLE[diff_log]

    @staticmethod
    def get_exp(a, n):
        if n == 0:
            return 1
        elif a == 0:
            return 0
        else:
            log_result = (LOG_TABLE[a] * n) % 255
            return EXP_TABLE[log_result]