from pydoc import locate
import multiprocessing
import datetime

from extract_keywords import extract_keywords
import file_loaders
from family_resemblance_tagger.common import logger, database, config


def monitor(monitor_queue):
    apx_tasks = 0
    while True:
        update = monitor_queue.get()
        apx_tasks += update
        print("Approximate tasks remaining: {}".format(apx_tasks))


def process(input_queue, monitor_queue, lgr, conf):
    while True:
        item = input_queue.get()

        old_filepath = database.check_already_added(item["checksum"])

        if old_filepath is not None:
            lgr.report("Item already preprocessed.", item)

            if conf["preprocess_update_filepaths"] and old_filepath != item["filepath"]:
                lgr.report("Updating filepath in database to match input filepath", item)
                database.update_filepath(item["checksum"], item["filepath"])

            monitor_queue.put(-1)
            continue

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
            keywords = extract_keywords.extract_keywords(text)
            item["keywords"] = database.format_keywords_for_db(keywords)
            item["keywords_date"] = datetime.datetime.utcnow().strftime("%m/%d/%Y, %H:%M:%S")
            database.insert_item(item)
            lgr.report("Keywords added", item)
            monitor_queue.put(-1)
        else:
            lgr.warning("Preprocessor found no text.", object=item)


def main():

    conf = config.dict
    database.init_db()
    lgr = logger.Logger()

    multiprocessing.set_start_method('spawn')

    addr = (conf["preprocess_server_addr"], conf["preprocess_server_port"])
    listener = multiprocessing.connection.Listener(addr, authkey=conf["preprocess_server_authkey"])

    input_queue = multiprocessing.Queue()
    monitor_queue = multiprocessing.Queue()
    workers = [multiprocessing.Process(target=process, args=(input_queue, monitor_queue, lgr, conf))
        for _ in range(conf["preprocess_server_max_threads"])]

    workers[-1] = multiprocessing.Process(target=monitor, args=(monitor_queue,))

    for worker in workers:
        worker.start()

    lgr.report("Tag preprocessor is initialized and ready to receive preprocessing requests.")

    try:

        while True:
            conn = listener.accept()
            item = conn.recv()
            conn.close()

            input_queue.put(item)
            monitor_queue.put(1)
        
            lgr.report("Added item to preprocessing queue", item)
            

    except KeyboardInterrupt:
        for worker in workers:
            worker.terminate()
        exit()


if __name__=="__main__":
    main()
