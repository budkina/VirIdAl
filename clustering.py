from subprocess import call
import os
import sys
import logging

class Cluster:
    """FASTA file clusterization"""
    def __init__(self,
        filename_gen,
        identity,
        threads):
        """Init cluster submodel"""
        self.filename_gen = filename_gen
        self.identity = identity
        self.threads = threads

    def do_cluster(self, fasta):
        """Cluster input fasta file"""
        logging.info("Clustering with vsearch")
        clustered_filename = self.filename_gen.compose_filename('clustered.fasta',True)

        if call(f"""vsearch --cluster_fast {fasta} --threads {self.threads} \
            --id {self.identity} --centroids {clustered_filename}""", shell=True)!=0:
            logging.error("Clustering with vsearch failed")
            sys.exit()

        if not os.path.isfile(clustered_filename):
            logging.error("Clustered file does not exist")
            sys.exit()
            
        return clustered_filename

