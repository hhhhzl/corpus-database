from gevent import monkey
from gevent.pywsgi import WSGIServer

monkey.patch_all()

from apps import prediction_system
from utils import abspath
from utils.logger_tools import get_general_logger
from configs.management_app_config import HOST, PORT

logger = get_general_logger(name='prediction_management', path=abspath('logs'))


def main():
    app = prediction_system.create_app()
    # app.run(debug=True, port=10981, host='0.0.0.0')
    http_server = WSGIServer((HOST, PORT), app)
    logger.info('Prediction Management system data api Started.')
    logger.info(f'Host: {HOST} Port: {PORT} URL: http://{HOST}:{PORT}')
    http_server.serve_forever()

if __name__ == '__main__':
    main()
