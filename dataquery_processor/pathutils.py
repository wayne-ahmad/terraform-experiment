import sys
import os
import logging
from pathvalidate import sanitize_filename, validate_filename, ValidationError

logger = logging.getLogger(__name__)


def sanitise_filename(filename):
    """ Ensures that filenames are valid """
    if filename is None or filename.strip() == "":
        raise ValidationError("No filename or empty filename provided")
    sanitised_filename = sanitize_filename(filename)
    validate_filename(sanitised_filename)
    return sanitised_filename


def resource_path(relative_path):
    """ Get absolute path to resource within a PyInstaller one-file EXE """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = getattr(sys, '_MEIPASS')
        return os.path.join(base_path, relative_path)
    except AttributeError:
        return None


def package_file_path(relative_path):
    """ Get absolute path to a file within the deployment package, works for PyInstaller dir EXE"""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


def context_path(relative_path):
    """ Get path relative to the EXE """
    return relative_path


def get_config_path(config_file):
    logger = logging.getLogger(__name__)

    if os.path.exists(context_path(config_file)):
        logger.debug("Loaded config from local file")
        return context_path(config_file)

    if resource_path(config_file) and os.path.exists(resource_path(config_file)):
        logger.debug("Loaded config from app folder")
        return resource_path(config_file)

    if os.path.exists(package_file_path(config_file)):
        logger.debug("Loaded logging config from package")
        return package_file_path(config_file)

    # Default
    logger.debug("No config available")
    return None
