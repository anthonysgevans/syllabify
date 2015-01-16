import re, copy, sys, random
from cmuparser import CMUtranscribe
from syllable_types import Cluster, Consonant, Vowel, Empty, Rime, Syllable
from phoneme_types import * 

phoneme_classify = re.compile('''
						((?P<Vowel>AO|UW|EH|AH|AA|IY|IH|UH|AE|AW|AY|ER|EY|OW|OY) 
						|(?P<Consonant>CH|DH|HH|JH|NG|SH|TH|ZH|Z|S|P|R|K|L|M|N|F|G|D|B|T|V|W|Y\d*)
						)
						((?P<Stress>0|1|2)
						)?
						''',re.VERBOSE)

def factory(phoneme):
	# argument is a string of phonemes e.g.'B IH0 K AH0 Z'
	phoneme_list = phoneme.split()

	def phoneme_fact(phoneme):
		# match against regular expression
		phoneme_feature = re.match(phoneme_classify,phoneme).groupdict()

		#input is phoneme feature dictionary 
		if phoneme_feature['Consonant']:
			# create return consonant object
			return Consonant(**phoneme_feature)

		elif phoneme_feature['Vowel']:
			# retun vowel object
			return Vowel(**phoneme_feature)
		else:
			# unkown phoneme class
			raise Exception('unkown Phoneme Class: cannot create appropriate Phoneme object')


	def cluster_fact(cluster_list, phenome):

		current_cluster = cluster_list.pop()
		'''Consonants must be grouped together into clusters '''
		if current_cluster.type() == Consonant and type(phenome) == Consonant or current_cluster.type() == None:
			# Adjacent phenomes of type consonant belong to the same cluster, if the 
			# current cluster.last_phenome == None that means it's empty
			# update current cluster
			current_cluster.add_phenome(phenome)
			# append to cluster list 
			cluster_list.append(current_cluster)
			# return cluster list
			return cluster_list
		else:
			#Create new cluster add phenome to it and return 
			cluster_list.append(current_cluster)
			cluster_list.append(Cluster(phenome))
			return cluster_list


	def syllable_fact(syllable_list, cluster):
		syllable = syllable_list.pop()
		push = syllable_list.append

		if syllable.onset_is_empty() and syllable.nucleus_is_empty() and cluster.type() == Consonant:
			# cluster is assigned to the onset of the current syllable
			syllable.set_onset(cluster)
			push(syllable)
			return syllable_list

		if  cluster.type() == Vowel:
				if syllable.has_nucleus():
					# this cluster becomes the nucleus of a new syllable
					# push current syllable back on the syllable stack 
					push(syllable)
					# create new syllable 
					new_syllable = Syllable(nucleus = cluster)
					# push new_syllable onto the stack 
					push(new_syllable)
					return syllable_list
				else:
					# syllable does not have nucleus so this cluster becomes the 
					# nucleus on the current syllable
					syllable.set_nucleus(cluster)
					push(syllable)
					return syllable_list

		if syllable.has_nucleus() and cluster.type() == Consonant:
				if syllable.has_coda():
					# this cluster is the onset of the next syllable
					new_syllable = Syllable(onset = cluster)
					# push syllable onto stack 
					push(new_syllable)
					return syllable_list
				elif syllable.coda_is_empty():
					# Onset Maximalism dictates we push consonant clusters to 
					# the onset of the next syllable, unless the nuclear cluster is LIGHT and 
					# has primary stress

					maximal_coda, maximal_onset = onset_rules(cluster)

					if syllable.is_short() and syllable.get_stress() == '1' and not maximal_coda:
						# The syllable is LIGHT and the consonat cluster is therefore ambisyllabic
						# it belongs to both the current syllable and the next 
						# coda is empty 
						light_coda = coda_rules(maximal_onset)
						syllable.set_coda(light_coda) 
						push(syllable)
						new_syllable = Syllable(onset = maximal_onset)
						push(new_syllable)
						return syllable_list
					else:
						# add cluster only to the next syllable
						if maximal_coda:
							syllable.set_coda(maximal_coda)
							push(syllable)
						else:
							push(syllable)
						if maximal_onset:
							new_syllable = Syllable(onset = maximal_onset)
						else:
							new_syllable = Syllable()
						push(new_syllable)
						return syllable_list  
			
	def check_last_syllable(syllable_list):
		# the syllable algorithm may assign a consanant cluster to a Syllable that does not have
		# a nucleus, this is not allowed in the English language. 

		# check the last syllable
		syllable = syllable_list.pop()
		push = syllable_list.append

		if syllable.nucleus_is_empty():
			if syllable.has_onset():
				# pop the previous syllable
				prev_syllable = syllable_list.pop()
				onset = syllable.get_onset()
				# set the coda of the previous syllable to the value of theorphan onset
				if prev_syllable.has_coda():
					#add phoneme
					coda_cluster = prev_syllable.get_coda()
					if coda_cluster != onset:
						for phoneme in onset.phoneme_list:  coda_cluster.add_phoneme(phoneme)
					# for phoneme in phonemes: coda_cluster.add_phoneme(phoneme)
				else:
					prev_syllable.set_coda(onset)
				push(prev_syllable)
		else:
			# There is no violation, push syllable back on the stack 
			push(syllable)
		
		return syllable_list					


	# Create a list of phoneme clusters from phoneme list
	cluster_list = reduce(cluster_fact, map(phoneme_fact, phoneme_list),[Cluster()])
	
	# Apply syllable creation rules to list of phenome clusters
	syllable_list = reduce(syllable_fact, cluster_list, [Syllable()])

	# Validate last syllable, and return completed syllable list  
	return check_last_syllable(syllable_list)


def coda_rules(cluster):
	''' checks if the cluster is a valid onset or whther it needs to be split'''

	coda_cluster = copy.deepcopy(cluster)
	phonemes = map(str, coda_cluster.get_phoneme())
	
	def _split_and_update(phoneme, phonemes = phonemes, coda_cluster = coda_cluster):
		index = phonemes.index(phoneme)
		# split on phoneme and discar the rest
		head = coda_cluster.phoneme_list[:index-1]
		#update cluster
		coda_cluster.phoneme_list = head
		#update string list
		phonemes = phonemes[:index-1]

		return (phonemes, coda_cluster)

	#rule 1 - no /HH/ is coda 
	if HH in phonemes:
		phonemes, coda_cluster = _split_and_update(HH)
	
	#rule 2 - no glides in coda
	if L in phonemes:
		phonemes, coda_cluster = _split_and_update(L)
	
	if R in phonemes:
		phonemes, coda_cluster = _split_and_update(R)
	
	if W in phonemes:
		phonemes, coda_cluster = _split_and_update(W)
	
	if Y in phonemes:
		phonemes, coda_cluster = _split_and_update(Y)

	#rule 3 - if complex coda second consonant must not be
	# /NG/ /ZH/ /DH/
	if len(phonemes) > 1 and phonemes[1] in [NG,DH,ZH]:
	
		phoneme = coda_cluster.phoneme_list[1]
		# update cluster 
		coda_cluster.phoneme_list = [phoneme]
		#update string list
		phonemes = phonemes[0:1]
		

	if coda_cluster.phoneme_list == []:
		coda_cluster = None

	return coda_cluster


def onset_rules(cluster):
	''' checks if the cluster is a valid onset or whther it needs to be split'''


	phonemes = map(str, cluster.get_phoneme())
	coda_cluster = Cluster()

	def _split_and_update(phoneme, phonemes = phonemes, coda_cluster = coda_cluster):
		#_get index of phoneme
		index = phonemes.index(phoneme)
		# split on phoneme and add tail coda cluster
		tail = cluster.phoneme_list[:index]
		# remaining phonemes
		head = cluster.phoneme_list[index+1:]
		#extend list
		coda_cluster.phoneme_list.extend(tail)
		#update cluster
		cluster.phoneme_list = head
		#update string list
		phonemes = phonemes[index+1:]
		
		return (phonemes, coda_cluster)
		
	
	def _remove_and_update(phonemes = phonemes, coda_cluster = coda_cluster):
		head = cluster.phoneme_list[0]
		rest = cluster.phoneme_list[1:]
		#extend list
		coda_cluster.phoneme_list.extend([head])
		#update cluster
		cluster.phoneme_list = rest
		#update string list
		phonemes = phonemes[1:]

		return (phonemes, coda_cluster)


	#rule 1 - /NG/ cannot exist in a valid onset
	# does /NG? exist? split on NG add NG to coda
	if NG in phonemes:
		phonemes, coda_cluster = _split_and_update(NG)
		
	#rule 2a - no affricates in complex onsets
	# /CH/ exist? split on affricate
	if CH in phonemes: 
		phonemes, coda_cluster = _split_and_update(CH)

	#rule 2b - no affrictes in complex onsets
	# /JH/ exist? split on affricate
	if JH in phonemes:
		phonemes, coda_cluster = _split_and_update(JH)

	#rule 3 - first consonant in a complex onset must be obstruent
	# if first consonant stop or fricative or nasal 
	if len(phonemes) > 1 and not phonemes[0] in [B,D,G,K,P,T,DH,F,S,SH,TH,V,ZH,M,N]:
		phonemes, coda_cluster = _remove_and_update()
		

	#rule 4 - second consonant in a complex onset must be a voiced obstruent
	# if not OBSTRUENT and VOICED? split on second consonant
	if len(phonemes) > 1 and not phonemes[1] in [B,M,V,D,N,Z,ZH]:
		phonemes, coda_cluster = _remove_and_update()

	#rule 5 - if first consonant in a omplex onmset is not /s/
	# the second consonant must be liquid or glide /L/ /R/ /W/ /Y/
	if len(phonemes) > 1 and not phonemes[0] == S and not phonemes[1] in [L,R,W,Y]:
		phonemes, coda_cluster = _remove_and_update()


	if coda_cluster.get_phoneme() == []:
		coda_cluster = None
	
	if cluster.get_phoneme() == []:
		cluster = None

	return (coda_cluster, cluster)



''' Public Method '''
def generate(word):
	phoneme_list = CMUtranscribe(word)
	if phoneme_list:
		return map(factory, phoneme_list)
	else: 
		return None


''' Test '''
def get_raw(word):
	return CMUtranscribe(word)

def test():
	words = open('./CMU_dictionary/american-english')
	words = words.readlines()

	for i in range(3): 
		word = random.choice(words)[:-1]
		syllable = generate(word)
		raw = get_raw(word)
		if syllable: 
			counter = 0

			for s in syllable:
				counter += 1
				word += '\n' + str(counter) + ': ' + str(map(str,s)) 
			print word
			for w in raw:
			 	print 'raw: ', w
			print '\n'



if __name__ == '__main__':
	try:
		word = sys.argv[1]
		syllable = generate(word)
		raw = get_raw(word)
		if syllable: 
			counter = 0
			for s in syllable:
				counter += 1
				word += '\n' + str(counter) + ': ' + str(map(str,s)) 
			print word
			for w in raw:
			 	print 'raw: ', w
			print '\n'
	except: 
		test()
	
