import argparse
import json

def parse_command_line():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(prog='main.py', formatter_class=argparse.RawTextHelpFormatter)

    general_group = parser.add_argument_group('General')

    # Input files commands
    general_group.add_argument('--unpaired',
        help='Input fastq name (unpaired)')
    general_group.add_argument('--forward',
        help='Input fastq name (paired-end, forward)')
    general_group.add_argument('--reverse',
        help='Input fastq name (paired-end, reverse)')
    general_group.add_argument('--input_dir',
        help='Path to input folder, default: "/input/" for docker image',
        default='/input/')
    general_group.add_argument('--load_config',
        help='Use JSON file for configuration (overwrites command line parameters)',
        action='store_true')
    general_group.add_argument('--config',
        help='JSON config file path, default: "/input/config.json" for docker image',
        default='/input/config.json')
    general_group.add_argument('--steps',
        help='Set of steps to perform in analysis (default: merging qc filter cluster virus_search):\n'+
        '\tmerging: Paired-end reads merging using fastp, always performed\n'+
        '\tqc: Quality filtering using fastp\n'+
        '\tfilter: Filter fastq by mapping reads on the reference genomes using bowtie2\n'+
        '\tcluster: Fasta file clusterization using vsearch\n'+
        '\tvirus_search: Search for virus sequences, always performed\n'+
        '\tadditional_search: Search for sequences that were not identified at virus_search step\n'+
        '\run_nn_test: Run Deepac-vir (doi.org/10.1093/nargab/lqab004) and ViraMiner (doi:10.1371/journal.pone.0222271) prediction for unidentified sequences\n'+
        '\tall: Perform all steps',
        nargs='+',
        default=['qc', 'merging', 'filter', 'cluster', 'virus_search'])

    # Output files commands
    general_group.add_argument('--output_dir',
        help='Path to output folder, default: "/output/" for docker image',
        default='/output/')

    # Other commands
    general_group.add_argument('--num_threads',
        help='Number of threads',
        default="1")
    general_group.add_argument('--keep_temp',
        help='Keep temporary files in output folder, default: false',
        action='store_true')

    # Merging commands
    merge_group = parser.add_argument_group('Merging (fastp)')
    merge_group.add_argument('--do_not_save_unmerged',
        help="Do not save unmerged reads for processing, default: disabled",
        action='store_true')
    
    # Quality control commands
    qc_group = parser.add_argument_group('Quality control (fastp)')
    qc_group.add_argument('--adapters',
        help='Path to the file with the adapter sequences for fastp, default: /input/adapters.fa for docker image',
        default="/input/adapters.fa")
    qc_group.add_argument('--average_qual',
        help='Quality score mean threshold for filtering with fastp, default: 20',
        default=20)
    qc_group.add_argument('--min_len',
        help='Filter sequences shorter than min_len, default 36',
        default=36)
    qc_group.add_argument('--complexity_threshold',
        help='The threshold value (between 0 and 100) for filtering low complexity sequence reads, default: 30',
        default=30)
    qc_group.add_argument('--cut_front',
        help="Move a sliding window from 5' to 3', drop the bases in the window if its mean quality is below cut_mean_quality, default disabled",
        action='store_true')
    qc_group.add_argument('--cut_tail',
        help="Move a sliding window from 3' to 5', drop the bases in the window if its mean quality is below cut_mean_quality, default disabled",
        action='store_true')
    qc_group.add_argument('--cut_right',
        help="move a sliding window from 5' to 3', if meet one window with mean quality < threshold, drop the bases in the window and the right part, default disabled",
        action='store_true')
    qc_group.add_argument('--cut_window_size',
        help="The window size option, default 4",
        default=4)
    qc_group.add_argument('--cut_mean_quality',
        help='The mean quality requirement option by cut_front, cut_tail, and cut_right, default 20',
        default=20)

    # Filtering commands
    filtering_group = parser.add_argument_group('Filtering')
    filtering_group.add_argument('--ref_names',
        help='Reference genomes for filtering from database folder, default=[]', nargs='+', default=[])

    # Clustering commands
    clustering_group = parser.add_argument_group('Clustering')
    clustering_group.add_argument('--identity',
        help='Sequence identity threshold for clustering using vsearch, default: 0.9',
        default="0.9")

    # Search commands
    search_group = parser.add_argument_group('Search')
    search_group.add_argument('--virus_search_s1_evalue_n',
        help='Megablast search evalue threshold for virus search step 1, default = 1e-3',
        default="1e-3")
    search_group.add_argument('--virus_search_s1_evalue_p',
        help='Diamond search evalue threshold for virus search step 1, default = 1e-3',
        default="1e-3")
    search_group.add_argument('--virus_search_s2_evalue_n',
        help='Megablast search evalue threshold for virus search step 2, default = 1e-10',
        default="1e-10")
    search_group.add_argument('--virus_search_s2_evalue_p',
        help='Diamond search evalue threshold for virus search step 2, default = 1e-10',
        default="1e-10")
    search_group.add_argument('--additional_search_evalue_n',
        help='Megablast evalue threshold for additional search stage, default = 1e-10',
        default="1e-10")
    search_group.add_argument('--additional_search_evalue_p',
        help='Diamond evalue threshold for additional search stage, default = 1e-10',
        default="1e-10")
    search_group.add_argument('--max_target_seqs',
        help=' Number of database sequences to show alignments for blastn and diamond, default = 25',
        default="10")
    search_group.add_argument('--virus_nucl_db_name',
        default='virus_nucl',
        help='Nucleotide database with virus sequences, default: virus_nucl')
    search_group.add_argument('--virus_prot_db_name',
        default='virus_prot_diamond',
        help='Protein database with virus sequences, default: virus_prot_diamond')
    search_group.add_argument('--nucl_db_name',
        default='nt',
        help='Nucleotide database with various sequences for search, default: nt')
    search_group.add_argument('--prot_db_name',
        default='nr_diamond',
        help='Protein database with various sequences for search, default: nr_diamond')
    search_group.add_argument('--db_dir',
        help='Full path to database folder, default: "/database/" for docker image',
        default='/database/')
    
    # DeePaC-vir and ViraMiner test commands
    nn_group = parser.add_argument_group('DeePaC-vir and ViraMiner tests')
    nn_group.add_argument('--deepac_model',
        help='DeePaC-vir model: CNN or LSTM, default = LSTM',
        default="LSTM")

    return parser.parse_args()

def get_arguments():
    # get arguments from command line
    args_namespace = parse_command_line()
    args = vars(args_namespace)

    # read configuartion file if specified
    if args_namespace.load_config:
        json_dict = {}
        with open(args_namespace.config) as json_file:
            json_dict = json.load(json_file)

        # overwrite configurations from config
        for argument in args:
            if argument in json_dict:
                args[argument] = json_dict[argument]

    return args
