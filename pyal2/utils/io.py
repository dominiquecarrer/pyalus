import os
import logging

def ensure_dir(filename=None):
    dirname = os.path.dirname(filename)
    if dirname != '' and not os.path.exists(dirname):
        try:
            os.makedirs(dirname)
        except NotADirectoryError as e:
            logging.error(f'Cannot create directory {dirname} : A file with the same name may already exist.')
            raise(e)
        except Exception as e:
            if not os.path.exists(dirname):
                raise(e)


