from blueprints.dataApi.controllers import DataController
import fire


def hello(file_name):
    return file_name


if __name__ == "__main__":
    file_name = fire.Fire(hello)
    DataController.data_import(file_name=file_name)
