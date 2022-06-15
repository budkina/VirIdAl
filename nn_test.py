import os
import sys
import logging
import pandas as pd
import numpy as np
from subprocess import call
from Bio import SeqIO

def run_deepac(filename_input, filename_output, model):
    ### Deepac-vir ###
    records = list(SeqIO.parse(filename_input, "fasta"))
    ids = [record.id for record in records]
    if model == 'CNN':
        if call(f'deepac-vir predict -r {filename_input}', shell=True)!=0:
            logging.error(f"deepac-vir predict -r {filename_input} failed")
            sys.exit()
    elif model == 'LSTM':
        if call(f'deepac-vir predict -s {filename_input}', shell=True)!=0:
            logging.error(f"deepac-vir predict -r {filename_input} failed")
            sys.exit()
    else:
        logging.error(f"Unknown deepac-vir model {model}")
        sys.exit()
    deepac_output = os.path.splitext(filename_input)[0]+"_predictions.npy"
    scores = np.load(deepac_output)
    deepac_results = pd.DataFrame({'id': ids, 'score' : scores})
    deepac_results.to_csv(filename_output+"_deepac.csv", sep = '\t')

def run_viraminer(filename_input, filename_output):
    ### ViraMiner ###
    records = list(SeqIO.parse(filename_input, "fasta"))
    ids = []
    seqs = []
    n = 300
    for record in records:
        seq = str(record.seq).upper()
        if len(seq) < n:
            continue
        seq_chunks = [seq[i:i+n] for i in range(0, len(seq), n)]
        for i,seq_chunk in enumerate(seq_chunks):
            if len(seq_chunk) == n:
                ids.append(f"{record.id}_{i}")
                seqs.append(seq_chunk)
    filename_input_virminer = filename_input + "_viraminer" 
    virminer_input_df = pd.DataFrame({'ids':ids, 'seqs':seqs, 'labels':0})
    virminer_input_df.to_csv(filename_input_virminer, sep = ',', header = False, index = None)
    if call(f'conda run -n python2_env python /ViraMiner/predict_only.py --input_file  {filename_input_virminer} --model_path /ViraMiner/final_ViraMiner/final_ViraMiner_afterFT.hdf5', shell=True)!=0:
        logging.error(f"ViraMiner predict {filename_input_virminer} failed")
        sys.exit()
    if call(f'cp /ViraMiner/final_ViraMiner/final_ViraMiner_afterFT_TEST_predictions.txt  .', shell=True)!=0:
        logging.error(f"copy ViraMiner result failed")
        sys.exit()
    viraminer_preds = pd.read_csv("final_ViraMiner_afterFT_TEST_predictions.txt", header = None)
    viraminer_results = pd.DataFrame({'id' : ids, 'score' : viraminer_preds[0]})
    viraminer_results.to_csv(filename_output , sep = '\t')