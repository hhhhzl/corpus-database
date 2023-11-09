from blueprints.dataApi.controllers import DataController
import fire


def file_command(file_name):
    return file_name


if __name__ == "__main__":
    file_name = fire.Fire(file_command)
    DataController.data_import(data_file=file_name)
