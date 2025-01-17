import logging

from anubis.config import config


def _get_logger(logger_name):
    """
    For any of the anubis services that use the API, the
    logger name should be specified. In prod, container
    logs will be captured by filebeat and pushed into
    elasticsearch in the elastic namespace.

    :param logger_name:
    :return:
    """

    # Initialize a logger for this app with the logger
    # name specified
    streamer = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    streamer.setFormatter(formatter)
    _logger = logging.getLogger(logger_name)
    _logger.setLevel(logging.NOTSET)
    _logger.addHandler(streamer)

    return _logger


# Create a single logger object for the current app instance
logger = _get_logger(config.LOGGER_NAME)
