import matplotlib.pyplot as plt
from dna_features_viewer import BiopythonTranslator
from Bio import SeqIO
import numpy as np
# https://edinburgh-genome-foundry.github.io/DnaFeaturesViewer/index.html
def parse_data(request_param):
    file_path = request_param['file_path']

    return request_param

def parse_plot(data,request_param):
    file_path = data['file_path']
    # REGION_START = 1000
    # REGION_END = 10000
    REGION_START = data['REGION_START']
    REGION_END = data['REGION_END']
    graphic_record = BiopythonTranslator().translate_record(file_path)
    sub_record = graphic_record.crop((REGION_START, REGION_END))
    sub_record.plot( with_ruler=False, strand_in_label_threshold=4)
    
    # fig, (ax1, ax2) = plt.subplots(
    #     2, 1, figsize=(12, 3), sharex=True, gridspec_kw={"height_ratios": [4, 1]}
    # )

    # # PLOT THE RECORD MAP
    # record = SeqIO.read(file_path, "genbank")
    # record = record[REGION_START:REGION_END]
    # graphic_record = BiopythonTranslator().translate_record(record)
    # graphic_record.plot(ax=ax1, with_ruler=False, strand_in_label_threshold=4)

    # # PLOT THE LOCAL GC CONTENT (we use 50bp windows)
    # gc = lambda s: 100.0 * len([c for c in s if c in "GC"]) / 50
    # xx = np.arange(len(record.seq) - 50)
    # yy = [gc(record.seq[x : x + 50]) for x in xx]
    # ax2.fill_between(xx + 25, yy, alpha=0.3)
    # ax2.set_ylim(bottom=0)
    # ax2.set_ylabel("GC(%)")
    return plt