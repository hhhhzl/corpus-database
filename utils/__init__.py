import os
import getpass
import datetime
from pprint import pprint
import pytz
USERNAME = getpass.getuser()
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def abspath(*path):
    """
    return absolute path from ROOT_DIR
    """
    abs_path = os.path.join(ROOT_DIR, *path)
    # file
    if '.' in path[-1]:
        dir_path = os.path.dirname(abs_path)
    else:
        dir_path = abs_path

    exists = os.path.exists(dir_path)
    if not exists:
        os.makedirs(dir_path)

    return abs_path


def iso_ts():
    current_china = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
    return current_china.isoformat()


def chunk_list(l, chunk_size):
    chunked_list = [l[i:i + chunk_size] for i in range(0, len(l), chunk_size)]
    return chunked_list


def generate_random_color():
    import random
    # Generate a random number for each RGB component and format it as a two-digit hexadecimal
    random_color = "#{:02X}{:02X}{:02X}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    return random_color


if __name__ == "__main__":
    print(iso_ts())
