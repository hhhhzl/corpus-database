from gevent import monkey
from gevent.pywsgi import WSGIServer
monkey.patch_all()

from apps import corpus_systems
from utils import abspath
from utils.logger_tools import get_general_logger
from configs.management_app_config import HOST, PORT

logger = get_general_logger(name='corpus_system', path=abspath('logs'))

def main():
    app = corpus_systems.create_app()
    # app.run(debug=True, port=5001, host='0.0.0.0')
    http_server = WSGIServer((HOST, PORT), app)
    logger.info('Corpus system data api Started.')
    logger.info(f'Host: {HOST} Port: {PORT} URL: http://{HOST}:{PORT}')
    http_server.serve_forever()

if __name__ == '__main__':
    main()