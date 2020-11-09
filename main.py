import os, sys
from pygitlib import *


class MimesisMerger :
	def __init__ (self, repo_dir=".") :
		self.gitrepo = GitCmd (repo_dir)
		origin = self.gitrepo.checkrepo ("origin", "https://github.com/mimesis-inria/sofa.git") 
		sofaframework = self.gitrepo.checkrepo("sofa-framework", "https://github.com/sofa-framework/sofa.git")
		if not origin or not sofaframework:
			print (">>> check remotes, might be missing")
			exit()
		self.gitrepo.fetch()
		self.gitrepo.fetch("--prune")

		self.blacklist = []
		self.mergedbranches = []

	def load_blacklist (self, filepath) :
		try :
			fstream = open (filepath+"blacklistbranches.name", "r")
			self.blacklist = [line.split("\n")[0] for line in fstream.readlines()]
			fstream.close()
			print ("[+] blacklist read")
		except :
			print ("[-] blacklist can't be read")

	def load_mergedbranches (self, filepath) :
		try :
			fstream = open (filepath+"mergedbranches.hash", "r")
			self.mergedbranches = fstream.readlines()
			fstream.close()
			print ("[+] merged branches read")
		except :
			print ("[-] merged branches can't be read")

	# selects branches to merge
	def compute_whitelist(self, path="") :
		branches_to_cut = self.gitrepo.getBranches ("-r | grep sofa-framework | sed  's/sofa-framework/origin/'")
		branches = self.gitrepo.getBranches ("-r | grep origin")
		self.load_blacklist(path)
		self.load_mergedbranches(path)
		whitelist_branches = cut_branches(cut_branches(branches, branches_to_cut), self.blacklist)
		printlist("whitelist branches :", whitelist_branches)
		
		self.whitelist_branches = []
		for branch in whitelist_branches:
			if not self.gitrepo.get_hash(branch) in self.mergedbranches :
				self.whitelist_branches.append (branch)
			else :
				print ("branch {} has already been merged".format(branch))
		printlist("whitelist branches to merge :", self.whitelist_branches)

	def merge_all (self, commitkw="master") :
		self.gitrepo.checkout("mimesis")
		self.gitrepo.reset_hard_to_commit(commitkw)
		faulty_branches, successful_br = [], []
		print ("=========================")
		for branch in self.whitelist_branches :
			headhash = self.gitrepo.get_hash ("HEAD")
			print ("merging " + branch)
			if not self.gitrepo.merge (branch) :
				print ("\t(fatal) fix merge conflict before resuming")
				self.gitrepo.reset_hard_to_commit(headhash)
				faulty_branches.append(branch)
			else :
				successful_br.append(branch)
			print ("=========================")
		self.gitrepo.checkout("master")
		self.gitrepo.dump_log()
		return faulty_branches, successful_br

if len(sys.argv) >= 2 :
	mimesis_merge = MimesisMerger(sys.argv[1])
	mimesis_merge.compute_whitelist(path="/home/omar/projects/tools/pygitlib/")
	faulty_branches, successful_br = [], []
	if len(sys.argv) == 3 :
		faulty_branches, successful_br = mimesis_merge.merge_all (readhash(sys.argv[2]))
	else :
		faulty_branches, successful_br = mimesis_merge.merge_all ()
	printlist("faulty branches :", faulty_branches)
	printlist("successful merges :", successful_br)

