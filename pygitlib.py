import os, sys

class GitCmd :
	
	def __init__ (self, repo) :
		self.repo = repo 
		self.log_err = []
		self.log_succ = []
		try :
			os.chdir (repo)
		except :
			print ("(fatal) repo {} does not seem to exist. Check path".format(repo))
			exit()

	def clone (self, url) :
		if os.path.exists (".git/") :
			print ("(fatal) This is already a git repo")
			return False
		pipe = os.popen ("git clone " + url, "r")
		out = "".join(pipe.readlines())
		pipe.close()
		return out
	
	def addRemote (self, name, remote) :
		pipe = os.popen ("git remote add " + name + " " + remote , "r")
		out = "".join(pipe.readlines())
		pipe.close()
		print (out)
		pipe = os.popen ("git remote -v" , "r")
		out = "".join(pipe.readlines())
		pipe.close()
		return out
	
	def command (self, cmd) :
		pipe = os.popen (cmd, "r")
		out = "".join(pipe.readlines())
		pipe.close()
		return out
	
	def reset_hard_to_commit (self, commit_hash) :
		return self.command("git reset --hard {}".format(commit_hash))
	def get_HEAD_hash (self) :
		return self.command("git rev-parse HEAD")

	def getBranches (self, param) :
		pipe = os.popen ("git branch " + param, "r")
		out = [line.strip().split()[0] for line in pipe.readlines()] #"".join(pipe.readlines())
		pipe.close()
		return out
	
	def checkrepo (self, remotename, url) :
		pipe = os.popen ("git config --get remote.{}.url".format(remotename), "r")
		out = "".join(pipe.readlines()).strip()
		pipe.close()
		print (out)
		if out == url :
			print("(success) remote {} found @ {}".format(remotename, url))
			return True
		else :
			print ("(fatal) remote {} is not @ {}".format(remotename, url))
			return False 

	def checkout (self, branch) :
		pipe = os.popen ("git checkout " + branch, "r")
		out = "".join(pipe.readlines()).strip()
		pipe.close()
		return
	
	def commitall (self, message) :
		pipe = os.popen ("git commit -am \'{}\'".format(message), "r")
		out = "".join(pipe.readlines()).strip()
		pipe.close()
		return out

	def push (self, param) :
		pipe = os.popen ("git push " + param, 'r')
		out = "".join(pipe.readlines())
		pipe.close()
		return out

	def merge (self, branch) :
		pipe = os.popen ("git merge " + branch, "r")
		out = [line.strip() for line in pipe.readlines()]
		pipe.close()
		merge_success = True
		if out == [] :
			print ("(fatal) merge error encountred")
			return False
		for o in out :
			# handle conflict
			isconflict = o.find ("CONFLICT") != -1 or o.find("conflict") != -1 or o.find('conflit') != -1 or o.find('CONFLIT') != -1
			if isconflict :
				status, err_msg = "(error) @{}.merge : {}".format(branch, o), "full error message : <<< {} >>>".format("\n".join(out))
				self.log_err.append ((status, err_msg))
				print ("\t" + status)
				return False
			else :
				status = "\t" + "(success) @{}.merge : {}".format(branch, o)
				#print ("\t" + status)
				self.log_succ.append (status)
		return True

	def dump_log (self, err_file="err_log.txt", succ_file="succ_log.txt") :
		if self.log_err != [] :
			err_stream = open (err_file, "w")
			for (status, err_msg) in self.log_err :
				line = status + "\n" + err_msg + "\n\n"
				err_stream.write(line)
			err_stream.close()
		if self.log_succ != [] :
			succ_stream = open (succ_file, "w")
			for status in self.log_succ :
				line = status + "\n"
				succ_stream.write(line)
			succ_stream.close()

	@staticmethod 
	def filterBranchesByRemote (branches, remote) :
		out = []
		for branch in branches :
			if branch.find(remote) != -1 :
				out.append(branch)
		print(out[1:])
		return out[1:]

def cut_branches (tree_a, tree_b) :
	out_tree = []
	for br in tree_a :
		if not (br in tree_b) :
			out_tree.append(br)
	return out_tree

def printlist (label, l) :
	print (label)
	for i in l :
		print("\t" + i)

blacklist = [
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
if len(sys.argv) == 2 :
	gitrepo = GitCmd (sys.argv[1])
	origin = gitrepo.checkrepo ("origin", "https://github.com/mimesis-inria/sofa.git") 
	sofaframework = gitrepo.checkrepo("sofa-framework", "https://github.com/sofa-framework/sofa.git")
	if not origin and not sofaframework:
		print (">>> check remotes, might be missing")
		exit ()

	branches_to_cut = gitrepo.getBranches ("-r | grep sofa-framework | sed  's/sofa-framework/origin/'")
	branches = gitrepo.getBranches ("-r | grep origin")
	whitelist_branches = cut_branches(cut_branches(branches, branches_to_cut), blacklist)
	gitrepo.checkout("mimesis")
	
	printlist("whitelist branches :", whitelist_branches)
	print()

	faulty_branches, successful_br = [], []
	for branch in whitelist_branches :
		headhash = gitrepo.get_HEAD_hash ()
		print ("merging " + branch)
		if not gitrepo.merge (branch) :
			print ("\t(fatal) fix merge conflict before resuming")
			gitrepo.reset_hard_to_commit(headhash)
			faulty_branches.append(branch)
		else :
			successful_br.append(branch)
	gitrepo.checkout("master")
	gitrepo.dump_log()

	print ()
	printlist("faulty branches :", faulty_branches)
	printlist("successful merges :", successful_br)
	
