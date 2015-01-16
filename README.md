# Syllabify
___

Words can be de constructed into utterances, each utterance is a phone. Phones can
be grouped into Consonant types and Vowel types. Vowels have a stress property and
can either carry primary stress, secondary stress or no stress. Vowels also have a length
property, they can either be long vowels like /AH/ in cat, or short vowels like /I/ in kit.

We can use a pronouncing dictionary to get a phonemic representation of a word. Carnegie
Melon University have produced an open source dictionary of North Amercian pronun-
ciations. The dictionary maps to over 125,000 phonemic transcriptions[8], and for some
entries contains multiple phonemic representations.

Consonants and vowels can group together to form a phonological unit called a syllable.
Syllables are formed of two parts: an onset and a rime. The rime of a syllable decom-
poses into two further parts: the nucleus and a coda.

The nucleus is the only mandatory part of the syllable and is usually accommodated by
a vowel[7]. if the onset and coda sections exist they have to be occupied by consonants,
which can either be singular of exist in clusters of 2 or 3.

Under some conditions, there are certain combinations of consonants that cannot appear
in coda and onset. These rules are called phonotactic constraints[7]. McMahon tabulates
6these as follows:

1. If an onset contains a cluster of three consonants, the first consonant must be /S/.
2. /NG/ cannot appear in an onset
3. /V DH Z ZH/ cannot form part of onset clusters
4. /T D TH/ adjoined with /L/ cannot form an onset cluster
5. /H/ cannot appear in a coda
6. /LG/ is not a permissible coda cluster

Syllables must adhere to these rules if they to be well formed. McMahon also defines a
further principle that is used to partition a phoneme string into well formed syllables. it
is the principle of Onset Maximalism:

Onset Maximalism ”Where there is a choice always assign as many consonants as
possible to the onset, and as few as possible to the coda. However, remember that
every word must also consist of a sequence of well formed syllables ”
For each transcribed word, the CMU dictionary returns a phoneme string that is not
partitioned into syllables. If we are to create a system that can compare phonological
units we will need to model the rules of syllabification.