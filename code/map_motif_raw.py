#!/usr/bin/env python
#map_motif.py
#Ciera Martinez
import sys
import os
import re
import pandas as pd
import numpy as np
import os, sys
from Bio import motifs
from Bio import SeqIO 
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.Alphabet import IUPAC, generic_dna, generic_protein
from collections import defaultdict

#####################
## sys Inputs - to do
#####################

## read in alignment and motif 
try:
    alignment = list(SeqIO.parse(sys.argv[1], "fasta"))
except:
    print ("ERROR This is not a fasta alignment file")
    sys.exit()
try:
    motif = motifs.read(open(sys.argv[2]), "pfm")
except:
    print ("ERROR This is not a pfm file")
    sys.exit()
try:
    threshold = sys.argv[3]
except IndexError:
    threshold = -10000

# Used later when marking output file
alignment_file_name =  os.path.basename(sys.argv[1])
motif_file_name =  os.path.basename(sys.argv[2])

print ("alignment file: " + alignment_file_name)
print ("motif file: " + motif_file_name)

raw_sequences = []
for record in alignment:
    raw_sequences.append(SeqRecord(record.seq.ungap("-"), id = record.id))

## make raw sequences all IUPAC.IUPACUnambiguousDNA()
raw_sequences_2 = []
for seq in raw_sequences:
    raw_sequences_2.append(Seq(str(seq.seq), IUPAC.IUPACUnambiguousDNA()))

#####################
## Motifs
## see http://biopython.readthedocs.io/en/latest/Tutorial/chapter_motifs.html#position-specific-scoring-matrices
#####################

pwm = motif.counts.normalize(pseudocounts=0.0) # Doesn't change from pwm
pssm = pwm.log_odds()
motif_length = len(motif) #for later retrival of nucleotide sequence

######################
## Searching for Motifs in Sequences
######################

## Returns a list of arrays with a score for each position
## This give the score for each position
## If you print the length you get the length of the sequence minus TFBS length. 

pssm_list = [ ]
for seq in raw_sequences_2:
    pssm_list.append(pssm.calculate(seq))

########################## 
## Automatic Calculation of threshold
##########################

## Ideal to find something that automatically calculates, as
## opposed to having human choosing threshold

## Approximate calculation of appropriate thresholds for motif finding 
## Patser Threshold
## It selects such a threshold that the log(fpr)=-ic(M) 
## note: the actual patser software uses natural logarithms instead of log_2, so the numbers 
## are not directly comparable. 

distribution = pssm.distribution(background=motif.background, precision=10**4)
patser_threshold = distribution.threshold_patser() #for use later

## for sys.out
## print("Patser Threshold is %5.3f" % patser_threshold) # Calculates Paster threshold. 

###################################
## Searching for motif in all raw_sequences
#################################

raw_id = []
for seq in raw_sequences:
    raw_id.append(seq.id)

record_length = []
for record in raw_sequences_2:
    record_length.append(len(record))

position_list = []
for i in range(len(raw_id)):
    for position, score in pssm.search(raw_sequences_2[i], threshold = -50):
        positions = {'species': raw_id[i], 'score':score, 'position':position, 'seq_len': record_length[i] }
        position_list.append(positions)
        
position_DF = pd.DataFrame(position_list)

#############################
## Add strand and pos position information as columns to position_DF
#############################

position_list_pos = []
for i, x in enumerate(position_DF['position']):
    if x < 0:
       position_list_pos.append(position_DF.loc[position_DF.index[i], 'seq_len'] + x)
    else:
       position_list_pos.append(x)

## append to position_DF
position_DF['raw_position'] = position_list_pos
    
## strand Column
strand = []
for x in position_DF['position']:
    if x < 0:
       strand.append("negative")
    else:
       strand.append("positive")
    
## append to position_DF
position_DF['strand'] = strand
position_DF = position_DF.sort_values(by=['species','raw_position'], ascending=[True, False])

## Write out Files
print ("Success!!")
print ("The output csv file is located at: " + os.getcwd())
print ("Under the name: map_motif" + alignment_file_name + "-" + motif_file_name + ".csv")
position_DF.to_csv('map_motif' + alignment_file_name + "-" + motif_file_name + ".csv", sep='\t')