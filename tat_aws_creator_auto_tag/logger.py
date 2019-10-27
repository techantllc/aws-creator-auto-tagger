# -*- coding: utf-8 -*-

from loggerFactory import StreamOnlyLogger

logger = StreamOnlyLogger(name="default")

def log(msg, indent=0, verbose=True, **kwargs):
    if verbose:
        logger.info(msg, indent=indent, **kwargs)
    else:
        logger.debug(msg, indent=indent, **kwargs)
