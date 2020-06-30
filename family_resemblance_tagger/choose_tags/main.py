from family_resemblance_tagger.common import logger, database, config
import detect_communities, choose_atags, write_tags
import argparse



def main():
    data = database.load_data()

    comms = detect_communities.detect_communities(data, sim_thresh=conf["cd_sim_thresh"])


    for comm in comms:
        atags = choose_atags.choose_atags(comm, data, flow_demand=conf["flow_demand"])

        for checksum in comm:
            if "atags" in data[checksum].keys():
                data[checksum][atags].append(atags)
            else:
                data[checksum]["atags"] = atags
            
        if args.report:
            print("For community of {} document(s):".format(len(comm)))
            for checksum in comm:
                print("\t{}".format(data[checksum]["filepath"]))

            print("Assigned Tags:\n\t{}".format(atags))
            print("-"*48)

    if args.write:
        lgr.report("Writing tags to filesystem...")
        write_tags.write_tags(data)
  

    lgr.report("Chose atags for {} documents in {} communities".format(len(data), len(comms)))



if __name__=="__main__":
    lgr = logger.Logger()
    parser = argparse.ArgumentParser("Assign tags based on previously extracted potential tags in database.")
    parser.add_argument("--report", "-r", action='store_true', default=False, help="Report the tags that will be assigned. If used without 'write', no changes will be made to filesystem tags.")
    parser.add_argument("--write", "-w", action='store_true', default=False, help="Write tags to file system.")
    args = parser.parse_args()
    conf = config.dict
    main()
