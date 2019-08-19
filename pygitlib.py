import os, sys

class GitCmd :
	
	def __init__ (self, repo) :
		self.repo = repo 
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

	def getBranches (self, param) :
		pipe = os.popen ("git branch " + param, "r")
		out = [line.strip().split()[0] for line in pipe.readlines()] #"".join(pipe.readlines())
		pipe.close()
		return out
	
	def checkrepo (self, remotename, url) :
		pipe = os.popen ("git config --get remote.{}.url".format(remotename), "r")
		out = "".join(pipe.readlines()).strip()
		pipe.close()
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
			#print (o, '#')
			isconflict = o.find ("CONFLICT") != -1 or o.find("conflict") != -1 or o.find('conflit') != -1 or o.find('CONFLIT') != -1
			if isconflict :
				print ("(error) @{}.merge : {}".format(branch, o))
				print ("full error message : <<< {} >>>".format("".join(out)))
				return False
		return True

	@staticmethod 
	def filterBranchesByRemote (branches, remote) :
		out = []
		for branch in branches :
			if branch.find(remote) != -1 :
				out.append(branch)
		return out


if len(sys.argv) == 2 :
	gitrepo = GitCmd (sys.argv[1])
	#if not gitrepo.checkrepo ("mimesis-inria", "https://github.com/mimesis-inria/sofa.git") :
		#exit ()

	#branches = gitrepo.getBranches ("-r")
	#gitrepo.checkout("mimesis")

	#for branch in GitCmd.filterBranchesByRemote (branches, "mimesis-inria") :
		#input()
		#print ("merging " + branch)
		#if not gitrepo.merge (branch) :
			#print ("(fatal) fix merge conflict before resuming")
			#exit()
	#gitrepo.merge("master")
	
	gitrepo.checkout("-b committest")
	branches = gitrepo.getBranches("-r")
	for branch in GitCmd.filterBranchesByRemote (branches, "origin") :
		print ("merging " + branch)
		if not gitrepo.merge (branch) :
			print ("(fatal) fix merge conflict before resuming")
			exit()
		gitrepo.merge("master")


