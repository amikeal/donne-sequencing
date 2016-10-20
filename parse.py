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
			
			tmp = ''
			for k in range(j):
				tmp += str(grp[i + k])
			
			r.append(tmp)
	
	return r


def process_hashes(dict):
	r1, r2, r3 = {}, {}, {}
	
	# Flatten the list of hashes, adding a name to
	#  an array every time the sequence is seen
	for name, arr in dict.items():
		for h in arr:
			if h in r1:
				r1[h].append(name)
			else:
				r1[h] = [name]
	
	#pprint.pprint(r1)			
	# Take the flattened hash list, and eliminate 
	#  entries that only have one item (no travel)
	for h, arr in r1.items():
		if len(arr) > 1:
			r2[h] = arr
			
	# Eliminate entries that are completely contained
	#  within a larger sequence
	r1 = r2
	count = 0
	for h1, a1 in r1.items():
		remove = False
		for h2, a2 in r2.items():
			if h1 != h2 and h2.find(h1) > -1 and a1 == a2:
				remove = True
				#print "'%s' is inside '%s'" % ( h1, h2 )
		if remove == False:
			r3[h1] = a1
	
	del r1, r2		
	return r3


def translate_seq_hash(h):
	num = len(h) / 2
	ret = []
	j = 0
	for i in range(num):
		ret.append(master[int(h[j:j+2])])
		j += 2
	
	return ret


def tuple_cmp(x, y):
	x_names, x_list = x
	y_names, y_list = y
	
	return len(y_list) - len(x_list)


def main():
	for n in os.listdir('seq'):
		f = open('seq/' + n, "r")
		res = parse_seq_file(f)
		
	h = {}	
	for name, grp in flat.items():
		h[name] = calculate_hashes(grp)
	
	final = []
	p = process_hashes(h)
	for h, arr in p.items():
		k = translate_seq_hash(h)
		final.append( (k, arr) )
	
	print "Finished processing groups... Found", len(p), "unique groups"

	print "Sorting result...\n\n"
	final.sort(tuple_cmp)
	
	print len(p)
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
	

if __name__ == '__main__':
	main()