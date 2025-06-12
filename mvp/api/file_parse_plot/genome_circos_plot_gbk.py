import matplotlib.pyplot as plt
import base64
from io import BytesIO
import pandas as pd
from pycirclize import Circos
from pycirclize.parser import Genbank
from pycirclize.utils import load_prokaryote_example_file
import numpy as np
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

def parse_data(request_param):
    file_path = request_param['file_path']

    return file_path

def parse_plot(data,request_param):
    file_path = request_param['file_path']

    # Load Genbank file
    # gbk_file = load_prokaryote_example_file("escherichia_coli.gbk.gz")
    # gbk = Genbank("/ssd1/wy/workspace2/leipu/leipu_workspace2/output/prokka/OSP-3-PACBIO-HIFI/S-1-1-assembly.gbk")
    gbk = Genbank(file_path)
   
    # Initialize circos instance
    seqid2size = gbk.get_seqid2size()
    space = 0 if len(seqid2size) == 1 else 2
    circos = Circos(sectors=seqid2size, space=space)
    circos.text("Ligilactobacillus murinus", size=12, r=20)

    seqid2features = gbk.get_seqid2features(feature_type=None)
    seqid2seq = gbk.get_seqid2seq()
    for sector in circos.sectors:
        # Plot outer track with xticks
        major_ticks_interval = 500000
        minor_ticks_interval = 100000
        outer_track = sector.add_track((98, 100))
        outer_track.axis(fc="lightgrey")
        if sector.size >= major_ticks_interval:
            outer_track.xticks_by_interval(
                major_ticks_interval, label_formatter=lambda v: f"{v/ 10 ** 6:.1f} Mb"
            )
            outer_track.xticks_by_interval(minor_ticks_interval, tick_length=1, show_label=False)

        f_cds_track = sector.add_track((90, 97), r_pad_ratio=0.1)
        r_cds_track = sector.add_track((83, 90), r_pad_ratio=0.1)
        rrna_track = sector.add_track((76, 83), r_pad_ratio=0.1)
        trna_track = sector.add_track((69, 76), r_pad_ratio=0.1)

        # Plot Forward CDS, Reverse CDS, rRNA, tRNA
        features = seqid2features[sector.name]
        for feature in features:
            if feature.type == "CDS" and feature.location.strand == 1:
                f_cds_track.genomic_features(feature, fc="red")
            elif feature.type == "CDS" and feature.location.strand == -1:
                r_cds_track.genomic_features(feature, fc="blue")
            elif feature.type == "rRNA":
                rrna_track.genomic_features(feature, fc="green")
            elif feature.type == "tRNA":
                trna_track.genomic_features(feature, color="magenta", lw=0.1)

        # Plot GC content
        gc_content_track = sector.add_track((50, 65))
        seq = seqid2seq[sector.name]
        label_pos_list, gc_contents = gbk.calc_gc_content(seq=seq)
        gc_contents = gc_contents - gbk.calc_genome_gc_content(seq=gbk.full_genome_seq)
        positive_gc_contents = np.where(gc_contents > 0, gc_contents, 0)
        negative_gc_contents = np.where(gc_contents < 0, gc_contents, 0)
        abs_max_gc_content = np.max(np.abs(gc_contents))
        vmin, vmax = -abs_max_gc_content, abs_max_gc_content
        gc_content_track.fill_between(
            label_pos_list, positive_gc_contents, 0, vmin=vmin, vmax=vmax, color="black"
        )
        gc_content_track.fill_between(
            label_pos_list, negative_gc_contents, 0, vmin=vmin, vmax=vmax, color="grey"
        )

        # Plot GC skew
        gc_skew_track = sector.add_track((35, 50))

        label_pos_list, gc_skews = gbk.calc_gc_skew(seq=seq)
        positive_gc_skews = np.where(gc_skews > 0, gc_skews, 0)
        negative_gc_skews = np.where(gc_skews < 0, gc_skews, 0)
        abs_max_gc_skew = np.max(np.abs(gc_skews))
        vmin, vmax = -abs_max_gc_skew, abs_max_gc_skew
        gc_skew_track.fill_between(
            label_pos_list, positive_gc_skews, 0, vmin=vmin, vmax=vmax, color="olive"
        )
        gc_skew_track.fill_between(
            label_pos_list, negative_gc_skews, 0, vmin=vmin, vmax=vmax, color="purple"
        )
    
    fig = circos.plotfig(dpi=200,figsize=(8, 8))
    # plt.figure()
    # circos.figure.set_size_inches(8, 8)  
    # Add legend
    handles = [
        Patch(color="red", label="Forward CDS"),
        Patch(color="blue", label="Reverse CDS"),
        Patch(color="green", label="rRNA"),
        Patch(color="magenta", label="tRNA"),
        Line2D([], [], color="black", label="Positive GC Content", marker="^", ms=6, ls="None"),
        Line2D([], [], color="grey", label="Negative GC Content", marker="v", ms=6, ls="None"),
        Line2D([], [], color="olive", label="Positive GC Skew", marker="^", ms=6, ls="None"),
        Line2D([], [], color="purple", label="Negative GC Skew", marker="v", ms=6, ls="None"),
    ]
    _ = circos.ax.legend(handles=handles, bbox_to_anchor=(0.5, 0.475), loc="center", fontsize=8)
    return plt