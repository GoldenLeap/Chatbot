from configparser import ConfigParser
import os


def load_config(filename='database.ini', sec='postgresql'):
    base = os.path.dirname(__file__)
    path = os.path.join(base, filename)

    parser = ConfigParser()
    parser.read(path)
    
    config = {}
    if parser.has_section(sec):
        for key, val in parser.items(sec):
            config[key] = val
    else:
        raise Exception(f"seção '{sec}' não encontrada em {path}; seções disponíveis: {parser.sections()}")
            
    return config

if __name__ == '__main__':
    config = load_config()
    print(config)