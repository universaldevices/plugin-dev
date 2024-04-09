import logging

# Set up the basic configuration for the logger
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create a logger instance
LOGGER = logging.getLogger('IoX-Plugin-Ext-Logger')

# Create a file handler to write logs to a file
file_handler = logging.FileHandler('iox-plugin-ext.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# Create a stream handler to output logs to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# Add the file handler and stream handler to the logger
LOGGER.addHandler(file_handler)
LOGGER.addHandler(console_handler)

# Use the logger in your extension
#logger.debug('Debug message')
#logger.info('Information message')
#logger.warning('Warning message')
#logger.error('Error message')
#logger.critical('Critical message')
