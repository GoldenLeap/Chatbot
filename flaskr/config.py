from configparser import ConfigParser

def load_config(filename='database.ini', sec='postgresql'):
    parser = ConfigParser()
    parser.read(filename)
    
    config = {}
    if(parser.has_section(sec)):
        params= parser.items(sec)
        for param in params:
            config[param[0]] = param[1]
    else:
        raise Exception('{0} não encontrado no arquivo {1}'.format(sec, filename))
            
    return config

if __name__ == '__main__':
    config = load_config()
    print(config)