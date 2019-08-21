import os, sys, datetime

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

	# clone a repo
	def clone (self, url) :
		if os.path.exists (".git/") :
			print ("(fatal) This is already a git repo")
			return False
		pipe = os.popen ("git clone " + url, "r")
		out = "".join(pipe.readlines())
		pipe.close()
		return out
	
	# add a remote by name
	def addRemote (self, name, remote) :
		pipe = os.popen ("git remote add " + name + " " + remote , "r")
		out = "".join(pipe.readlines())
		pipe.close()
		print (out)
		pipe = os.popen ("git remote -v" , "r")
		out = "".join(pipe.readlines())
		pipe.close()
		return out
	
	# runs any command in popen
	def command (self, cmd) :
		pipe = os.popen (cmd, "r")
		out = "".join(pipe.readlines())
		pipe.close()
		return out

	# git fetch
	def fetch (self, param="") :
		return self.command("git fetch {}".format(param))
	# for hard reseting branches
	def reset_hard_to_commit (self, commit_hash) :
		return self.command("git reset --hard {}".format(commit_hash))
	# for getting a branche's hash
	def get_hash (self, branch) :
		return self.command("git rev-parse {}".format(branch))

	# git branch
	def getBranches (self, param) :
		pipe = os.popen ("git branch " + param, "r")
		out = [line.strip().split()[0] for line in pipe.readlines()] #"".join(pipe.readlines())
		pipe.close()
		return out
	
	#check if remote is present
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

	# git checkout
	def checkout (self, branch) :
		pipe = os.popen ("git checkout " + branch, "r")
		out = "".join(pipe.readlines()).strip()
		pipe.close()
		return
	
	# git commit -am
	def commitall (self, message) :
		pipe = os.popen ("git commit -am \'{}\'".format(message), "r")
		out = "".join(pipe.readlines()).strip()
		pipe.close()
		return out

	# git push
	def push (self, param) :
		pipe = os.popen ("git push " + param, 'r')
		out = "".join(pipe.readlines())
		pipe.close()
		return out

	# tries merging otherwise hard resets the branch
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

	# dumps logs in text files
	def dump_log (self, err_file="err_log.txt", succ_file="succ_log.txt") :
		if self.log_err != [] :
			err_stream = open (err_file, "w")
			err_stream.write ("{}\n".format(datetime.datetime.now()))
			for (status, err_msg) in self.log_err :
				line = status + "\n" + err_msg + "\n\n"
				err_stream.write(line)
			err_stream.close()
		if self.log_succ != [] :
			succ_stream = open (succ_file, "w")
			succ_stream.write ("{}\n".format(datetime.datetime.now()))
			for status in self.log_succ :
				line = status + "\n"
				succ_stream.write(line)
			succ_stream.close()

	# get branches by remote
	@staticmethod 
	def filterBranchesByRemote (branches, remote) :
		out = []
		for branch in branches :
			if branch.find(remote) != -1 :
				out.append(branch)
		print(out[1:])
		return out[1:]
