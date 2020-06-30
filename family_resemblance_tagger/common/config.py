dict = {
	# These three variables are used by tag_preprocessor.py and queue_for_tags.py
	"preprocess_server_port" : 29028,
	"preprocess_server_addr" : "localhost",
	"preprocess_server_authkey" : b"server-authkey",

	# The number of threads that the preprocessor server should use.
	"preprocess_server_max_threads" : 2,


	# The following are used by the preprocessor and affect how keywords are extracted from the raw text of a file
	## keywords shorter than min_tag_length are discarded
	"min_tag_length" : 3,
	## Before creating ngrams, tokens of length less than min_token_length are discarded.
	## This is useful to remove things like single digits or roman numerals
	"min_token_length" : 2,
	## Keywords may be ngrams if they are prevalent. Potential keywords will include ngrams for all n, 1 < n <= ngram_max.
	"ngram_max" : 2,
	## keyword_threshold affects how many potential keywords are extracted.
	## The threshold is the target portion of text that should be covered by the keywords.
	## I.e., choose enough keywords so that x fraction of text is represented, where x = keyword_threshold.
	## Because of Zipf's law, a very small number of keywords will allow a relatively large portion of text to be covered.
	"keyword_threshold" : 0.20,


	# Whether to update filepaths based on the md5 hash of file.
	## If a newly added file shares a md5 hash but not a filepath with a file already added,
	## if preprocess_update_filepaths is True, then the preprocessor will retain the preprocessing results
	## but update the filepath to the new filepath.
	## If files are moved in the filesystem, by default then the preprocessor should just 'relink'
	## with the new path.
	"preprocess_update_filepaths" : True,


	# The following variables tune the behavior of the tag assignment algorithm

	## flow_demand: how many keywords should each document contribute to the group
	## This affects, but does not define, the number of keywords for each group.
	"flow_demand" : 2,

	## 'cost_alpha' is a parameter that tunes the cost function in the max flow problem.
	### In general, a higher value yields tags that are more unique and diverse.
	### In detail:
	### A value > 1.0 results in costs that depend more on the 'intrinsic_weight' of a keyword
	### A value < 1.0 results in costs that depend more on the 'commonality' of a keyword
	### The 'intrinsic_weight' of a keyword reflects the importance of a keyword in a document
	### The 'commonality' of a keyword reflects how many documents share the keyword
	"cost_alpha" : 1.0,

	## Force each document to contribute something. 
	## If set to True, the results will be considerably more diverse.

	"flow_constraint_full_coverage" : False,

	## 'cd_sim_thresh' sets the threshold for commonality between documents that 
	## affects how large the communities will be.
	## A higher threshold produces a large number of small, homogeneous communities.
	## A lower threshold produces a small number of relatively heterogenous communities.
	## Suggested range is between 0.1 and 0.5; required range is between 0.0 and 1.0. 
	"cd_sim_thresh" : 0.25,

	## When assigning tags to the filesystem, use this prefix on each tag.
	## This separates the tags from any pre-existing or manually assigned tags.
	## If the tags are removed from a document, all tags with this prefix will be removed.
	"tag_prefix" : "x__"

}