import importlib
import sys

def get_data_writer(writer_string):
    """ This function is responsible to import the appropriate code to write data """
    if writer_string == 'c3s_writer':
        import pyal2.writers.c3s_writer
        return pyal2.writers.c3s_writer.Writer, pyal2.writers.c3s_writer.data_params
    if writer_string == 'msg_writer':
        import pyal2.writers.msg_writer
        return pyal2.writers.msg_writer.Writer, pyal2.writers.msg_writer.data_params
    if writer_string == 'mtg_writer':
        import pyal2.writers.mtg_writer
        return pyal2.writers.mtg_writer.Writer, pyal2.writers.mtg_writer.data_params
    raise Exception(f'Error : cannot find writer {writer_string}. It needs to be defined in the file pyal2/writers/__init__.py')
