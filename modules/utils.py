

from math import atan, sqrt


def calculate_tbh(tbs, hr):
    return tbs * atan(0.151977 * sqrt(hr + 8.313659)) + atan(tbs + hr) - atan(hr - 1.6763) + 0.00391838 * pow(hr, 1.5) * atan(0.023101 * hr) - 4.686035
