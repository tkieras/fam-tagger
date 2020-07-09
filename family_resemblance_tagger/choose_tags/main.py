from family_resemblance_tagger.common import logger, database, config
import detect_communities, choose_community_tags, write_tags
import argparse



def main():
    data = database.load_all_data()

    comms = detect_communities.detect_communities(data, sim_thresh=conf["cd_sim_thresh"])


    for comm in comms:
        tags = choose_community_tags.choose_community_tags(comm, data, flow_demand=conf["flow_demand"])

        for checksum in comm:
            if data[checksum]["tags"] is not None:
                data[checksum]["tags"].append(tags)
            else:
                data[checksum]["tags"] = tags
            
        if args.report:
            print("For community of {} document(s):".format(len(comm)))
            for checksum in comm:
                print("\t{}".format(data[checksum]["filepath"]))

            print("Assigned Tags:\n\t{}".format(tags))
            print("-"*48)

    if args.remove:
        write_tags.remove_tags(data)

    if args.write:
        lgr.report("Writing tags to filesystem...")
        write_tags.write_tags(data)
  

    lgr.report("Chose atags for {} documents in {} communities".format(len(data), len(comms)))



if __name__=="__main__":
    lgr = logger.Logger()
    parser = argparse.ArgumentParser("Assign tags based on previously extracted potential tags in database.")
    parser.add_argument("--report", "-r", action='store_true', default=False, help="Report the tags that will be assigned. If used without 'write', no changes will be made to filesystem tags.")
    parser.add_argument("--write", "-w", action='store_true', default=False, help="Write tags to file system.")
    parser.add_argument("--remove", action='store_true', default=False, help="Remove all tags assigned by this application.")
    args = parser.parse_args()
    conf = config.dict
    main()
