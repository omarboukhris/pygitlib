#!/usr/bin/env python3
import os, sys
from pygitlib import *

def help():
	print(
	'''
		pygitlib/main.py is a script to keep the MIMESIS's team SOFA repository up to date.
		It is supposed to merge all compatible branches of the remote into our mimesis branch.
		
		Usage:
			>> mimesis_merger.py [optinonal-sofa-commit-hash]

		By default, every branch is merged into sofa-framework latest commit.
		If an optionnal sofa commit hash is given, the merge will be performed into this specific commit.
		For any questions, be sure to ask:
			- Omar Boukhris (@omarboukhris)
			- Pedro Perrusi (@pedroperrusi)

	'''
	)

class MimesisMerger :
	def __init__ (self, repo_dir=os.environ.get("SOFA_WORK_DIRECTORY") + "/sofa/") :
		self.gitrepo = GitCmd (repo_dir)
		origin = self.gitrepo.checkrepo ("origin", "git@github.com:mimesis-inria/sofa.git") 
		sofaframework = self.gitrepo.checkrepo("sofa-framework", "https://github.com/sofa-framework/sofa.git")
		if not origin or not sofaframework:
			print (">>> Expected remotes not found, add them to the git project? [y/n]")
			answer = input('--> ').strip()  
			if answer[0] == 'y':
				self.gitrepo.addRemote("origin", "git@github.com:mimesis-inria/sofa.git")
				self.gitrepo.addRemote("sofa-framework", "https://github.com/sofa-framework/sofa.git")
			else:
				print('Exiting mimesis_merger...')
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
		#self.gitrepo.checkout("master")
		self.gitrepo.dump_log(
			err_file=os.environ.get("SOFA_WORK_DIRECTORY") + "/mimesiscript/pygitlib/err_log.txt", 
			succ_file=os.environ.get("SOFA_WORK_DIRECTORY") + "/mimesiscript/pygitlib/succ_log.txt")
		return faulty_branches, successful_br
	
	def push(self) :
		self.gitrepo.push("--force origin mimesis") 

if __name__ == "__main__":
	if len(sys.argv) > 1 and sys.argv[1] == '-h':
		help()
		exit()	
	mimesis_merge = MimesisMerger()
	mimesis_merge.compute_whitelist(path=os.environ.get("SOFA_WORK_DIRECTORY") + "/mimesiscript/pygitlib/")
	faulty_branches, successful_br = [], []
	if len(sys.argv) == 2 :
		faulty_branches, successful_br = mimesis_merge.merge_all (readhash(sys.argv[1]))
	else :
		faulty_branches, successful_br = mimesis_merge.merge_all ()
	mimesis_merge.push()
	printlist("faulty branches :", faulty_branches)
	printlist("successful merges :", successful_br)
