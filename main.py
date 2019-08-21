import os, sys
from pygitlib import *

def printlist (label, l) :
	print (label)
	for i in l :
		print("\t" + i)

def cut_branches (tree_a, tree_b) :
	out_tree = []
	for br in tree_a :
		if not (br in tree_b) :
			out_tree.append(br)
	return out_tree

class MimesisMerger :
	def __init__ (self, repo_dir=".") :
	self.gitrepo = GitCmd (repo_dir)
	origin = self.gitrepo.checkrepo ("origin", "https://github.com/mimesis-inria/sofa.git") 
	sofaframework = self.gitrepo.checkrepo("sofa-framework", "https://github.com/sofa-framework/sofa.git")
	if not origin and not sofaframework:
		print (">>> check remotes, might be missing")
		exit()
	self.gitrepo.fetch()
	self.gitrepo.fetch("--prune")

	self.blacklist = [
		"origin/HEAD",
		"origin/cmtopology",
		"origin/cmtopology_draft",
		"origin/cmtopology_module",
		"origin/cmtopology_pr_backup",
		"origin/cmtopology_rebased_cleaned_squashed",
		"origin/issofa_beamfemff",
		"origin/issofa_debug",
		"rigin/issofa_deprecatedapi",
		"origin/issofa_gui",
		"origin/issofa_planeff",
		"origin/issofa_sofaphysicsapi",
		"rigin/issofa_solvers",
		"origin/issofa_sph",
		"origin/issofa_subsetmultimapping",
		"origin/issofa_tests",
		"origin/master",
		"origin/mimesis",
		"origin/multithreading_mmoge_wip",
		"origin/v16.08",
		"origin/add_rotatableboxroi",
		"origin/beam_mapping",
		"origin/parallelVectorsPlugin",
		"origin/pluginizing_beamFF",
		"origin/scn2python_timerJSONOutput",
		"origin/wip_stateFilter",
		"origin/v18.12.everest",
		"origin/sofabending",
	]
	#return gitrepo

	# selects branches to merge
	def compute_whitelist(self) :
		branches_to_cut = self.gitrepo.getBranches ("-r | grep sofa-framework | sed  's/sofa-framework/origin/'")
		branches = self.gitrepo.getBranches ("-r | grep origin")
		self.whitelist_branches = cut_branches(cut_branches(branches, branches_to_cut), self.blacklist)
		printlist("whitelist branches :", self.whitelist_branches)

	def merge_all (self) :
		self.gitrepo.checkout("mimesis")
		self.gitrepo.reset_hard_to_commit("master")
		faulty_branches, successful_br = [], []
		for branch in self.whitelist_branches :
			headhash = self.gitrepo.get_hash ("HEAD")
			print ("merging " + branch)
			if not self.gitrepo.merge (branch) :
				print ("\t(fatal) fix merge conflict before resuming")
				self.gitrepo.reset_hard_to_commit(headhash)
				faulty_branches.append(branch)
			else :
				successful_br.append(branch)
		gitrepo.checkout("master")
		gitrepo.dump_log()
		return faulty_branches, successful_br

if len(sys.argv) == 2 :

	mimesis_merge = MimesisMerger(sys.argv[1])
	mimesis_merge.compute_whitelist()
	faulty_branches, successful_br = mimesis_merge.merge_all (gitrepo, whitelist_branches)
	printlist("faulty branches :", faulty_branches)
	printlist("successful merges :", successful_br)
	
