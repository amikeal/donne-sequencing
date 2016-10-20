# # !/usr/bin/python

import os, pprint

# Script parameters
MIN_SEQ = 2
MAX_SEQ = False

# Global vars for soring sequences and mapping data
master = {}
flat = {}
grouped = {}


#
# Load all the objects in the provided file into the 
#  master data structure of all sequences
#
def parse_seq_file(fh):
	name = fh.readline()
	fh.readline() # trash it
	name = name[0:name.find(' SS')]
	flat[name] = []
	grouped[name] = {}
	
	grp = 1
	for ln in fh.readlines():
		if grp not in grouped[name]:
			grouped[name][grp] = []
		if ln[0] == '-':
			grp += 1
		else:
			pnum = int(ln[0:3])
			grouped[name][grp].append( pnum )
			flat[name].append( pnum )
			master[pnum] = ln[4:].strip()


#
# Given a single set of item groups (all the sequence
#  groups in a given file), calculate the 
#
def calculate_hashes(grp):
	r = []
	
	# To avoid seeking outside the array bounds, only iterate
	#  up to the MIN_SEQ distance from the end of the array
	for i in range(len(grp)):
		
		# Calculate the maximum length of the sequences
		if MAX_SEQ == False:
			smax = len(grp) - i
		else:
			smax = MAX_SEQ
		
		# The inner loop specifies how many items are in this 
		#  particular sequence
		for j in range(MIN_SEQ, smax):
			
			tmp = []
			for k in range(j):
				tmp.append(grp[i + k])
			
			r.append(set(tmp))
	
	return r


def process_hashes(dict):
	map1 = SequenceMap()
	
	# Flatten the list of hashes, adding a name to
	#  an array every time the sequence is seen
	for name, arr in dict.items():
		for p_set in arr:
			map1[p_set] = name
	
	# Take the flattened hash list, and eliminate 
	#  entries that only have one item (no travel)
	map1.filter_sequence(lambda x: len(x) < 2)
	
	# Eliminate entries where the group is contained
	#  entirely within a larger group (can only be done 
	#  after the initial collapse and filter)
	map1.remove_subgroups()
	
	return map1


def tuple_cmp(x, y):
	x_names, x_list = x
	y_names, y_list = y
	
	if len(y_list) > len(x_list):
		return 1
	elif len(y_list) == len(x_list):
		if len(y_names) > len(x_names):
			return 1
		elif len(y_names) == len(x_names):
			return 0
		else:
			return -1
	else: 
		return -1
	

def main():
	print "Parsing sequence files..."
	for n in os.listdir('seq'):
		f = open('seq/' + n, "r")
		res = parse_seq_file(f)
	
	print "Calculating all possible poem groups..."
	h = {}	
	for name, grp in flat.items():
		h[name] = calculate_hashes(grp)	
	
	print "Processing poem groups -- collapse duplicates across manuscripts and eliminate single patterns..."
	p = process_hashes(h)
	
	print "Finished processing groups... Found", len(p), "unique groups"
	
	print "Sorting result...\n\n"
	final = p.get_tuples()
	final.sort(tuple_cmp)
	
	#pprint.pprint(p)
	#pprint.pprint(final)
	
	for (names, codes) in final:
		for n in names:
			print n + ', ',
		print
		print '   ',
		for c in codes:
			print c + ', ',
		print "\n"
	

class SequenceMap:
	'''Create a data structure that allows anything (like sets) as the key and an array of strings as the value'''
	
	# a mapping of the sets to the names (multiple names per set)
	mapping = {}
	
	def __init__(self):
		pass
	
	def __getitem__(self, key):
		hsh = self._set2hsh(key)
		if hsh in self.mapping:
			return self.mapping[hsh]
		else:
			return False
	
	def __setitem__(self, key, value):
		# check for existence in the catalog
		hsh = self._set2hsh(key)
		
		# either append the value to the existing record, or create a new one
		if hsh in self.mapping:
			self._add_to_map(hsh, value)
		else:
			self._create_map(hsh, value)
		
		# be nice
		return True

	def __delitem__(self, key):
		hsh = self._set2hsh(key)
		if hsh in self.mapping:
			self._delete(hsh)
			return True
		else:
			return False
		
	def __contains__(self, key):
		return self._set2hsh(key) in self.mapping
	
	def __iter__(self):
		return self
	
	def __len__(self):
		return len(self.mapping)
	
	def _set2hsh(self, set_obj):
		tmp = ''
		for i in set_obj:
			tmp += str(i)
		return tmp
	
	def _hsh2set(self, hsh_str):
		ret = []
		j = 0
		for i in range(len(hsh_str) / 2):
			ret.append(int(hsh_str[j:j+2]))
			j += 2
		return set(ret)
	
	def _hsh2names(self, hsh_str):
		ret = []
		j = 0
		for i in range(len(hsh_str) / 2):
			ret.append(master[int(hsh_str[j:j+2])])
			j += 2
		return ret
	
	def _add_to_map(self, idx, value):
		'''String-or-List safe append'''
		if value in self.mapping[idx]:
			return True
		if isinstance(value, list):
			self.mapping[idx] += value
		else:
			self.mapping[idx].append(value)
		
	def _create_map(self, idx, value):
		'''String-or-List safe val creation'''
		if isinstance(value, list):
			self.mapping[idx] = value
		else:
			self.mapping[idx] = [value]
	
	def _delete(self, idx):
		del(self.mapping[idx])
	
	def next(self):
		if self.i not in self.catalog:
			raise StopIteration
		self.i += 1
		return (self.catalog[self.i], self.mapping[self.i])
	
	def filter_sequence(self, func):
		for idx in self.mapping.keys():
			if func(self.mapping[idx]):
				self._delete(idx)
	
	def remove_subgroups(self):
		m1, m2 = self.mapping, self.mapping
		for h1, a1 in m1.items():
			for h2, as2 in m2.items():
				if h1 != h2 and self._hsh2set(h1).issubset(self._hsh2set(h2)) and self.mapping[h1] == self.mapping[h2]:
					self._delete(h1)
					break
	
	def pprint(self):
		for hsh, arr in self.mapping.items():
			print self._hsh2names(hsh)
			print "   ", arr, "\n"
	
	def get_tuples(self):
		ret = []
		for hsh, arr in self.mapping.items():
			ret.append( (self._hsh2names(hsh), arr) )
		return ret
	


if __name__ == '__main__':
	main()