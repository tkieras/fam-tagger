from family_resemblance_tagger.common import logger, database, config
import file_loaders
from pydoc import locate
from multiprocessing import Pool, connection, Manager
import multiprocessing
import datetime

from extract_keywords import extract_keywords


def ingest_request_handler(item):
    loaders = file_loaders.__all__
    loader_it = 0
    text = None
    while(text is None):
        loader = locate("file_loaders." + loaders[loader_it])
        text = loader.load(item["filepath"])
        loader_it += 1
        if(loader_it >= len(loaders)):
            break
    
    if text is not None:
    
        ptags = extract_keywords.extract_keywords(text)
        item["ptags"] = ptags
        item["ptags_date"] = datetime.datetime.utcnow().strftime("%m/%d/%Y, %H:%M:%S")

        return item
    else:
        lgr.warning("Ingest processor found no text.", object=item)
        return None


def ingest_consumer_callback(item):
    if item is not None:
        lgr.report("ptags added", item)
        data[item["checksum"]] = item
        database.save_data(data.copy())
    


def check_redundancy(item):
    if item["checksum"] not in data.keys():
        return item

    lgr.report("Item already added", item)

    already_added = data[item["checksum"]]

    if conf["preprocess_update_filepaths"] and already_added["filepath"] != item["filepath"]:
        data[item["checksum"]]["filepath"] = item["filepath"]
        database.save_data(data.copy())
        lgr.report("Updating filepath in database to match input filepath", item)
    
    return None


def main():
    
    lgr.report("Ingest request consumer is initialized and ready to process.")

    try:

        while True:
            conn = listener.accept()
            item = conn.recv()
            conn.close()

            item = check_redundancy(item)
            if item is None:
                continue
            
            lgr.report("Added item to ingest processing queue", item)
            result = pool.apply_async(ingest_request_handler, 
                [item], callback=ingest_consumer_callback)
            result.ready()

    except KeyboardInterrupt:
        pool.terminate()
        exit()


if __name__=="__main__":

    multiprocessing.set_start_method('spawn')
    conf = config.dict
    addr = (conf["preprocess_server_addr"], conf["preprocess_server_port"])

    
    pool = Pool(conf["preprocess_server_max_threads"])
    manager = Manager()
    data = manager.dict(database.load_data())
    listener = connection.Listener(addr, authkey=conf["preprocess_server_authkey"])

    lgr = logger.Logger()
    main()


