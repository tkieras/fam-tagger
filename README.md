# Family Resemblance File Tagger

Assigns a set of tags to document communities that loosely captures what the documents have in common. While there are many approaches to tagging, the approach here aims to keep the number of tags relatively small, while making it more likely that tags are shared between documents. This may result in some counter-intuitive behavior, so read on to find out more about how the algorithm works. The basic use case of this approach is to treat tags as a loose file organization system, and so a balance needs to be found between tags that are very specific (descriptive, but isolated and numerous) and tags that are very general (vague, but reflecting group structure).

## Installation

```
git clone https://github.com/tkieras/fam-tagger
```

Before running any command described below, make sure that the environment variable PYTHONPATH is set properly in your shell. It must include the path to the downloaded directory 'fam-tagger'.


For example, after executing `git clone` as above,
```
cd fam-tagger
export PYTHONPATH=PYTHONPATH:$(pwd)
```

For the time being, this step must be repeated for each shell session, or included in a .bashrc / .bash_profile file.


## Usage

As an overview, there are three components to use in the following order:
	(1) A server process that conducts preprocessing.
	(2) A short script that adds documents to be preprocessed.
	(3) The main application that chooses and assigns tags to the documents that have been preprocessed.

Step by step usage:
	(0) Navigate to the directory `fam-tagger/family_resemblance_tagger`
	(1) Start the preprocessing server with:
		`python preprocessing/tag_preprocessor.py`
		- The output of this process includes logs and notifications, but no further action is required on this process.
		- To exit the process, use `Ctrl-c`
	(2) While the preprocessing server is running, add the files you want to be tagged with:
		`python preprocessing/queue_for_tags.py <path/to/file>`
		- You can add multiple files by using wildcard expansion:
		`python preprocessing/queue_for_tags.py <path/to/folder/>*.pdf`
		- Currently suported filetypes are:
			- pdf
			- docx
			- txt
			- epub
		- If you add a file that has already been preprocessed, the server will skip preprocessing it again.
	(3) At any point, you may execute the main application and choose tags. All documents that have been preprocessed will be given tags. There are a few options for how to run the main application:
		- To run the main application and preview the results without making changes to the file system:
			`choose_tags/main.py --report`
		- To run the main application and write the tags to the filesystem:
			`choose_tags/main.py --write`
		- To run the main application, view the results and write them to the filesystem:
			`choose_tags/main.py --report --write`
	(4) (Optional step) To remove any and all assigned tags that resulted from running the above step (3), run:
		`choose_tags/main.py --remove`
		- This step is only needed if you wish to cleanup bad results or otherwise remove traces of the tags assigned with step (3). It is like an 'undo' command for step (3).
		- By default, when running `choose_tags/main.py` with the `--write` flag set, the application will preserve user defined tags and ensure that the most up-to-date tags are set in the filesystem.
		- If you wish, you may run `choose_tags/main.py --remove --write`, but the removal step here is redundant.

## Configuration

Configuration is controlled by a file 'config.py' located in:
	`common/config.py`

The comments in the config file explain the various configuration options. No initial configuration is required.


## Algorithm Description

The process used here has several steps:
 (1) Preprocess the document contents to extract a small set of possible keywords.
 (2) Detect communities in the document set, where a user-defined threshold is used to indicate the similarity required for two documents to be adjacent.
 (3) For each detected community, assign a set of tags that represents the community. The tags are found by solving a max flow problem. Depending on user-defined parameters, the resulting tags will skew towards representing the commonalities, or toward representing the diversity of keywords found in the documents.

## Caveats

A feature of this approach is that the resulting tags for a given document will change depending on what other documents are also being tagged. In other words, the tags for a document are context dependent. As more documents are added, communities will evolve and the chosen tags for each community will reflect these changes.

As noted above, because tags are chosen at a group level, it is part of the intended behavior of this application that some tags to a document will not be keywords strictly found in the document itself. Depending on user-defined parameters, this will be more or less common. In such a case, the tag in question reflects keywords that are highly important to the group to which the document belongs. Therefore, the tag is assigned to the document because the document belongs to the group, and the tag reflects the group.

The inspiration for the algorithm comes from Wittgenstein's theory of family resemblance. In short, the notion is that common terms (i.e., 'dog', 'cat', 'game') do not need to reflect a conceptual 'least common denominator' or a definition that all members in the group share. Rather, membership in the group is assigned based on resemblance to other instances, and it may be impossible to discover a definition that all members in the group have in common. For the purpose of file tagging, the application of this theory is that not all documents in a cluster need to have a strictly shared topic, but rather they must all be related sufficiently closely to produce a family. Rather than give the family a single name (like 'cat', 'dog', 'game'), the family is named based on a heterogeneous set of keywords that, in general, captures what documents in the cluster are about. Read more about Wittgenstein at [https://plato.stanford.edu/entries/wittgenstein/#LangGameFamiRese!](https://plato.stanford.edu/entries/wittgenstein/#LangGameFamiRese)


## TODO:

	-diagnostics
	-experiment with hierarchical community detection, and/or using multiple thresholds