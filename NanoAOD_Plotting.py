import argparse
import array
import ROOT
import glob
import pandas as pd
import os
import pprint
import time
import numpy as np
import math
import h5py
import matplotlib.pyplot as plt
import itertools
from matplotlib.ticker import LogLocator
import matplotlib.lines as mlines

ROOT.gROOT.SetBatch(True)



path = "/pnfs/psi.ch/cms/trivcat/store/user/zoghafoo/crabsubmission_files/selEvents_new"

scratch_path = os.environ.get("SCRATCH_DIR", "/scratch/zoghafoo")
print(f"Using scratch path: {scratch_path}")

DATASETS = [
            "SingleMuon",
            "MinBias",
            "MCDY",
            "MCMinBias"
           ]

FILES = [
         f"{path}/SingleMuon_SelectedEvents_RunIIFGH2016.root",
         f"{path}/MinBias_SelectedEvents_RunIIFGH2016.root",
         f"{path}/MCDY_SelectedEvents_RunII2_Weights.root",
         f"{path}/MCMinBias_SelectedEvents_RunII2_Weights.root"
        ]

VARIABLES = {
    "PFCands_pt": "p_{T} [GeV]",
    "PFCands_eta": "\\eta",
    "PFCands_phi": "\\phi",
    "PFCands_pvAssocQuality": "PV association quality",
    "nPFCands": "N^{PF}_{charged}",
    "PFCands_Ht": "H_{T} [GeV]",
    "PFCands_Pt2sum": "\\sum_{PF cands} p^{2}_{T} [GeV^{2}]",
    "PFCands_Psum": "\\sum_{PF cands} p [GeV]",
    "PFCands_P2sum": "\\sum_{PF cands} p^{2} [GeV^{2}]",
    "PFCands_InvariantMass": "m_{inv} [GeV]",
    "DiMuon_Mass": "m_{\\mu\\mu} [GeV]",
    "DiMuon_Pt": "p_{T}^{\\mu\\mu} [GeV]",
    "DiMuon_P": "p^{\\mu\\mu} [GeV]",
    "DiMuon_xmaxll": "x_{max}^{ll}",
    "DiMuon_xminll": "x_{min}^{ll}",
}

VARIABLESFORAVERAGE = {
    "PFCands_pt": ("\\bar{p}^{PF Cand.}_{T}", "[GeV]"),
    "PFCands_eta": ("\\eta", ""),
    "PFCands_phi": ("\\phi", ""),
    "PFCands_pvAssocQuality": ("PV association quality", ""),
    "nPFCands": ("N^{PF}_{charged}", ""),
    "PFCands_Ht": ("H_{T}", "[GeV]"),
    "PFCands_Pt2sum": ("\\sum_{PF cands} p^{2}_{T}", "[GeV^{2}]"),
    "PFCands_Psum": ("\\sum_{PF cands} p", "[GeV]"),
    "PFCands_P2sum": ("\\sum_{PF cands} p^{2}", "[GeV^{2}]"),
    "PFCands_InvariantMass": ("m_{inv}", "[GeV]"),
    "DiMuon_Mass": ("m_{\\mu\\mu}", "[GeV]"),
    "DiMuon_Pt": ("p_{T}^{\\mu\\mu}", "[GeV]"),
    "DiMuon_P": ("p^{\\mu\\mu}", "[GeV]"),
    "DiMuon_xmaxll": ("x_{max}^{ll}", ""),
    "DiMuon_xminll": ("x_{min}^{ll}", ""),
}

VARIABLESFORPYTHON = {
    "PFCands_pt": r'$p_{T}\,\mathrm{[GeV]}$',
    "PFCands_eta": r'$\eta$',
    "PFCands_phi": r'$\phi$',
    "PFCands_pvAssocQuality": r'$^{\mathrm{PV}}\,\mathrm{association\,quality}$',
    "nPFCands": r'$N_{\mathrm{PF}}^{\mathrm{charged}}$',
    "PFCands_Ht": r'$\mathbf{H_{T}\,\mathbf{[GeV]}}$',
    "PFCands_Pt2sum": r'$\sum_{\mathrm{PF\,cands}} p_{T}^{2}\,\mathrm{[GeV^{2}]}$',
    "PFCands_Psum": r'$\sum_{\mathrm{PF\,cands}} p\,\mathrm{[GeV]}$',
    "PFCands_P2sum": r'$\sum_{\mathrm{PF\,cands}} p^{2}\,\mathrm{[GeV^{2}]}$',
    "PFCands_InvariantMass": r'$\mathbf{m_{\mathbf{inv}}\,\mathbf{[GeV]}}$',
    "DiMuon_Mass": r'$\mathbf{m_{\mathbf{\mu\mu}}\,\mathbf{[GeV]}}$',
    "DiMuon_Pt": r'$\mathbf{p_{T}^{\mu\mu}\,\mathbf{[GeV]}}$',
    "DiMuon_P": r'$\mathbf{p^{\mu\mu}\,\mathbf{[GeV]}}$',
    "DiMuon_xmaxll": r'$x_{\mathrm{max}}^{\ell\ell}$',
    "DiMuon_xminll": r'$x_{\mathrm{min}}^{\ell\ell}$',
}

BINNING = {
    "PFCands_pt": [20, 0, 100],
    "PFCands_eta": [20, -2.4, 2.4],
    "PFCands_phi": [20, -3.14, 3.14],
    # "PFCands_InvariantMass": [0, 2, 5, 10, 15, 20, 25, 35, 45, 60, 80, 120, 160],
    "PFCands_InvariantMass": [0, 10, 20, 30, 40, 50, 60, 70, 86, 96, 100, 110, 120, 130, 140, 150, 160],
    "PFCands_pvAssocQuality": [9, 0, 9],
    "nPFCands": [3.0, 5.0, 8.0, 11.0, 15.0, 20.0, 27.0, 34.0, 43.0, 54.0, 65.0, 90.0, 130.0, 160.0],
    # "PFCands_Ht": [0, 5, 10, 15, 20, 30, 50, 70, 90, 110, 130, 150, 170, 200, 230, 260, 300, 350, 370],
    "PFCands_Ht": [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 60, 70, 80, 90, 100, 110, 120],
    "PFCands_Pt2sum": [0, 10, 20, 30, 40, 50, 70, 90, 120, 140, 160, 200, 250, 300, 350, 400],
    "PFCands_Psum": [0, 10, 20, 30, 40, 50, 60, 70, 100, 150, 200, 250, 300, 350, 400],
    "PFCands_P2sum": [0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 250, 300, 400, 500, 600, 800, 1000],
    "DiMuon_Mass": [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 52, 54, 56, 58, 60, 62, 64, 66, 68, 70, 72, 74, 76, 78, 80, 82, 84, 86, 88, 90, 92, 94, 96, 98, 100, 102, 104, 106, 108, 110, 112, 114, 116, 118, 120, 122, 124, 126, 128, 130, 132, 134, 136, 138, 140],
    "DiMuon_Pt": [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 52, 54, 56, 58, 60],
    "DiMuon_P": [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 52, 54, 56, 58, 60],
    "DiMuon_xmaxll": [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    "DiMuon_xminll": [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
}

def MakeDataframes(maxevents=None):

    df_SingleMuon = ROOT.RDataFrame("Events", FILES[0])
    df_MinBias = ROOT.RDataFrame("Events", FILES[1])
    df_MCDYJets = ROOT.RDataFrame("Events", FILES[2])
    df_MCMinBias = ROOT.RDataFrame("Events", FILES[3])
    # print("DataFrames created for SingleMuon, MinBias, MCDY, and MCMinBias datasets.")

    if maxevents is not None:
        print(f"\nProcessing only the first {maxevents} Events from each file.")
        print("\n-------------------------------------------\n")
        df_SingleMuon = df_SingleMuon.Range(maxevents)
        df_MinBias = df_MinBias.Range(maxevents)
        df_MCDYJets = df_MCDYJets.Range(maxevents)
        df_MCMinBias = df_MCMinBias.Range(maxevents)

    # One MC DY event has genWeight ~3e16 (all others < 1e5): veto generator weight outliers
    df_MCDYJets = df_MCDYJets.Filter("std::abs(genWeight) < 1e6", "genWeight outlier veto")

    return df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias

def TotalEvents():
    print("------------------------")
    print(f"Reading total events and PF candidates from text files...")

    event_dict = {"SingleMuon": [], "MinBias": [], "MCDY": [], "MCMinBias": {}}

    for dataset in DATASETS:
        if dataset in ["SingleMuon", "MinBias"]:
            txt_file = f"{path}/{dataset}_TotalEvents_RunII2016FGH.txt"
        else:
            txt_file = f"{path}/{dataset}_TotalEvents.txt"
        pd_totalEvents = pd.read_csv(txt_file, delimiter="\t")
        event_dict[dataset] = [int(pd_totalEvents.iloc[0, 1]), int(pd_totalEvents.iloc[1, 1])]


    tmp_path = f"{scratch_path}/tmp/TotalEvents_RunII2016FGH.txt"
    final_path = f"{scratch_path}/TotalEvents_RunII2016FGH.txt"

    with open(tmp_path, "w") as summary_file:
        summary_file.write("Event Type\tData_SingleMuon\tData_MinBias\tMC_DY\tMC_MinBias\n")
        summary_file.write(f"Total Events\t{event_dict['SingleMuon'][0]}\t{event_dict['MinBias'][0]}\t{event_dict['MCDY'][0]}\t{event_dict['MCMinBias'][0]}\n")
        summary_file.write(f"Total PF Cands\t{event_dict['SingleMuon'][1]}\t{event_dict['MinBias'][1]}\t{event_dict['MCDY'][1]}\t{event_dict['MCMinBias'][1]}\n")
    
    os.replace(tmp_path, final_path)

    pd_totalEvents_summary = pd.read_csv(final_path, delimiter="\t")
    print(f"\n{pd_totalEvents_summary}\n")

    print(f"Total events and PF candidates summary written to '{final_path}'!")

    print("\n------------------------")


    return {"SingleMuon": [event_dict['SingleMuon'][0], event_dict['SingleMuon'][1]],
            "MinBias": [event_dict['MinBias'][0], event_dict['MinBias'][1]],
            "MCDY": [event_dict['MCDY'][0], event_dict['MCDY'][1]],
            "MCMinBias": [event_dict['MCMinBias'][0], event_dict['MCMinBias'][1]]
            }


def SelectedEvents(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias):

    print("------------------------\n")

    print(f"Calculating selected events and PF candidates from NanoAODs...")

    event_dict = {"SingleMuon":
                  [int(df_SingleMuon.Count().GetValue()), int(df_SingleMuon.Sum("PFSelection_nPFCands").GetValue())],
                  "MinBias":
                  [int(df_MinBias.Count().GetValue()), int(df_MinBias.Sum("PFSelection_nPFCands").GetValue())],
                  "MCDY":
                  [int(df_MCDYJets.Count().GetValue()), int(df_MCDYJets.Sum("PFSelection_nPFCands").GetValue())],
                  "MCMinBias":
                  [int(df_MCMinBias.Count().GetValue()), int(df_MCMinBias.Sum("PFSelection_nPFCands").GetValue())]
                  }

    tmp_path = f"{scratch_path}/tmp/SelectedEvents_RunII2016FGH.txt"
    final_path = f"{scratch_path}/SelectedEvents_RunII2016FGH.txt"

    with open(tmp_path, "w") as summary_file:
        summary_file.write("Event Type\tData_SingleMuon\tData_MinBias\tMC_DY\tMC_MinBias\n")
        summary_file.write(f"Selected Events\t{event_dict['SingleMuon'][0]}\t{event_dict['MinBias'][0]}\t{event_dict['MCDY'][0]}\t{event_dict['MCMinBias'][0]}\n")
        summary_file.write(f"Selected PF Cands\t{event_dict['SingleMuon'][1]}\t{event_dict['MinBias'][1]}\t{event_dict['MCDY'][1]}\t{event_dict['MCMinBias'][1]}\n")
    
    os.replace(tmp_path, final_path)

    pd_selectedEvents_summary = pd.read_csv(final_path, delimiter="\t")
    print(f"\n{pd_selectedEvents_summary}\n")

    print(f"Selected events and PF candidates summary written to '{final_path}'!")

    print("\n------------------------")

    return {"SingleMuon": [event_dict['SingleMuon'][0], event_dict['SingleMuon'][1]],
            "MinBias": [event_dict['MinBias'][0], event_dict['MinBias'][1]],
            "MCDY": [event_dict['MCDY'][0], event_dict['MCDY'][1]],
            "MCMinBias": [event_dict['MCMinBias'][0], event_dict['MCMinBias'][1]]
            }


def TotalEvents_local():
    print("------------------------")
    print(f"Reading total events and PF candidates from text files...")


    event_dict = {"SingleMuon": [], "MinBias": [], "MCDY": [], "MCMinBias": {}}

    for dataset in DATASETS:
        txt_file = f"{path}/{dataset}_TotalEvents.txt"
        pd_totalEvents = pd.read_csv(txt_file, delimiter="\t")
        event_dict[dataset] = [int(pd_totalEvents.iloc[0, 1]), int(pd_totalEvents.iloc[1, 1])]


    tmp_path = f"{path}/tmp/TotalEvents.txt"
    final_path = f"{path}/TotalEvents.txt"

    with open(tmp_path, "w") as summary_file:
        summary_file.write("Event Type\tData_SingleMuon\tData_MinBias\tMC_DY\tMC_MinBias\n")
        summary_file.write(f"Total Events\t{event_dict['SingleMuon'][0]}\t{event_dict['MinBias'][0]}\t{event_dict['MCDY'][0]}\t{event_dict['MCMinBias'][0]}\n")
        summary_file.write(f"Total PF Cands\t{event_dict['SingleMuon'][1]}\t{event_dict['MinBias'][1]}\t{event_dict['MCDY'][1]}\t{event_dict['MCMinBias'][1]}\n")

    os.replace(tmp_path, final_path)

    pd_totalEvents_summary = pd.read_csv(final_path, delimiter="\t")
    print(f"\n{pd_totalEvents_summary}\n")

    print(f"Total events and PF candidates summary written to '{final_path}'!")

    print("\n------------------------")


    return {"SingleMuon": [event_dict['SingleMuon'][0], event_dict['SingleMuon'][1]],
            "MinBias": [event_dict['MinBias'][0], event_dict['MinBias'][1]],
            "MCDY": [event_dict['MCDY'][0], event_dict['MCDY'][1]],
            "MCMinBias": [event_dict['MCMinBias'][0], event_dict['MCMinBias'][1]]
            }


def SelectedEvents_local(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias):

    print("------------------------\n")

    print(f"Calculating selected events and PF candidates from NanoAODs...")

    event_dict = {"SingleMuon":
                  [int(df_SingleMuon.Count().GetValue()), int(df_SingleMuon.Sum("PFSelection_nPFCands").GetValue())],
                  "MinBias":
                  [int(df_MinBias.Count().GetValue()), int(df_MinBias.Sum("PFSelection_nPFCands").GetValue())],
                  "MCDY":
                  [int(df_MCDYJets.Count().GetValue()), int(df_MCDYJets.Sum("PFSelection_nPFCands").GetValue())],
                  "MCMinBias":
                  [int(df_MCMinBias.Count().GetValue()), int(df_MCMinBias.Sum("PFSelection_nPFCands").GetValue())]
                  }

    tmp_path = f"{path}/tmp/SelectedEvents.txt"
    final_path = f"{path}/SelectedEvents.txt"

    with open(tmp_path, "w") as summary_file:
        summary_file.write("Event Type\tData_SingleMuon\tData_MinBias\tMC_DY\tMC_MinBias\n")
        summary_file.write(f"Selected Events\t{event_dict['SingleMuon'][0]}\t{event_dict['MinBias'][0]}\t{event_dict['MCDY'][0]}\t{event_dict['MCMinBias'][0]}\n")
        summary_file.write(f"Selected PF Cands\t{event_dict['SingleMuon'][1]}\t{event_dict['MinBias'][1]}\t{event_dict['MCDY'][1]}\t{event_dict['MCMinBias'][1]}\n")

    os.replace(tmp_path, final_path)

    pd_selectedEvents_summary = pd.read_csv(final_path, delimiter="\t")
    print(f"\n{pd_selectedEvents_summary}\n")

    print(f"Selected events and PF candidates summary written to '{final_path}'!")

    print("\n------------------------")

    return {"SingleMuon": [event_dict['SingleMuon'][0], event_dict['SingleMuon'][1]],
            "MinBias": [event_dict['MinBias'][0], event_dict['MinBias'][1]],
            "MCDY": [event_dict['MCDY'][0], event_dict['MCDY'][1]],
            "MCMinBias": [event_dict['MCMinBias'][0], event_dict['MCMinBias'][1]]
            }

def DiMuonPtCut(df, pt_cut):
    df = df.Filter(f"DiMuon_Pt < {pt_cut}")
    return df

def MakeHist(df, var, label, y_title, bins, hist_name, axis="raw"):
    
    # Detect binning format
    if len(bins) == 3:
        # Uniform binning: [nbins, xlow, xup]
        if axis == "raw":
            h = df.Histo1D(
                (hist_name, label, int(bins[0]), bins[1], bins[2]),
                f"PFSelection_{var}" if not var.startswith("DiMuon_") else var,
                *(["genWeight"] if "genWeight" in df.GetColumnNames() else [])
            )
        elif axis == "quantile":
            q_column = f"{var}_InvQ"
            h = df.Histo1D(
                (hist_name, label, int(bins[0]), bins[1], bins[2]),
                q_column,
                *(["genWeight"] if "genWeight" in df.GetColumnNames() else [])
            )
        elif axis == "IP":
            b_column = f"{var}_b"
            h = df.Histo1D(
                (hist_name, label, int(bins[0]), bins[1], bins[2]),
                b_column,
                *(["genWeight"] if "genWeight" in df.GetColumnNames() else [])
            )
    else:
        if not isinstance(bins, array.array):
            bins = array.array("d", bins)
        
        if axis == "raw":
            h = df.Histo1D(
                (hist_name, label, len(bins) - 1, bins),
                f"PFSelection_{var}" if not var.startswith("DiMuon_") else var,
                *(["genWeight"] if "genWeight" in df.GetColumnNames() else [])
            )
        elif axis == "quantile":
            q_column = f"{var}_InvQ"
            h = df.Histo1D(
                (hist_name, label, len(bins) - 1, bins),
                q_column,
                *(["genWeight"] if "genWeight" in df.GetColumnNames() else [])
            )
        elif axis == "IP":
            b_column = f"{var}_b"
            h = df.Histo1D(
                (hist_name, label, len(bins) - 1, bins),
                b_column,
                *(["genWeight"] if "genWeight" in df.GetColumnNames() else [])
            )
    
    return h


def NormaliseHist(hist, width=False):
    print(f"Normalising histogram '{hist.GetName()}' with width={width}")

    integral = hist.Integral()
    if integral > 0:
        if width:
            hist.Scale(1.0 / integral, "width")
        else:
            hist.Scale(1.0 / integral)
    else:
        print(f"Warning: histogram '{hist.GetName()}' has zero integral; skipping normalization")
    hist.SetStats(0)

def parse_pt_cuts(pt_cuts):
    print("parse_pt_cuts called with:", pt_cuts)
    print("types:", [type(x) for x in pt_cuts])

    if pt_cuts is None or len(pt_cuts) == 0:
        return [None]

    parsed = []

    for cut in pt_cuts:
        print("processing:", cut, type(cut))

        if cut.lower() == "none":
            parsed.append(None)
        else:
            parsed.append(float(cut))

    return parsed




def BuildQuantile(df, var, map_name):

    # Histogram used to build the CDF
    h_ptr = MakeHist(df, var, "", "", BINNING[var], f"h_{map_name}_{var}_quantile")
    h = h_ptr.GetValue()
    total = h.Integral()

    if total <= 0:
        print(f"Warning: {map_name} histogram for '{var}' is empty")
        return False


    # Store bin edges and CDF values
    bin_edges = [h.GetBinLowEdge(1)]
    cdf_values = [0.0]

    cumulative = 0.0

    for i in range(1, h.GetNbinsX()+1):

        cumulative += h.GetBinContent(i)

        edge = h.GetBinLowEdge(i+1)

        cdf = cumulative / total

        bin_edges.append(edge)
        cdf_values.append(cdf)


    edges_cpp = ", ".join(f"{x:.17g}" for x in bin_edges)
    cdf_cpp = ", ".join(f"{x:.17g}" for x in cdf_values)


    ROOT.gInterpreter.Declare(
        f"""
        namespace {var}InvQMap{map_name} {{
        static const std::vector<double> edges = {{{edges_cpp}}};
        static const std::vector<double> cdf = {{{cdf_cpp}}};


        double eval(double x) {{
            if(edges.empty())
                return 0.0;

            if(x <= edges.front())
                return 0.0;

            if(x >= edges.back())
                return 1.0;


            for(size_t i=1; i<edges.size(); i++) {{

                if(x < edges[i]) {{

                    double x1 = edges[i-1];
                    double x2 = edges[i];

                    double y1 = cdf[i-1];
                    double y2 = cdf[i];


                    return y1 +
                    (x-x1)*(y2-y1)/(x2-x1);
                }}
            }}

            return 1.0;
        }}

        }}
        """
    )


    print(f"Built quantile map {map_name} for {var}")

    return True


def ApplyQuantileAndIP(df, var, map_name):

    df = df.Define(f"{var}_InvQ", f"1.0 - {var}InvQMap{map_name}::eval(PFSelection_{var})")
    df = df.Define(f"{var}_b", f"TMath::Sqrt({var}_InvQ)")

    return df


def inverse_cdf_from_hist(h, target_cdf):
    total = h.Integral()
    if total <= 0:
        return None

    if target_cdf <= 0.0:
        return h.GetBinLowEdge(1)

    if target_cdf >= 1.0:
        return h.GetBinLowEdge(h.GetNbinsX() + 1)

    cumulative = 0.0
    prev_x = h.GetBinLowEdge(1)
    prev_cdf = 0.0

    for i in range(1, h.GetNbinsX() + 1):
        x = h.GetBinLowEdge(i + 1)
        cumulative += h.GetBinContent(i)
        cdf = cumulative / total

        if target_cdf <= cdf:
            if cdf == prev_cdf:
                return x
            frac = (target_cdf - prev_cdf) / (cdf - prev_cdf)
            return prev_x + frac * (x - prev_x)

        prev_x = x
        prev_cdf = cdf

    return h.GetBinLowEdge(h.GetNbinsX() + 1)


def quantile_edges_from_hist(hist, quantile_bins):
    if not quantile_bins or len(quantile_bins) < 2:
        return None

    edges = []
    for q in reversed(quantile_bins):
        edge = inverse_cdf_from_hist(hist, 1.0 - q)
        if edge is None:
            return None
        edges.append(edge)

    return edges

def CopyLegendStyle(source, target):
    # Text
    target.SetTextFont(source.GetTextFont())
    target.SetTextSize(source.GetTextSize())
    target.SetTextColor(source.GetTextColor())
    target.SetTextAlign(source.GetTextAlign())

    # Fill
    target.SetFillColor(source.GetFillColor())
    target.SetFillStyle(source.GetFillStyle())

    # Border
    target.SetBorderSize(source.GetBorderSize())
    target.SetLineColor(source.GetLineColor())
    target.SetLineStyle(source.GetLineStyle())
    target.SetLineWidth(source.GetLineWidth())

    # Margins / spacing
    target.SetMargin(source.GetMargin())

    # Entry separation
    target.SetEntrySeparation(source.GetEntrySeparation())

    # Number of columns
    target.SetNColumns(source.GetNColumns())

    # Header
    # target.SetHeader(source.GetHeader())


def CopyLegend(source, target):
    CopyLegendStyle(source, target)

    for entry in source.GetListOfPrimitives():
        target.AddEntry(
            entry.GetObject(),
            entry.GetLabel(),
            entry.GetOption()
        )

def BuildAverageEventActivityObservable(df, var):

    if "PFCands_Rapidity" not in df.GetColumnNames():
        df = df.Define("PFCands_Rapidity", "auto pz = PFCands_pt * sinh(PFCands_eta);"
                        "return 0.5f * log((PFCands_energy + pz) / (PFCands_energy - pz));")
    else:
        print("PFCands_Rapidity already exists in the DataFrame.")
        return df

    # pT/E ratio per PF candidate
    df = df.Define("PFCands_pToverE",
        "return PFCands_pt / PFCands_energy;")
    return df

def VarianceCalculation(df, df_name, weight = False):

    col_names = list(df.GetColumnNames())

    if "PFSelection_PFCands_E" not in col_names:
        df = df.Define("PFSelection_PFCands_E", "PFSelection_PFCands_pt * cosh(PFSelection_PFCands_eta)")
        # print(f"PFSelection_PFCands_E column created in {df_name} Dataframe.")

    if "PFSelection_PFCands_P" not in col_names:
        df = df.Define("PFSelection_PFCands_P",
            """ROOT::VecOps::Construct<ROOT::Math::PtEtaPhiEVector>(
            PFSelection_PFCands_pt,
            PFSelection_PFCands_eta,
            PFSelection_PFCands_phi,
            PFSelection_PFCands_E)""")
        # print(f"PFSelection_PFCands_P column created in {df_name} Dataframe.")

    if "PFSelection_PFCands_SumP" not in col_names:
        df = df.Define("PFSelection_PFCands_SumP", "ROOT::VecOps::Sum(PFSelection_PFCands_P, ROOT::Math::PtEtaPhiEVector())")
        # print(f"PFSelection_PFCands_SumP column created in {df_name} Dataframe.")

    if "PFSelection_PFCands_EventRapidity" not in col_names:
        df = df.Define("PFSelection_PFCands_EventRapidity", "PFSelection_PFCands_SumP.Rapidity()")
        # print(f"PFSelection_PFCands_EventRapidity column created in {df_name} Dataframe.")


    if "PFSelection_PFCands_pToverE" not in col_names:
        df = df.Define("PFSelection_PFCands_pToverE", "PFSelection_PFCands_pt / PFSelection_PFCands_E")
        # print(f"PFSelection_PFCands_pToverE column created in {df_name} Dataframe.")

    print(f"Variance calculation columns created in {df_name} Dataframe.")

    return df

def Cuts(bins):
    centers   = [0.5 * (a + b) for a, b in bins]
    edges     = sorted(set(edge for b in bins for edge in b))
    edges_arr = np.array(edges)
    return centers, edges, edges_arr


# ---------------------- PLOTS ----------------------

def Histograms(df_SingleMuon_var, df_MinBias_var, df_MCDYJets_var, df_MCMinBias_var, variables, kin_filter, ratio, axis, out_suffix, q_bins, b_bins, overlay_filters=False):

    RATIOS = {
        "DYMinBias": "#frac{DY}{MinBias}",
        "DataMC": "#frac{Data}{MC}",
        "DYZ": "#frac{DY}{DY_{Z}}",
    }

    # if kin_filter == "mass":
    #     df_SingleMuon_var = DiMuonPtCut(df_SingleMuon_var, 4)
    #     df_MCDYJets_var = DiMuonPtCut(df_MCDYJets_var, 4)
    # elif kin_filter == "pt":
    #     df_SingleMuon_var = df_SingleMuon_var.Filter("DiMuon_Mass > 86 && DiMuon_Mass < 96")
    #     df_MCDYJets_var = df_MCDYJets_var.Filter("DiMuon_Mass > 86 && DiMuon_Mass < 96")

    colours = [
            ROOT.kBlue + 1,
            ROOT.kGreen + 2,
            ROOT.kMagenta + 1,
            ROOT.kOrange + 7,
            ROOT.kCyan + 1,
            ROOT.kViolet + 1,
            ROOT.kAzure + 1,
            ROOT.kPink + 7,
            ROOT.kTeal + 3,
            ROOT.kSpring + 5,
            ROOT.kYellow + 2,
            ROOT.kGray + 2,
            ROOT.kBlack,
            ROOT.kRed,
            ROOT.kOrange - 3,
            ROOT.kGreen - 3,
            ROOT.kMagenta - 3,
            ROOT.kCyan - 3,
            ROOT.kViolet - 3,
            ROOT.kAzure - 3,
            ROOT.kPink - 3,
        ]

    mass = [
                # (0, 10),
                # (10, 20), 
                # (20, 30), 
                # (30, 40), 
                # (40, 50), 
                # (50, 60), 
                # (60, 70), 
                # (70, 86),
                # (86, 96),
                # (96, 100), 
                # (100, 110), 
                # (110, 120), 
                # (120, 130), 
                # (130, 140), 
                # (140, 150)
                (0, 50),
                (50, 70),
                (70, 86),
                (86, 96),
                (96, 110),
                (110, 130),
                (130, 150)
        ]
    pt_cuts = [
                (0, 1),
                (1, 2),
                (2, 3), 
                (3, 4),
                (4, 5), 
                (5, 6), 
                (6, 7), 
                (7, 8), 
                (8, 9), 
                (9, 10), 
                (10, 11), 
                (11, 12), 
                (12, 13), 
                (13, 14), 
                (14, 15), 
                (15, 16), 
                (16, 17), 
                (17, 18), 
                (18, 19), 
                (19, 20)
        ]
    rapidity = [
                (-2.4, -2),
                (-2, -1),
                (-1, -0.5),
                (-0.5, 0),
                (0, 0.5),
                (0.5, 1),
                (1, 2),
                (2, 2.4)
        ]
    Ht_slices = [
                (0, 10),
                (10, 20),
                (20, 30),
                (30, 40),
                (40, 50),
                (50, 60),
                (60, 70),
                (70, 80),
                (80, 90),
                (90, 100),
                (100, 110),
                (110, 120)
    ]

    mass_centers, mass_edges, mass_edges_arr = Cuts(mass)
    pt_centers, pt_edges, pt_edges_arr = Cuts(pt_cuts)
    rapidity_centers, rapidity_edges, rapidity_edges_arr = Cuts(rapidity)
    Ht_centers, Ht_edges, Ht_edges_arr = Cuts(Ht_slices)


    BIN_DEFS = {
                    "mass": mass,
                    "pt": pt_cuts,
                    "rapidity": rapidity,
                    "Ht": Ht_slices,
                }
    FILTER_COL = {
                    "mass": "DiMuon_Mass",
                    "pt": "DiMuon_Pt",
                    "rapidity": "DiMuon_Rapidity",
                    "Ht": "PFSelection_PFCands_Ht",
                }

    AXIS_INFO = {
                    "mass": {
                        "label": r"m_{#mu#mu}",
                        "edges": mass_edges,
                        "edges_arr": mass_edges_arr,
                    },
                    "pt": {
                        "label": r"p^{#mu#mu}_{T}",
                        "edges": pt_edges,
                        "edges_arr": pt_edges_arr,
                    },
                    "rapidity": {
                        "label": r"y_{#mu#mu}",
                        "edges": rapidity_edges,
                        "edges_arr": rapidity_edges_arr,
                    },
                    "Ht": {
                        "label": r"H_{T}",
                        "edges": Ht_edges,
                        "edges_arr": Ht_edges_arr,
                    },
                }

    filter_specs = [{"name": kf, "col": FILTER_COL[kf], "bins": BIN_DEFS[kf], "label": AXIS_INFO[kf]["label"]} for kf in kin_filter]
    filter_bins = [spec["bins"] for spec in filter_specs]

    print(f"Filter specifications: {filter_specs}")
    print(f"Filter bins: {filter_bins}")


    # q_bins = array.array("d", q_bins)
    q_bins = array.array("d", np.concatenate([
                                np.arange(0.00, 0.10, 0.01),
                                np.arange(0.10, 0.20, 0.01),
                                np.arange(0.20, 1.05, 0.05)
                            ])
                        )

    b_bins = array.array("d", np.linspace(0, 1, 20))
    # b_bins = array.array("d", np.concatenate([
    #                           np.arange(0.00, 0.10, 0.01),
    #                           np.arange(0.10, 0.20, 0.01),
    #                           np.arange(0.20, 1.05, 0.05)
    #                         ])
    #                     )

    for var in variables:
        if var in ["PFCands_pt", "PFCands_eta", "PFCands_phi", "PFCands_pvAssocQuality"]:
            continue

        skip_minbias = var.startswith("DiMuon_")

        if axis == "raw":
            label = VARIABLES[var]
            bins = array.array('d', BINNING[var])
            # bins = BINNING[var]
        elif axis == "quantile":
            label = f"Inv. Quantile ({VARIABLES[var]})"
            bins = q_bins
        elif axis == "IP":
            label = f"Impact Parameter ({VARIABLES[var]})"
            bins = b_bins
        
        y_title_pad1 = "Density #frac{1}{N} #frac{dN}{dx} (normalised)"
        y_title_pad2 = RATIOS[ratio]


# --------------- LEGEND -----------------

        dummy = ROOT.TObject()

        DYMarker = ROOT.TMarker()
        DYMarker.SetMarkerStyle(20)
        DYMarker.SetMarkerSize(1)
        DYMarker.SetMarkerColor(ROOT.kViolet - 6)

        ZeroBiasMarker = ROOT.TMarker()
        ZeroBiasMarker.SetMarkerStyle(20)
        ZeroBiasMarker.SetMarkerSize(1)
        ZeroBiasMarker.SetMarkerColor(ROOT.kOrange + 5)

        legend_DataStyle = ROOT.TLine(0.0, 0.0, 0.5, 0.0)
        legend_DataStyle.SetLineColor(ROOT.kBlack)
        legend_DataStyle.SetLineWidth(2)
        legend_DataStyle.SetLineStyle(1)

        legend_MCStyle = ROOT.TLine(0.0, 0.0, 0.5, 0.0)
        legend_MCStyle.SetLineColor(ROOT.kBlack)
        legend_MCStyle.SetLineWidth(2)
        legend_MCStyle.SetLineStyle(2)


# --------------- PLOT -----------------

        if not skip_minbias:
            if axis == "raw":
                h_MinBias_ptr = MakeHist(df_MinBias_var, var, label, y_title_pad1, bins, f"h_MinBias_{var}", axis="raw")
                h_MCMinBias_ptr = MakeHist(df_MCMinBias_var, var, label, y_title_pad1, bins, f"h_MCMinBias_{var}", axis="raw")

            elif axis == "quantile":
                BuildQuantile(df_MinBias_var, var, "MinBias")
                BuildQuantile(df_MCMinBias_var, var, "MCMinBias")

                df_MinBias_var_q = ApplyQuantileAndIP(df_MinBias_var, var, "MinBias")
                df_MCMinBias_var_q = ApplyQuantileAndIP(df_MCMinBias_var, var, "MCMinBias")

                h_MinBias_ptr = MakeHist(df_MinBias_var_q, var, label, y_title_pad1, bins, f"h_MinBias_{var}", axis="quantile")
                h_MCMinBias_ptr = MakeHist(df_MCMinBias_var_q, var, label, y_title_pad1, bins, f"h_MCMinBias_{var}", axis="quantile")

            elif axis == "IP":
                BuildQuantile(df_MinBias_var, var, "MinBias")
                BuildQuantile(df_MCMinBias_var, var, "MCMinBias")

                df_MinBias_var_q = ApplyQuantileAndIP(df_MinBias_var, var, "MinBias")
                df_MCMinBias_var_q = ApplyQuantileAndIP(df_MCMinBias_var, var, "MCMinBias")

                h_MinBias_ptr = MakeHist(df_MinBias_var_q, var, label, y_title_pad1, bins, f"h_MinBias_{var}", axis="IP")
                h_MCMinBias_ptr = MakeHist(df_MCMinBias_var_q, var, label, y_title_pad1, bins, f"h_MCMinBias_{var}", axis="IP")

            h_MinBias = h_MinBias_ptr.GetValue()
            h_MCMinBias = h_MCMinBias_ptr.GetValue()

            NormaliseHist(h_MinBias, True)
            NormaliseHist(h_MCMinBias, True)

            h_MinBias.SetLineColor(ROOT.kOrange + 5)
            h_MinBias.SetLineWidth(2)
            h_MinBias.SetTitle("")
            h_MinBias.GetXaxis().SetTitle("")
            h_MinBias.GetYaxis().SetTitle(y_title_pad1)
            h_MinBias.GetYaxis().SetLabelSize(0.048)
            h_MinBias.GetYaxis().SetTitleSize(0.06)
            h_MinBias.GetYaxis().SetTitleOffset(0.9)
            h_MinBias.GetYaxis().SetNdivisions(510)
            h_MinBias.GetXaxis().SetLabelSize(0)

            h_MCMinBias.SetLineColor(ROOT.kOrange + 5)
            h_MCMinBias.SetLineWidth(2)
            h_MCMinBias.SetLineStyle(2)

            ratios_MinBias = h_MinBias.Clone(f"ratio_{var}")
            if ratio == "DataMC":
                ratios_MinBias.Divide(h_MCMinBias)
                ratios_MinBias.SetLineColor(ROOT.kOrange + 5)
                ratios_MinBias.SetMarkerColor(ROOT.kOrange + 5)
                ratios_MinBias.SetMarkerStyle(20)
                ratios_MinBias.SetMarkerSize(0.8)
                ratios_MinBias.SetTitle("")
                ratios_MinBias.GetXaxis().SetTitle(label)
                ratios_MinBias.GetXaxis().SetTitleSize(0.11)
                ratios_MinBias.GetXaxis().SetTitleOffset(1.2)
                ratios_MinBias.GetXaxis().SetLabelSize(0.1)
                ratios_MinBias.GetXaxis().SetTickLength(0.07)
                ratios_MinBias.GetYaxis().SetTitle(y_title_pad2)
                ratios_MinBias.GetYaxis().SetTitleSize(0.1)
                ratios_MinBias.GetYaxis().SetLabelSize(0.09)
                ratios_MinBias.GetYaxis().SetTitleOffset(0.52)
                ratios_MinBias.GetYaxis().SetNdivisions(510)

        
        for combo in itertools.product(*filter_bins):

            filter_conditions = []
            name_parts = []
            legend_parts = []
            
            for spec, fbin in zip(filter_specs, combo):
                filter_conditions.append(f"{spec['col']} >= {fbin[0]} && {spec['col']} < {fbin[1]}")
                name_parts.append(f"{spec['name'].capitalize()}{fbin[0]}-{fbin[1]}")
                unit = " GeV" if spec["name"] in ("pt", "mass", "Ht") else ""
                legend_parts.append(f"{fbin[0]}{unit} #leq {spec['label']} < {fbin[1]}{unit}")

            filter_expr = " && ".join(filter_conditions)
            name_suffix = "_".join(name_parts)
            legend_text = ", ".join(legend_parts)

            print(f"\n\nApplying filter(s): {filter_expr if filter_expr else 'none'}\n")





            # --------------- CANVAS -----------------

            canvas = ROOT.TCanvas(f"c_{var}_{name_suffix}")

            pad1 = ROOT.TPad("pad1", "pad1", 0, 0.35, 1, 1)
            pad1.Draw()
            pad1.cd()
            pad1.SetBottomMargin(0.08)
            pad1.SetRightMargin(0.04)
            pad1.SetLeftMargin(0.13)
            pad1.SetTopMargin(0.05)
            # pad1.SetLogy()
            # pad1.SetGridy()
            

            canvas.cd()
            pad2 = ROOT.TPad("pad2", "pad2", 0, 0.02, 1, 0.38)
            pad2.Draw()
            pad2.cd()
            pad2.SetTopMargin(0.05)
            pad2.SetBottomMargin(0.35)
            pad2.SetLeftMargin(0.13)
            pad2.SetRightMargin(0.04)
            # pad2.SetLogy()
            pad2.SetGridy()

            # if skip_minbias:
            #     pad1.SetLogy()


            # --------------- LEGEND -----------------
            if kin_filter:
                if axis in ["raw", "quantile"]:
                    legend = ROOT.TLegend(0.55, 0.65, 0.8, 0.92)
                elif axis == "IP":
                    legend = ROOT.TLegend(0.36, 0.65, 0.7, 0.92)
                legend.SetMargin(0.13)
            else:
                if axis in ["raw", "quantile"]:
                    legend = ROOT.TLegend(0.8, 0.65, 0.96, 0.92)
                elif axis == "IP":
                    legend = ROOT.TLegend(0.16, 0.67, 0.3, 0.92)
                legend.SetMargin(0.28)

            if skip_minbias:
                legend = ROOT.TLegend(0.16, 0.65, 0.3, 0.92)
                legend.SetMargin(0.28)

            legend.SetBorderSize(0)
            legend.SetFillStyle(0)
            legend.SetTextSize(0.06)
            
            
            legend.AddEntry(legend_DataStyle, "#bf{Data}", "l")
            legend.AddEntry(legend_MCStyle, "#bf{MC}", "l")

            # if kin_filter != "pt":
            #     legend.AddEntry(dummy, f"#color[{ROOT.kViolet - 6}]{{#bf{{DY}}(p^{{#mu#mu}}_{{T}} < 4 GeV)}}", "")
            # elif kin_filter != "mass":
            #     legend.AddEntry(dummy, f"#color[{ROOT.kViolet - 6}]{{#bf{{DY}}(86 GeV < m_{{#mu#mu}} < 96 GeV)}}", "")
            # else:






            # --------------- PLOT -----------------

            canvas.cd()
            pad1.cd()

            if not skip_minbias:
                h_MinBias.Draw("hist e")
                h_MCMinBias.Draw("hist e same")

            

            print(f"Filtering DY (Data and MC) for {filter_expr}...")

            df_SingleMuon_var_filtered = df_SingleMuon_var.Filter(filter_expr) if filter_expr else df_SingleMuon_var
            df_MCDYJets_var_filtered = df_MCDYJets_var.Filter(filter_expr) if filter_expr else df_MCDYJets_var

            hist_name_DY = f"h_SingleMuon_{var}_{name_suffix}"
            hist_name_MCDY = f"h_MCDYJets_{var}_{name_suffix}"

            if axis == "raw":
                h_SingleMuon_ptr_filtered = MakeHist(df_SingleMuon_var_filtered, var, label, y_title_pad1, bins, hist_name_DY, axis="raw")
                h_MCDYJets_ptr_filtered = MakeHist(df_MCDYJets_var_filtered, var, label, y_title_pad1, bins, hist_name_MCDY, axis="raw")

            elif (axis == "quantile" or axis == "IP") and not skip_minbias:
                df_SingleMuon_var_filtered = ApplyQuantileAndIP(df_SingleMuon_var_filtered, var, "MinBias")
                df_MCDYJets_var_filtered = ApplyQuantileAndIP(df_MCDYJets_var_filtered, var, "MCMinBias")

                if axis == "quantile":
                    h_SingleMuon_ptr_filtered = MakeHist(df_SingleMuon_var_filtered, var, label, y_title_pad1, bins, hist_name_DY, axis="quantile")
                    h_MCDYJets_ptr_filtered = MakeHist(df_MCDYJets_var_filtered, var, label, y_title_pad1, bins, hist_name_MCDY, axis="quantile")

                elif axis == "IP":
                    h_SingleMuon_ptr_filtered = MakeHist(df_SingleMuon_var_filtered, var, label, y_title_pad1, bins, hist_name_DY, axis="IP")
                    h_MCDYJets_ptr_filtered = MakeHist(df_MCDYJets_var_filtered, var, label, y_title_pad1, bins, hist_name_MCDY, axis="IP")




            h_SingleMuon_filtered = h_SingleMuon_ptr_filtered.GetValue()
            h_MCDYJets_filtered = h_MCDYJets_ptr_filtered.GetValue()

            NormaliseHist(h_SingleMuon_filtered, True)
            NormaliseHist(h_MCDYJets_filtered, True)

            if skip_minbias:
                h_SingleMuon_filtered.SetTitle("")
                h_SingleMuon_filtered.GetXaxis().SetTitle(VARIABLES[var])
                h_SingleMuon_filtered.GetYaxis().SetTitle(y_title_pad1)
                h_SingleMuon_filtered.GetYaxis().SetLabelSize(0.048)
                h_SingleMuon_filtered.GetYaxis().SetTitleSize(0.06)
                h_SingleMuon_filtered.GetYaxis().SetTitleOffset(0.9)
                h_SingleMuon_filtered.GetYaxis().SetNdivisions(510)
                h_SingleMuon_filtered.GetXaxis().SetLabelSize(0)
        
            h_SingleMuon_filtered.SetLineColor(ROOT.kViolet - 6)
            h_SingleMuon_filtered.SetLineWidth(2)
            draw_opt = "hist e same" if not skip_minbias else "hist e"
            h_SingleMuon_filtered.Draw(draw_opt)

            h_MCDYJets_filtered.SetLineColor(ROOT.kViolet - 6)
            h_MCDYJets_filtered.SetLineWidth(2)
            h_MCDYJets_filtered.SetLineStyle(2)
            h_MCDYJets_filtered.Draw("hist e same")

            # h_MinBias.SetMaximum(max(h_SingleMuon_filtered.GetMaximum(), h_MinBias.GetMaximum(), h_MCDYJets_filtered.GetMaximum(), h_MCMinBias.GetMaximum()) * 1.02 if axis in ["raw", "quantile"] else max(h_SingleMuon_filtered.GetMaximum(), h_MinBias.GetMaximum(), h_MCDYJets_filtered.GetMaximum(), h_MCMinBias.GetMaximum()) * 1.05)
            scale = 1.02 if axis in ["raw", "quantile"] else 1.05
            all_maxima = [h_SingleMuon_filtered.GetMaximum(), h_MCDYJets_filtered.GetMaximum()]
            if not skip_minbias:
                all_maxima += [h_MinBias.GetMaximum(), h_MCMinBias.GetMaximum()]
            top_hist = h_SingleMuon_filtered if skip_minbias else h_MinBias
            top_hist.SetMaximum(max(all_maxima) * scale)


            legend.AddEntry(dummy, f"#color[{ROOT.kViolet - 6}]{{#bf{{DY}} ({legend_text})}}" if legend_text else f"#color[{ROOT.kViolet - 6}]{{#bf{{DY}}}}", "")
            if not skip_minbias:
                legend.AddEntry(dummy, f"#color[{ROOT.kOrange + 5}]{{#bf{{MinBias}}}}", "")


            if kin_filter:
                # Auto-fit width based on longest entry
                entries = legend.GetListOfPrimitives()
                max_text_length = 0
                for entry in entries:
                    if hasattr(entry, 'GetLabel'):
                        text_length = len(entry.GetLabel())
                        max_text_length = max(max_text_length, text_length)

                # Estimate width: ~0.015 per character
                width_adjustment = max_text_length * 0.006

                if axis in ["raw", "quantile"]:
                    if not skip_minbias:
                        x1, x2 = 0.55, 0.8
                    else:
                        x1, x2 = 0.16, 0.3
                    new_x2 = x1 + width_adjustment
                    legend.SetX1(x1)
                    legend.SetX2(new_x2)
                elif axis == "IP":
                    x1, x2 = 0.36, 0.7
                    new_x2 = x1 + width_adjustment
                    legend.SetX1(x1)
                    legend.SetX2(new_x2)

            legend.Draw()





            canvas.cd()
            pad2.cd()


            ratios_DY = h_SingleMuon_filtered.Clone(f"ratio_{var}")
            ratios_MCDY = h_MCDYJets_filtered.Clone(f"ratio_MC_{var}")


            if ratio == "DYMinBias" and not skip_minbias:

                if axis == "raw":
                    legend_ratios = ROOT.TLegend(0.15, 0.7, 0.24, 0.94)
                elif axis in ["quantile", "IP"]:
                    legend_ratios = ROOT.TLegend(0.86, 0.7, 0.95, 0.94)
                legend_ratios.SetBorderSize(0)
                # legend_ratios.SetFillStyle(0)
                legend_ratios.SetTextSize(0.08)
                legend_ratios.SetMargin(0.5)

                ratios_DY.Divide(h_MinBias)
                ratios_DY.SetLineColor(ROOT.kBlack)
                ratios_MCDY.Divide(h_MCMinBias)
                ratios_MCDY.SetLineColor(ROOT.kGray + 2)
                ratios_MCDY.SetLineStyle(2)

            elif ratio == "DataMC":
                ratios_DY.Divide(h_MCDYJets_filtered)
                if not skip_minbias:
                    ratios_MinBias.Draw("hist e")
                ratios_DY.Draw("hist e same" if not skip_minbias else "hist e")

            ratios_DY.SetTitle("")
            ratios_DY.SetMarkerStyle(20)
            ratios_DY.SetMarkerSize(0.8)
            ratios_DY.GetXaxis().SetTitle(label)
            ratios_DY.GetXaxis().SetTitleSize(0.11)
            ratios_DY.GetXaxis().SetTitleOffset(1.2)
            ratios_DY.GetXaxis().SetLabelSize(0.1)
            ratios_DY.GetXaxis().SetTickLength(0.07)
            ratios_DY.GetYaxis().SetTitle(y_title_pad2)
            ratios_DY.GetYaxis().SetTitleSize(0.1)
            ratios_DY.GetYaxis().SetLabelSize(0.09)
            ratios_DY.GetYaxis().SetTitleOffset(0.52)
            ratios_DY.GetYaxis().SetNdivisions(510)

            ratios_MCDY.SetLineStyle(1)
            ratios_MCDY.SetMarkerColor(ROOT.kGray + 2)
            ratios_MCDY.SetMarkerStyle(20)
            ratios_MCDY.SetMarkerSize(0.8)

            if ratio == "DYMinBias" and not skip_minbias:
                ratios_DY.Draw("hist e")
                ratios_MCDY.Draw("hist e same")
                ratios_DY.SetMaximum(max(ratios_DY.GetMaximum(), ratios_MCDY.GetMaximum()) * 1.1)
                ratios_DY.SetMinimum(min(ratios_DY.GetMinimum(), ratios_MCDY.GetMinimum()) * 0.9)
            elif ratio == "DataMC":
                # fixed y range of pad 2, set on the histogram drawn first there, as it defines the axes
                frame = ratios_MinBias if not skip_minbias else ratios_DY
                frame.SetMinimum(0.8)
                frame.SetMaximum(1.8)



            if ratio == "DYMinBias" and not skip_minbias:
                legend_ratios.AddEntry(ratios_DY, f"#color[{ROOT.kBlack}]{{#bf{{Data}}}}", "lpe")
                legend_ratios.AddEntry(ratios_MCDY, f"#color[{ROOT.kGray + 2}]{{#bf{{MC}}}}", "lpe")

                legend_ratios.Draw()


            kin_filter_tag = "".join(kf.capitalize() for kf in kin_filter) if kin_filter else "NoFilter"
            path = f"new_plots/{var}/{axis.capitalize() if axis in ['raw', 'quantile'] else axis}/{kin_filter_tag}"
            output_name = f"{path}/{var}_{axis.capitalize() if axis in ['raw', 'quantile'] else axis}{'_' + name_suffix if name_suffix else ''}_{ratio}{out_suffix}.pdf"

            os.makedirs(path, exist_ok=True)
            canvas.SaveAs(output_name)
            canvas.Close()


def AverageObservablesVsZpT(df_SingleMuon_var, df_MinBias_var, df_MCDYJets_var, df_MCMinBias_var, variables, out_suffix):
    pt_edges = array.array('d', [
                                    0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5,
                                    4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 25, 30, 35
                                ])
    n_bins = len(pt_edges) - 1

    for var in variables:
        var_name = f"PFSelection_{var}"

        if var not in ["PFCands_Ht", "PFCands_Pt2sum", "PFCands_Psum", "PFCands_P2sum", "PFCands_InvariantMass", "nPFCands"]:
            # Build average event activity observable per event
            # continue
            df_SingleMuon_var = BuildAverageEventActivityObservable(df_SingleMuon_var, var)
            df_MinBias_var = BuildAverageEventActivityObservable(df_MinBias_var, var)
            df_MCDYJets_var = BuildAverageEventActivityObservable(df_MCDYJets_var, var)
            df_MCMinBias_var = BuildAverageEventActivityObservable(df_MCMinBias_var, var)
            var_name = f"PFSelection_{var}_Mean"

        canvas = ROOT.TCanvas(f"c_{var_name}")
        canvas.SetBottomMargin(0.15)
        canvas.SetLeftMargin(0.13)
        canvas.SetRightMargin(0.05)




        DY_profile = df_SingleMuon_var.Fill(ROOT.TProfile(f"p_{var_name}_DY", "pT [GeV]; <H_{T}> [GeV]", n_bins, pt_edges), ["DiMuon_Pt", var_name]).GetValue()
        MCDY_profile = df_MCDYJets_var.Fill(ROOT.TProfile(f"p_{var_name}_MCDY", "pT [GeV]; <H_{T}> [GeV]", n_bins, pt_edges), ["DiMuon_Pt", var_name]).GetValue()

        DY_profile.SetLineColor(ROOT.kViolet - 6)
        DY_profile.SetLineWidth(2)
        DY_profile.SetStats(0)

        MCDY_profile.SetLineColor(ROOT.kViolet - 6)
        MCDY_profile.SetLineWidth(2)
        MCDY_profile.SetLineStyle(2)


        DY_profile.SetTitle("")
        DY_profile.GetXaxis().SetTitle("p^{#mu#mu}_{T} [GeV]")
        DY_profile.GetXaxis().SetTitleSize(0.04)
        DY_profile.GetXaxis().SetTitleOffset(1.3)
        DY_profile.GetYaxis().SetTitle(f"<{VARIABLESFORAVERAGE[var][0]}> {VARIABLESFORAVERAGE[var][1]}")
        DY_profile.GetYaxis().SetTitleSize(0.04)
        DY_profile.GetYaxis().SetTitleOffset(1.2)

        DY_profile.SetMaximum(max(DY_profile.GetMaximum(), MCDY_profile.GetMaximum()) * 1.2)
        DY_profile.Draw("hist e")
        MCDY_profile.Draw("hist e same")

        legend = ROOT.TLegend(0.81, 0.78, 1.1, 0.89)
        legend.SetBorderSize(0)
        legend.SetFillStyle(0)
        legend.SetTextSize(0.04)
        legend.SetMargin(0.14)

        legend.AddEntry(DY_profile, "#bf{DY}", "l")
        legend.AddEntry(MCDY_profile, "#bf{MC DY}", "l")

        legend.Draw()

        # ── Zoom inset (bottom-right corner, 0–5 GeV) ────────────────────
        # box = ROOT.TBox(0, DY_profile.GetMinimum(),
        #                 5, DY_profile.GetMaximum() * 0.55)
        # box.SetFillColorAlpha(ROOT.kGray, 0.15)
        # box.SetLineColor(ROOT.kGray + 1)
        # box.SetLineWidth(1)
        # box.Draw()

        inset = ROOT.TPad("inset", "", 0.1, 0.51, 0.62, 0.9)
        inset.SetFillStyle(0)
        inset.SetFrameFillStyle(0)
        inset.SetFrameBorderMode(0)
        inset.SetLeftMargin(0.18)
        inset.SetRightMargin(0.04)
        inset.SetBottomMargin(0.22)
        inset.SetTopMargin(0.04)
        inset.Draw()
        inset.cd()

        # Clone profiles and restrict x range
        DY_zoom  = DY_profile.Clone(f"zoom_DY_{var_name}")
        MCDY_zoom = MCDY_profile.Clone(f"zoom_MCDY_{var_name}")

        DY_zoom.GetXaxis().SetRangeUser(0, 5)
        DY_zoom.SetTitle("")
        DY_zoom.GetXaxis().SetTitle("")
        DY_zoom.GetXaxis().SetTitleSize(0.08)
        DY_zoom.GetXaxis().SetTitleOffset(1.1)
        DY_zoom.GetXaxis().SetLabelSize(0.07)
        DY_zoom.GetYaxis().SetTitle("")
        DY_zoom.GetYaxis().CenterTitle(True)
        DY_zoom.GetYaxis().SetTitleSize(0.08)
        DY_zoom.GetYaxis().SetTitleOffset(0.7)
        DY_zoom.GetYaxis().SetLabelSize(0.07)
        DY_zoom.SetStats(0)

        def GetYMinMaxRangeZoom(hist1, hist2, ptmin, ptmax):
            for hist in (hist1, hist2):
                for bin in range(1, hist.GetNbinsX() + 1):
                    pt = hist.GetBinCenter(bin)
                    if pt < ptmin or pt > ptmax:
                        continue
                    bin1 = hist1.FindBin(pt)
                    bin2 = hist2.FindBin(pt)

                    if bin == 1:
                        ymin_zoom = min(hist1.GetBinContent(bin1), hist2.GetBinContent(bin2))
                        ymax_zoom = max(hist1.GetBinContent(bin1), hist2.GetBinContent(bin2))

                    if hist1.GetBinContent(bin1) < ymin_zoom:
                        ymin_zoom = hist1.GetBinContent(bin1)
                    if hist1.GetBinContent(bin1) > ymax_zoom:
                        ymax_zoom = hist1.GetBinContent(bin1)
                    if hist2.GetBinContent(bin2) < ymin_zoom:
                        ymin_zoom = hist2.GetBinContent(bin2)
                    if hist2.GetBinContent(bin2) > ymax_zoom:
                        ymax_zoom = hist2.GetBinContent(bin2)
            return ymin_zoom * 0.98, ymax_zoom * 1.02
        
        ymin_zoom, ymax_zoom = GetYMinMaxRangeZoom(DY_zoom, MCDY_zoom, 0, 5)

        DY_zoom.SetMinimum(ymin_zoom)
        DY_zoom.SetMaximum(ymax_zoom)

        DY_zoom.Draw("hist e")
        MCDY_zoom.Draw("hist e same")

        canvas.cd()



            
    

        path = f"new_plots/AverageVsZpT"
        output_name = f"{path}/{var}{out_suffix}.pdf"

        os.makedirs(path, exist_ok=True)
        canvas.SaveAs(output_name)
        canvas.Close()


def RapidityVarianceMethod(df_SingleMuon_var, df_MinBias_var, df_MCDYJets_var, df_MCMinBias_var, variables, out_suffix, weight):

    df_SingleMuon_var = VarianceCalculation(df_SingleMuon_var, "SingleMuon", weight)
    df_MinBias_var = VarianceCalculation(df_MinBias_var, "MinBias", weight)
    df_MCDYJets_var = VarianceCalculation(df_MCDYJets_var, "MCDYJets", weight)
    df_MCMinBias_var = VarianceCalculation(df_MCMinBias_var, "MCMinBias", weight)

    # df_SingleMuon_var = DiMuonPtCut(df_SingleMuon_var, 4)
    # df_MCDYJets_var = DiMuonPtCut(df_MCDYJets_var, 4)

    # Event-activity observables to slice in: bin edges, axis symbol and unit
    OBS_EDGES = {
        "PFCands_Ht": [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120],
        "PFCands_Pt2sum": [0, 10, 20, 30, 40, 50, 60, 70, 100, 150, 200, 250, 300, 350, 400],
        "PFCands_Psum": [0, 10, 20, 30, 40, 50, 60, 70, 100, 150, 200, 250, 300, 350, 400],
        "PFCands_P2sum": [0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 250, 300, 400, 500, 600, 800, 1000],
        "nPFCands":[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 18, 20, 25, 30, 40, 50],
        "PFCands_InvariantMass":[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160],
    }
    OBS_LABEL = {
        "PFCands_Ht": (r"$H_{T}$", "GeV"),
        "PFCands_Pt2sum":(r"$\sum p^{2}_{T}$", r"GeV$^{2}$"),
        "PFCands_Psum": (r"$\sum p$", "GeV"),
        "PFCands_P2sum": (r"$\sum p^{2}$", r"GeV$^{2}$"),
        "nPFCands": (r"$N^\mathrm{charged}_\mathrm{PF}$", ""),
        "PFCands_InvariantMass": (r"$m_\mathrm{inv}$", "GeV"),
    }

    observables = [v for v in variables if v in OBS_EDGES]
    if not observables:
        print(f"RapidityVarianceMethod: none of {list(variables)} are supported, choose from {list(OBS_EDGES)}")
        return

    obs_slices = {var: [(edges[i], edges[i+1]) for i in range(len(edges)-1)] for var, edges in OBS_EDGES.items()}
    obs_centers = {var: [(lo+hi)/2.0 for lo, hi in slices] for var, slices in obs_slices.items()}

    colour_DY = "#7B2D8B"
    colour_MinBias = "#C84B00"

    KIN_COL = {"mass": "DiMuon_Mass", "pt": "DiMuon_Pt"}
    KIN_LABEL = {"mass": r"$m_{\mu\mu}$", "pt": r"$p^{\mu\mu}_T$"}
    KIN_CUTS = {
        "mass": [
                (50,70),
                (70,86),
                (86,96),
                (96,110),
                (110,130),
                (130,150)
                ],
        "pt":   [
                (0,1),
                (1,2),
                (2,3),
                (3,4),
                (4,5),
                (5,6),
                (6,7),
                (7,8),
                (8,9),
                (9,10),
                (10,11),
                (11,12),
                (12,13),
                (13,14),
                (14,15),
                (15,16),
                (16,17),
                (17,18),
                (18,19),
                (19,20),
                ],
        "none": [None],
    }

    DY_names = {"DY", "MC DY"}

    datasets = [
        ("DY", df_SingleMuon_var, colour_DY, "-",  "o"),
        ("MC DY", df_MCDYJets_var, colour_DY, "--", "o"),
        ("MinBias", df_MinBias_var, colour_MinBias, "-",  "s"),
        ("MC MinBias", df_MCMinBias_var,  colour_MinBias, "--", "s"),
    ]

    # Build all result pointers for all observables × cuts × datasets × observable bins
    stats_ptrs = {}   # {(var, kin_axis, cut, name): [ResultPtr, ...]}
    for kin_axis, cuts in KIN_CUTS.items():
        for cut in cuts:
            for name, df, *_ in datasets:
                if cut is not None and name in DY_names:
                    lo, hi = cut
                    df_cut = df.Filter(f"{KIN_COL[kin_axis]} >= {lo} && {KIN_COL[kin_axis]} < {hi}")
                else:
                    df_cut = df
                for var in observables:
                    col = f"PFSelection_{var}"
                    ptrs = []
                    for low, high in obs_slices[var]:
                        obs_cut = f"{col} >= {low} && {col} < {high}"
                        ptrs.append(df_cut.Filter(obs_cut).Stats("PFSelection_PFCands_EventRapidity"))
                    stats_ptrs[(var, kin_axis, cut, name)] = ptrs

    # Single RunGraphs call — one event loop per df
    all_ptrs = [p for ptrs in stats_ptrs.values() for p in ptrs]
    ROOT.RDF.RunGraphs(all_ptrs)

    # Plot (one figure per observable × cut)
    for var in observables:
        edges = OBS_EDGES[var]
        obs_symbol, obs_unit = OBS_LABEL[var]
        if var == "nPFCands":
            obs_unit = ""
        if var != "nPFCands":
            obs_tag = var.replace("PFCands_", "")
        else:
            obs_tag = var

        for kin_axis, cuts in KIN_CUTS.items():

            for cut in cuts:

                inv_vars = {}
                for name, *_ in datasets:
                    inv_vars[name] = []
                    for i, (low, high) in enumerate(obs_slices[var]):

                        v = stats_ptrs[(var, kin_axis, cut, name)][i].GetValue().GetVar()

                        if v == 0:
                            print(f"Warning: Var=0 for {name}, {obs_tag} [{low},{high})")
                        inv_vars[name].append(1/v if v != 0 else 0)

                # <1/Var>_MB = sum_i (N_i/N_MB) * 1/Var_i over every observable bin, i.e. 1/Var averaged over MinBias events.
                # Same MinBias-weighted mean as Omega^h(obs), which is 1 by construction. Data and MC use their own MinBias.
                mean_inv_var = {}
                for mb_name in ("MinBias", "MC MinBias"):
                    mb_stats = [p.GetValue() for p in stats_ptrs[(var, kin_axis, cut, mb_name)]]
                    mb_stats = [s for s in mb_stats if s.GetVar() > 0]
                    mean_inv_var[mb_name] = sum(s.GetN() / s.GetVar() for s in mb_stats) / sum(s.GetN() for s in mb_stats)
                    print(f"<1/Var>_{mb_name} over {obs_tag} bins = {mean_inv_var[mb_name]:.4f}")

                for normalise in (False, True):
                    fig, ax = plt.subplots(figsize=(9, 5))

                    for edge in edges:
                        ax.axvline(edge, color='grey', linestyle='--', linewidth=0.5)

                    ax.set_xticks(edges)
                    ax.set_xticklabels(edges)

                    for name, df, color, ls, marker in datasets:
                        mb_name = "MC MinBias" if name.startswith("MC") else "MinBias"
                        norm = mean_inv_var[mb_name] if normalise else 1.0
                        ax.plot(obs_centers[var], [x / norm for x in inv_vars[name]], color=color, linestyle=ls, marker=marker, linewidth=1.8, markersize=6, label=name)

                    if normalise:
                        ax.axhline(1.0, color='grey', linestyle='-', linewidth=0.8)

                    ax.set_xlabel(f"{obs_symbol} [{obs_unit}]" if var != "nPFCands" else f"{obs_symbol}", fontsize=13)
                    if normalise:
                        ax.set_ylabel(r"$\mathrm{Var}^{-1}(y_\mathrm{had})\ /\ \langle \mathrm{Var}^{-1} \rangle_\mathrm{MB}$", fontsize=13)
                    else:
                        ax.set_ylabel(f"Inverse of Rapidity Variance per {obs_symbol} Bin", fontsize=13)
                    pad = 0.02 * (edges[-1] - edges[0])
                    ax.set_xlim(edges[0]-pad, edges[-1]+pad)
                    ax.set_ylim(bottom=0)
                    ax.legend(frameon=False, fontsize=11, ncol=2)
                    ax.tick_params(axis='y', labelsize=10)

                    handles, labels = ax.get_legend_handles_labels()
                    if cut is not None:
                        lo, hi = cut
                        cut_label = f"{KIN_LABEL[kin_axis]} $\\in [{lo},\\,{hi})$ GeV"
                        cut_tag = f"{kin_axis.capitalize()}_{lo}_{hi}"
                    else:
                        cut_label = "No Kinematic Cut on DY"
                        cut_tag = "Inclusive"
                        # cut_label = "$p^{\\mu\\mu}_{T} < 4$ GeV"
                        # cut_tag = "DiMuonPt4GeV"

                    ax.legend(handles=handles, labels=labels, frameon=False, fontsize=11, ncol=2, loc="upper left", handlelength=2.5, handletextpad=0.4)
                    ax.text(0.015, 0.86, cut_label, transform=ax.transAxes, fontsize=11, color=colour_DY, va='top')

                    fig.tight_layout()

                    output_dir = f"new_plots/RapidityVarianceMethod/{obs_tag}/{kin_axis.capitalize()}"
                    os.makedirs(output_dir, exist_ok=True)

                    norm_tag = "_Normalised" if normalise else ""
                    output = f"{output_dir}/EventRapidityVariance_{obs_tag}_{cut_tag}{norm_tag}{out_suffix}.pdf"
                    plt.savefig(output, bbox_inches='tight')
                    plt.close(fig)

                    print(f"\nSaved plot: {output}")





def RapidityVarianceKinematics3D(df_SingleMuon_var, df_MCDYJets_var, out_suffix, weight):
    """
    3-variable heatmap: H_T (x) × kinematic variable (y) × 1/Var(y_had) (colour).

    kinematic_axes : list of "mass" and/or "pt" — one figure is produced per entry.
                     Defaults to ["mass", "pt"].

    Only DY datasets are used because MinBias has no di-muon kinematics.
    """
    # df_SingleMuon_var = DiMuonPtCut(df_SingleMuon_var, 4)
    # df_MCDYJets_var = DiMuonPtCut(df_MCDYJets_var, 4)

    df_SingleMuon_var = VarianceCalculation(df_SingleMuon_var, "SingleMuon", weight)
    df_MCDYJets_var   = VarianceCalculation(df_MCDYJets_var,   "MCDYJets",   weight)

    datasets = [("DY", df_SingleMuon_var), ("MC DY", df_MCDYJets_var)]


    Ht_edges   = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120]
    Ht_slices  = [(Ht_edges[i], Ht_edges[i+1]) for i in range(len(Ht_edges)-1)]
    Ht_centers = [(lo + hi) / 2.0 for lo, hi in Ht_slices]
    Ht_edges_arr = np.array(Ht_edges, dtype=float)

    kinematic_axes = ["mass", "pt"]

    KIN_BINS = {
        "mass": [
            (50, 70),
            (70, 86),
            (86, 96),
            (96, 110),
            (110, 130),
            (130, 150),
        ],
        "pt": [
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 4),
            (4, 5),
            (5, 6),
            (6, 7),
            (7, 8),
            (8, 9),
            (9, 10),
        ],
    }

    KIN_COL = {
        "mass": "DiMuon_Mass",
        "pt": "DiMuon_Pt",
    }
    
    KIN_LABEL = {
        "mass": r"$m_{\mu\mu}\,[\mathrm{GeV}]$",
        "pt": r"$p^{\mu\mu}_{T}\,[\mathrm{GeV}]$",
    }

    for ax in kinematic_axes:
        if ax not in KIN_BINS:
            raise ValueError(f"Unknown kinematic_axis '{ax}'. Choose 'mass' or 'pt'.")



    """
        stats_ptrs is a dictionary mapping (kin_axis, dataset_name) tuples to their corresponding ptr_grid (2D list of ResultPtr objects).

        After the full loop over all kinematic axes and datasets, stats_ptrs contains 4 entries (2 axes × 2 datasets):

        stats_ptrs
        ├── ("mass", "DY")
        │     ├── row 0  [mass: 50– 70]  →  [Stats(Ht:0-10), Stats(Ht:10-20), ..., Stats(Ht:110-120)]
        │     ├── row 1  [mass: 70– 86]  →  [Stats(Ht:0-10), Stats(Ht:10-20), ..., Stats(Ht:110-120)]
        │     ├── ...
        │     └── row 5  [mass:130–150]  →  [Stats(Ht:0-10), Stats(Ht:10-20), ..., Stats(Ht:110-120)]
        │
        ├── ("mass", "MC DY")
        │     └── (same structure as above, but for MC events)
        │
        ├── ("pt", "DY")
        │     ├── row 0  [pt: 0–1]       →  [Stats(Ht:0-10), Stats(Ht:10-20), ..., Stats(Ht:110-120)]
        │     ├── row 1  [pt: 1–2]       →  [Stats(Ht:0-10), Stats(Ht:10-20), ..., Stats(Ht:110-120)]
        │     ├── ...
        │     └── row 9  [pt: 9–10]      →  [Stats(Ht:0-10), Stats(Ht:10-20), ..., Stats(Ht:110-120)]
        │
        └── ("pt", "MC DY")
            └── (same structure as above, but for MC events)

        Total ResultPtr objects: (6+6+10+10) × 12 = 384 lazy pointers.

        Access: stats_ptrs[(kin_axis, name)][i][j] → Stats pointer for events satisfying both the i-th kinematic bin and the j-th Ht bin, for the given dataset.
    """
    stats_ptrs = {}

    #Loop over the kinematic filter: DiMuon_Pt and DiMuon_Mass, i.e. "pt" and "mass"
    for kin_axis in kinematic_axes:

        # Define the kinematic slices and the corresponding column name, i.e. DiMuon_Pt and DiMuon_Mass
        kin_slices = KIN_BINS[kin_axis]
        kin_col = KIN_COL[kin_axis]

        # Loop over the datasets, i.e. DY and MCDY
        for name, df in datasets:

            # Define a fresh grid for this particular (kin_axis, dataset) combination to store the ResultPtr objects for each kinematic slice and Ht slice
            # This will become a list of rows, where each row is a list of pointers corresponding to the Ht slices for a given kinematic slice
            # It will look like this: 
            """
                ptr_grid is a 2D list (list of rows) built for a specific (kin_axis, dataset) pair.
                Each row corresponds to one kinematic bin (e.g. a DiMuon_Mass or DiMuon_Pt slice),
                and each element within that row is a ResultPtr for the variance of
                PFSelection_PFCands_EventRapidity in a specific Ht bin.

                After all kinematic bins are looped, ptr_grid has shape [n_kin_bins × n_Ht_bins].

                Example for kin_axis="mass", dataset="DY"  →  6 rows × 12 columns:

                                    Ht: 0–10    10–20    20–30    30–40  ...  110–120
                                    ┌──────────────────────────────────────────────────
                mass:  50– 70  (i=0) │  Stats()   Stats()  Stats()  Stats() ...  Stats()
                mass:  70– 86  (i=1) │  Stats()   Stats()  Stats()  Stats() ...  Stats()
                mass:  86– 96  (i=2) │  Stats()   Stats()  Stats()  Stats() ...  Stats()
                mass:  96–110  (i=3) │  Stats()   Stats()  Stats()  Stats() ...  Stats()
                mass: 110–130  (i=4) │  Stats()   Stats()  Stats()  Stats() ...  Stats()
                mass: 130–150  (i=5) │  Stats()   Stats()  Stats()  Stats() ...  Stats()
                                         (j=0)      (j=1)    (j=2)    (j=3)        (j=11)

                Access: ptr_grid[i][j]  →  Stats pointer for events with
                        KIN_BINS[kin_axis][i][0] ≤ kin_col < KIN_BINS[kin_axis][i][1]
                        AND
                        Ht_slices[j][0] ≤ PFSelection_PFCands_Ht < Ht_slices[j][1]

                No computation is triggered here — ptr_grid holds lazy ResultPtr objects.
                """

            ptr_grid = []

            # Loop over the kinematic slices, i.e. the bins in DiMuon_Pt or DiMuon_Mass
            for kin_low, kin_high in kin_slices:
                df_kin = df.Filter(f"{kin_col} >= {kin_low} && {kin_col} < {kin_high}")

                # For each kinematic slice (i.e. each DiMuon_Pt or DiMuon_Mass bin), we will create a row in the grid that contains the ResultPtr objects for each Ht slice
                # It will look like this: [[ptr_kin1_ht1, ptr_kin1_ht2, ...], [ptr_kin2_ht1, ptr_kin2_ht2, ...], ...]
                """
                    Per kinematic bin, i.e. a specific bin of DiMuon_Pt or DiMuon_Mass, we create a row in the grid.
                    Each element in the row is a ResultPtr object representing the variance of PFSelection_PFCands_EventRapidity in a specific Ht bin.

                    row = [
                        Stats(Ht: 0–10),   Stats(Ht: 10–20),  Stats(Ht: 20–30),
                        Stats(Ht: 30–40),  Stats(Ht: 40–50),  Stats(Ht: 50–60),
                        Stats(Ht: 60–70),  Stats(Ht: 70–80),  Stats(Ht: 80–90),
                        Stats(Ht: 90–100), Stats(Ht: 100–110), Stats(Ht: 110–120)
                    ]
                """
                row = []

                # Loop over the Ht slices, i.e. the bins in PFSelection_PFCands_Ht, and create a ResultPtr for the variance of PFSelection_PFCands_EventRapidity in that Ht slice
                for ht_low, ht_high in Ht_slices:
                    df_cell = df_kin.Filter(f"PFSelection_PFCands_Ht >= {ht_low} && " f"PFSelection_PFCands_Ht < {ht_high}")
                    row.append(df_cell.Stats("PFSelection_PFCands_EventRapidity"))

                # After processing all Ht slices for this kinematic slice, we append the row to the ptr_grid
                ptr_grid.append(row)

            stats_ptrs[(kin_axis, name)] = ptr_grid

    # Single RunGraphs call — one event loop per df
    all_ptrs = [ptr for grid in stats_ptrs.values() for row in grid for ptr in row]
    
    # Compute all pointers in parallel (one event loop per df)
    ROOT.RDF.RunGraphs(all_ptrs)



    for kin_axis in kinematic_axes:
        kin_slices  = KIN_BINS[kin_axis]
        kin_label   = KIN_LABEL[kin_axis]
        kin_centers = [(lo + hi) / 2.0 for lo, hi in kin_slices]
        kin_edges_arr = np.array(sorted(set(e for b in kin_slices for e in b)), dtype=float)

        def extract_grid(name):
            grid = np.zeros((len(kin_slices), len(Ht_slices)))
            for i, (kin_low, kin_high) in enumerate(kin_slices):
                for j, (ht_low, ht_high) in enumerate(Ht_slices):
                    var = stats_ptrs[(kin_axis, name)][i][j].GetValue().GetVar()
                    if var == 0:
                        print(f"Warning: Var=0 for {name}, {kin_axis} in [{kin_low},{kin_high}), Ht in [{ht_low},{ht_high})")
                    grid[i, j] = 1 / var if var != 0 else "None"
            return grid

        Data_grid = extract_grid("DY")
        MC_grid = extract_grid("MC DY")

        # Plot 
        vmin = min(Data_grid.min(), MC_grid.min())
        vmax = max(Data_grid.max(), MC_grid.max())
        # vmax = 100

        fig, (ax_Data, ax_MC) = plt.subplots(1, 2, figsize=(16, 6))

        def draw_panel(ax, Z, title):
            mesh = ax.pcolormesh(Ht_edges_arr, kin_edges_arr, Z, cmap='viridis', vmin=vmin, vmax=vmax)
            cbar = fig.colorbar(mesh, ax=ax)
            cbar.set_label(r"$1/\mathrm{Var}(y_\mathrm{had})$", fontsize=11)
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.set_xlabel(r"$H_T\,[\mathrm{GeV}]$", fontsize=12)
            ax.set_ylabel(kin_label, fontsize=12)
            ax.set_xticks(Ht_edges)
            ax.set_xticklabels([str(e) for e in Ht_edges], ha='center', fontsize=8)
            ax.set_yticks(kin_edges_arr)

            threshold = (vmin + vmax) / 2.0
            for i, y_c in enumerate(kin_centers):
                for j, x_c in enumerate(Ht_centers):
                    val = Z[i, j]
                    txt_color = "white" if val < threshold else "black"
                    ax.text(x_c, y_c, f"{val:.2f}", ha="center", va="center", color=txt_color, fontsize=8)

        draw_panel(ax_Data, Data_grid, "Data DY")
        draw_panel(ax_MC, MC_grid, "MC DY")

        fig.suptitle("")
        fig.tight_layout()

        # Extract grids and plot one figure per kinematic axis
        output_dir = "new_plots/RapidityVarianceMethod"
        os.makedirs(output_dir, exist_ok=True)

        output = (f"{output_dir}/RapidityVarianceKinematics3D_Ht_{kin_axis.capitalize()}{out_suffix}.pdf")
        plt.savefig(output, bbox_inches='tight')
        plt.close(fig)

        print(f"\nSaved: {output}")


def MomentumFractions(df_SingleMuon_var, df_MCDYJets_var, pt_cuts, out_suffix):

    samples = [
        ("DataDY", df_SingleMuon_var),
        ("MCDY", df_MCDYJets_var),
    ]
    

    for label, df in samples:

        print(f"\n\n----------Processing Sample: {label}----------\n")

        df = df.Redefine("DiMuon_xminll", "min(DiMuon_xmaxll, DiMuon_xminll)")
        df = df.Redefine("DiMuon_xmaxll", "max(DiMuon_xmaxll, DiMuon_xminll)")

        x_min_plot = 6e-4
        y_min_plot = 1e-3

        x_max_plot = 1e-1
        y_max_plot = 6e-1
        # min_plot = 1e-4


        # print(f"Entries = {df.Count().GetValue()}\n")

        for pt_cut in (pt_cuts or [None]):

            if pt_cut is not None:
                print(f"\nApplying diMuon pT cut: {pt_cut} GeV for mass-rapidity plot...")
                df_cut = df.Filter(f"DiMuon_Pt < {pt_cut}")
                # print(f"Entries after {pt_cut} GeV pT cut = {df_cut.Count().GetValue()}\n\n")

            else:
                df_cut = df
                print("No diMuon pT cut applied for mass-rapidity plot...")
                # print(f"Entries after no pT cut = {df_cut.Count().GetValue()}\n\n")
    
            h_ptr = df_cut.Histo2D(
                (
                    "h_2D",
                    "",
                    100, x_min_plot, x_max_plot,
                    100, y_min_plot, y_max_plot,
                ),
                "DiMuon_xminll",   # x axis
                "DiMuon_xmaxll",   # y axis
            )

            hist = h_ptr.GetValue()
            hist.SetDirectory(0)
            hist.GetXaxis().SetTitle("x_{min}^{#mu#mu}")
            hist.GetYaxis().SetTitle("x_{max}^{#mu#mu}")

            # print("N_200 =", df.Filter("DiMuon_Mass > 200").Count().GetValue())
            # print("N_50 =", df.Filter("DiMuon_Mass < 50").Count().GetValue())

            if hist.GetEntries() == 0 or hist.Integral() == 0:
                print("ERROR: histogram is empty. Nothing will be visible.")
                return

            NormaliseHist(hist)

            # print("N_200 after NORM =", df.Filter("DiMuon_Mass > 200").Count().GetValue())
            # print("N_50 after NORM =", df.Filter("DiMuon_Mass < 50").Count().GetValue())

            canvas = ROOT.TCanvas(f"canvas_{out_suffix}", "Momentum fractions", 900, 700)
            canvas.SetRightMargin(0.18)
            canvas.cd()
            canvas.SetLogx()
            canvas.SetLogy()
            canvas.SetLogz()

            hist.SetTitle(f"{label}")
            hist.SetStats(0)
            hist.SetMinimum(0)
            hist.GetXaxis().SetTitleOffset(1.2)
            hist.GetYaxis().SetTitleOffset(1.2)
            hist.GetZaxis().SetTitle("Normalised Entries")
            hist.GetZaxis().SetTitleOffset(1.5)
            # hist.GetZaxis().SetRangeUser(hist.GetMinimum(), hist.GetMaximum())
            hist.GetZaxis().SetRangeUser(1e-8, 1)

            
            ROOT.gStyle.SetPalette(ROOT.kRainBow)
            ROOT.gStyle.SetNumberContours(255)
            # ROOT.gStyle.SetOptStat(100000)

            hist.Draw("COLZ")
            ROOT.gStyle.SetPalette(61)


            # -------- Lines for mass values --------

            sqrt_s = 13000 # GeV

            masses = [(ROOT.kBlack, 20), (ROOT.kGreen, 60), (ROOT.kRed, 90.0), (ROOT.kBlue, 120), (ROOT.kMagenta, 150)]
            rapidities = [(ROOT.kGray + 2, 0), (ROOT.kOrange + 7, 1.0), (ROOT.kCyan + 2, 2), (ROOT.kViolet + 1, 2.4)] 

            legend_mll = ROOT.TLegend(0.52, 0.13, 0.68, 0.4)
            legend_mll.SetMargin(0.2)
            legend_yll = ROOT.TLegend(0.69, 0.13, 0.815, 0.34)
            legend_yll.SetMargin(0.3)

            for legend in (legend_mll, legend_yll):
                # legend.SetBorderSize(0)
                # legend.SetFillStyle(0)
                legend.SetTextSize(0.026)
                

            for m in masses:
                line = ROOT.TF1(
                    f"mass_line_{int(m[1])}",
                    f"({m[1] * m[1]})/({sqrt_s * sqrt_s}*x)",
                    1e-4,
                    x_max_plot,
                )

                line.SetLineColor(m[0])
                line.SetLineWidth(3)
                line.SetLineStyle(3)
                line.Draw("SAME")

                x_label = x_max_plot * 0.6
                y_label = (m[1] * m[1]) / (sqrt_s * sqrt_s * x_label)

                legend_mll.AddEntry(line, f"m_{{#mu#mu}} = {m[1]:.0f} GeV", "l")

            for y in rapidities:
                slope = ROOT.TMath.Exp(2.0 * y[1])
                slope_neg = ROOT.TMath.Exp(2.0 * -y[1])

                line = ROOT.TF1(
                    f"rapidity_line_{str(y[1]).replace('.', 'p')}",
                    f"{slope}*x",
                    1e-4,
                    x_max_plot,
                )

                line_neg = ROOT.TF1(
                    f"rapidity_line_neg_{str(y[1]).replace('.', 'p')}",
                    f"{slope_neg}*x",
                    1e-4,
                    x_max_plot,
                )

                line.SetLineColor(y[0])
                line_neg.SetLineColor(y[0])
                line.SetLineWidth(3)
                line_neg.SetLineWidth(3)
                line.SetLineStyle(8)
                line_neg.SetLineStyle(8)
                line.Draw("SAME")
                line_neg.Draw("SAME")

                legend_yll.AddEntry(line, f"|y_{{#mu#mu}}| = {y[1]:.1f}", "l")

            legend_mll.Draw()
            legend_yll.Draw()

            if pt_cut is not None:
                dummy = ROOT.TObject()
                legend_ptcut = ROOT.TLegend(0.11, 0.86, 0.26, 0.89)
                legend_ptcut.SetTextSize(0.026)
                legend_ptcut.SetMargin(0.1)
                legend_ptcut.SetBorderSize(0)
                legend_ptcut.SetFillStyle(0)
                legend_ptcut.AddEntry(dummy, f"#bf{{p^{{#mu#mu}}_{{T}} < {pt_cut} GeV}}", "")
                legend_ptcut.Draw()

            if pt_cut is None:
                canvas.SaveAs(f"new_plots/xmaxllxminll_MllYll/xmaxll_xminll_{label}{out_suffix}.pdf")
            else:
                canvas.SaveAs(f"new_plots/xmaxllxminll_MllYll/xmaxll_xminll_DiMuonPtCut{pt_cut}GeV_{label}{out_suffix}.pdf")
                
            canvas.Close()

    print("Momentum fraction plots saved")

def MassRapidity(df_SingleMuon_var, df_MCDYJets_var, pt_cuts, out_suffix):

    samples = [
        ("DataDY", df_SingleMuon_var),
        ("MCDY", df_MCDYJets_var),
    ]
    

    for label, df in samples:

        print(f"\n\n----------Processing Sample: {label}----------\n")

        xmax_plot = 0.02
        ymax_plot = 0.1

        xmin_plot = 1e-3
        
        # print(f"Entries = {df.Count().GetValue()}\n")

        for pt_cut in (pt_cuts or [None]):

            if pt_cut is not None:
                print(f"\nApplying diMuon pT cut: {pt_cut} GeV for mass-rapidity plot...")
                df_cut = df.Filter(f"DiMuon_Pt < {pt_cut}")
                # print(f"Entries after {pt_cut} GeV pT cut = {df_cut.Count().GetValue()}\n\n")

            else:
                df_cut = df
                print("No diMuon pT cut applied for mass-rapidity plot...")
                # print(f"Entries after no pT cut = {df_cut.Count().GetValue()}\n\n")

            h_ptr = df_cut.Histo2D(
                            (
                                "h_2D",
                                "",
                                200, 0, 400,
                                100, -3, 3,
                            ),
                            "DiMuon_Mass",   # x axis
                            "DiMuon_Rapidity",   # y axis
                        )

            hist = h_ptr.GetValue()
            hist.SetDirectory(0)
            hist.GetXaxis().SetTitle("m_{#mu#mu} [GeV]")
            hist.GetYaxis().SetTitle("y_{#mu#mu}")
            hist.GetXaxis().SetTitleOffset(1.1)

            # print("N_200 =", df.Filter("DiMuon_Mass > 200").Count().GetValue())
            # print("N_50 =", df.Filter("DiMuon_Mass < 50").Count().GetValue())

            if hist.GetEntries() == 0 or hist.Integral() == 0:
                print("ERROR: histogram is empty. Nothing will be visible.")
                return

            NormaliseHist(hist)

            # print("N_200 after NORM =", df.Filter("DiMuon_Mass > 200").Count().GetValue())
            # print("N_50 after NORM =", df.Filter("DiMuon_Mass < 50").Count().GetValue())

            canvas = ROOT.TCanvas(f"canvas_{out_suffix}", "Mll_Yll", 900, 700)
            canvas.SetRightMargin(0.18)
            canvas.cd()
            # canvas.SetLogx()
            # canvas.SetLogy()
            canvas.SetLogz()

            hist.SetTitle(f"{label}")
            hist.SetStats(0)
            # hist.SetMinimum(0)
            hist.GetYaxis().SetTitleOffset(1.2)
            hist.GetZaxis().SetTitle("Normalised Entries")
            hist.GetZaxis().SetTitleOffset(1.5)
            hist.GetZaxis().SetRangeUser(1e-8, 1)

        
            ROOT.gStyle.SetPalette(ROOT.kRainBow)
            ROOT.gStyle.SetNumberContours(255)
            # ROOT.gStyle.SetOptStat(100000)

            hist.Draw("COLZ")
            ROOT.gStyle.SetPalette(61)


            # -------- Lines for mass values --------

            masses = [(ROOT.kBlack, 20), (ROOT.kGreen, 60), (ROOT.kRed, 90.0), (ROOT.kBlue, 120), (ROOT.kMagenta, 150)]
            rapidities = [(ROOT.kGray + 2, 0), (ROOT.kOrange + 7, 1.0), (ROOT.kCyan + 2, 2), (ROOT.kViolet + 1, 2.4)] 

            legend_mll = ROOT.TLegend(0.52, 0.13, 0.68, 0.4)
            legend_mll.SetMargin(0.2)
            legend_yll = ROOT.TLegend(0.69, 0.13, 0.815, 0.34)
            legend_yll.SetMargin(0.3)

            for legend in (legend_mll, legend_yll):
                # legend.SetBorderSize(0)
                # legend.SetFillStyle(0)
                legend.SetTextSize(0.026)
                


            x_min = hist.GetXaxis().GetXmin()
            x_max = hist.GetXaxis().GetXmax()
            y_min = hist.GetYaxis().GetXmin()
            y_max = hist.GetYaxis().GetXmax()

            mll_lines = []
            yll_lines = []

            for m in masses:
                line = ROOT.TLine(m[1], y_min, m[1], y_max)

                line.SetLineColor(m[0])
                line.SetLineWidth(3)
                line.SetLineStyle(3)
                mll_lines.append(line)
                line.Draw("SAME")

                legend_mll.AddEntry(line, f"m_{{#mu#mu}} = {m[1]:.0f} GeV", "l")

            for y in rapidities:
                line_plus = ROOT.TLine(x_min, y[1], x_max, y[1])
                legend_minus = ROOT.TLine(x_min, -y[1], x_max, -y[1])
                
                for line in [line_plus, legend_minus]:
                    line.SetLineColor(y[0])
                    line.SetLineWidth(3)
                    line.SetLineStyle(8)
                    yll_lines.append(line)
                    line.Draw("SAME")

                legend_yll.AddEntry(line_plus, f"|y_{{#mu#mu}}| = {y[1]:.1f}", "l")

            legend_mll.Draw()
            legend_yll.Draw()

            if pt_cut is not None:
                dummy = ROOT.TObject()
                legend_ptcut = ROOT.TLegend(0.67, 0.86, 0.8, 0.89)
                legend_ptcut.SetTextSize(0.026)
                legend_ptcut.SetMargin(0.1)
                legend_ptcut.SetBorderSize(0)
                legend_ptcut.SetFillStyle(0)
                legend_ptcut.AddEntry(dummy, f"#bf{{p^{{#mu#mu}}_{{T}} < {pt_cut} GeV}}", "")
                legend_ptcut.Draw()

            if pt_cut is None:
                canvas.SaveAs(f"new_plots/xmaxllxminll_MllYll/Mll_Yll_{label}{out_suffix}.pdf")
            else:
                canvas.SaveAs(f"new_plots/xmaxllxminll_MllYll/Mll_Yll_DiMuonPtCut{pt_cut}GeV_{label}{out_suffix}.pdf")
                
            canvas.Close()

    print("Mass-Rapidity plots saved")

    


def SigmaEff(df_SingleMuon_var, df_MinBias_var, df_MCDYJets_var, df_MCMinBias_var, variables, pt_cuts, out_suffix, bins, b_bins, binweight, mass_rapidity):

    if mass_rapidity not in ["mass", "rapidity"]:
        raise ValueError("the flag \"--mass-rapidity\" must be either 'mass' or 'rapidity'")

    quantile_bins = array.array("d", bins)

    if b_bins is None:
        b_bins = array.array("d", np.linspace(0, 1, 20))
        # b_bins = array.array("d", np.concatenate([
        #                           np.arange(0.00, 0.10, 0.01),
        #                           np.arange(0.10, 0.20, 0.01),
        #                           np.arange(0.20, 1.05, 0.05)
        #                         ])
        #                     )
    else:
        b_bins = array.array("d", b_bins)

    pt_cuts = parse_pt_cuts(pt_cuts)
    
    colours = [
            ROOT.kBlue + 1,
            ROOT.kGreen + 2,
            ROOT.kMagenta + 1,
            ROOT.kOrange + 7,
            ROOT.kCyan + 1,
            ROOT.kViolet + 1,
            ROOT.kAzure + 1,
            ROOT.kPink + 7,
            ROOT.kTeal + 3,
            ROOT.kSpring + 5,
            ROOT.kYellow + 2,
            ROOT.kGray + 2,
            ROOT.kBlack,
            ROOT.kRed,
            ROOT.kOrange - 3,
            ROOT.kGreen - 3,
            ROOT.kMagenta - 3,
            ROOT.kCyan - 3,
            ROOT.kViolet - 3,
            ROOT.kAzure - 3,
            ROOT.kPink - 3,
        ]

    sigma0 = 70  # mb
    
    for var in variables:
        if var in ["PFCands_pt", "PFCands_eta", "PFCands_phi", "PFCands_pvAssocQuality"]:
            continue

        label = VARIABLES[var]
        binning = BINNING[var]
        y_title = "#sigma_{eff}"

        q_column = f"{var}_InvQ"
        plot_xlabel = f"impact parameter b"
        b_column = f"{var}_b"

        canvas = ROOT.TCanvas(f"c_quantile_ptscan_{var}", "", 1500, 1400)
        canvas.cd()
        canvas.SetBottomMargin(0.05)
        canvas.SetRightMargin(0.26)
        canvas.SetTopMargin(0.05)

        BuildQuantile(df_MinBias_var, var, "MB")
        BuildQuantile(df_MCMinBias_var, var, "MCMB")

        df_MinBias_q = ApplyQuantileAndIP(df_MinBias_var, var, "MB")
        df_MCMinBias_q = ApplyQuantileAndIP(df_MCMinBias_var, var, "MCMB")


        h_MinBias_ptr = df_MinBias_q.Histo1D((f"h_MinBias_{var}_quantile", f"; {plot_xlabel}; {y_title}", len(b_bins) - 1, b_bins), b_column)
        h_MCMinBias_ptr = df_MCMinBias_q.Histo1D((f"h_MCMinBias_{var}_quantile", f"; {plot_xlabel}; {y_title}", len(b_bins) - 1, b_bins), b_column)

        h_MinBias = h_MinBias_ptr.GetValue()
        h_MCMinBias = h_MCMinBias_ptr.GetValue()

        NormaliseHist(h_MinBias, binweight)
        NormaliseHist(h_MCMinBias, binweight)

        x_values = []

        sigma_eff_data_values = []
        sigma_eff_mc_values = []
        sigma_eff_data_errors = []
        sigma_eff_mc_errors = []
        # inv_mass = [(0, 15), (15, 20), (20, 30), (30, 40), (40, 50), (50, 60), (60, 70), (70, 86), (86, 96), (96, 100), (100, 110), (110, 120), (120, 130), (130, 140), (140, 150)]
        # inv_mass = [(0, 10), (10, 20), (20, 30), (30, 40), (40, 50), (50, 60), (60, 70), (70, 80), (80, 90), (90, 100), (100, 110), (110, 120), (120, 130), (130, 140), (140, 150)]
        inv_mass = [# (0, 10),
                    # (10, 20), 
                    # (20, 30), 
                    # (30, 40), 
                    # (40, 50), 
                    # (50, 60), 
                    # (60, 70), 
                    # (70, 86), 
                    # (96, 100), 
                    # (100, 110), 
                    # (110, 120), 
                    # (120, 130), 
                    # (130, 140), 
                    # (140, 150)
                    # (0, 50),
                    (50, 70),
                    (70, 86),
                    (86, 96),
                    (96, 110),
                    (110, 130),
                    (130, 150)
                    ]
        rapidity = [(-2.4, -2), (-2, -1), (-1, -0.5), (-0.5, 0), (0, 0.5), (0.5, 1), (1, 2), (2, 2.4)]
        abs_rapidity = [(0, 0.5), (0.5, 1), (1, 1.5), (1.5, 2), (2, 2.4)]


        for index, pt_cut in enumerate(pt_cuts):
        
            canvas.cd()          

            print(f"\n\nProcessing DiMuon pT cut: {pt_cut} GeV...\n")


            if pt_cut is None or len(pt_cuts) == 0:
                print(f"\n\nNo DiMuon pT cut specified for quantile plot.\n")

                df_SingleMuon_q = df_SingleMuon_var
                df_MCDYJets_q = df_MCDYJets_var

            else:
                pt_cut = int(pt_cut)
                print(f"\n\nApplying DiMuon pT cuts for quantile plot: {pt_cut} GeV...\n")

                df_SingleMuon_q = DiMuonPtCut(df_SingleMuon_var, pt_cut)
                df_MCDYJets_q = DiMuonPtCut(df_MCDYJets_var, pt_cut)

                
            df_SingleMuon_q = ApplyQuantileAndIP(df_SingleMuon_q, var, "MB")
            df_MCDYJets_q = ApplyQuantileAndIP(df_MCDYJets_q, var, "MCMB")

            for idx, mass_rap in enumerate(inv_mass) if mass_rapidity == "mass" else enumerate(abs_rapidity):

                print(f"\n\nProcessing DiMuon {mass_rap} range:...\n")

                if mass_rapidity == "mass":
                    mass = mass_rap

                    print(f"{mass[0]} - {mass[1]} GeV...\n")
        
                    df_SingleMuon_massrap = df_SingleMuon_q.Filter(f"DiMuon_Mass >= {mass[0]} && DiMuon_Mass < {mass[1]}")
                    df_MCDYJets_massrap = df_MCDYJets_q.Filter(f"DiMuon_Mass >= {mass[0]} && DiMuon_Mass < {mass[1]}")


                elif mass_rapidity == "rapidity":
                    rapidity = mass_rap
                    
                    print(f"{abs_rapidity[0]} - {abs_rapidity[1]}...\n")
        
                    df_SingleMuon_massrap = df_SingleMuon_q.Filter(f"abs(DiMuon_Rapidity) >= {rapidity[0]} && abs(DiMuon_Rapidity) < {rapidity[1]}")
                    df_MCDYJets_massrap = df_MCDYJets_q.Filter(f"abs(DiMuon_Rapidity) >= {rapidity[0]} && abs(DiMuon_Rapidity) < {rapidity[1]}")
                print(idx)
                colour = colours[idx]

                    
                if mass_rapidity == "mass":                
                    h_SingleMuon_ptr = df_SingleMuon_massrap.Histo1D((f"h_SingleMuon_{var}_{mass[0]}_{mass[1]}_{pt_cut}", f"; {plot_xlabel}; {y_title}", len(b_bins) - 1, b_bins), b_column)
                    h_MCDYJets_ptr = df_MCDYJets_massrap.Histo1D((f"h_MCDYJets_{var}_{mass[0]}_{mass[1]}_{pt_cut}", f"; {plot_xlabel}; {y_title}", len(b_bins) - 1, b_bins), b_column)
                else:
                    h_SingleMuon_ptr = df_SingleMuon_massrap.Histo1D((f"h_SingleMuon_{var}_{rapidity[0]}_{rapidity[1]}_{pt_cut}", f"; {plot_xlabel}; {y_title}", len(b_bins) - 1, b_bins), b_column)
                    h_MCDYJets_ptr = df_MCDYJets_massrap.Histo1D((f"h_MCDYJets_{var}_{rapidity[0]}_{rapidity[1]}_{pt_cut}", f"; {plot_xlabel}; {y_title}", len(b_bins) - 1, b_bins), b_column)

                h_SingleMuon = h_SingleMuon_ptr.GetValue()
                h_MCDYJets = h_MCDYJets_ptr.GetValue()

                NormaliseHist(h_SingleMuon, binweight)
                NormaliseHist(h_MCDYJets, binweight)



                ratio_Data = h_SingleMuon.Clone(f"ratio_sigmaeff_ptscan_data_{var}_pt{pt_cut}")
                ratio_Data.Divide(h_MinBias)
                ratio_Data.SetLineColor(colour)
                ratio_Data.SetLineWidth(2)
                ratio_Data.SetMarkerColor(colour)
                ratio_Data.GetXaxis().SetTitle(plot_xlabel)
                ratio_Data.GetYaxis().SetTitle(y_title)
                
                ratio_MC = h_MCDYJets.Clone(f"ratio_sigmaeff_ptscan_mc_{var}_pt{pt_cut}")
                ratio_MC.Divide(h_MCMinBias)
                ratio_MC.SetLineColor(colour)
                ratio_MC.SetLineWidth(2)
                ratio_MC.SetLineStyle(2)
                ratio_MC.SetMarkerColor(colour)
                ratio_MC.GetXaxis().SetTitle(plot_xlabel)
                ratio_MC.GetYaxis().SetTitle(y_title)


                width_list = []
                normalization_Data = 0.0
                normalization_MC = 0.0
                integral_Data = 0.0
                integral_MC = 0.0
                bin_values = []
                E_Data_list = []
                E_MC_list = []
                EError_Data_list = []
                EError_MC_list = []


                for i in range(1, ratio_Data.GetNbinsX() + 1):

                    b_low = ratio_Data.GetBinLowEdge(i)
                    b_high = ratio_Data.GetBinLowEdge(i) + ratio_Data.GetBinWidth(i)

                    # Calculate the width each bin
                    width = np.pi * (b_high**2 - b_low**2)
                    width_list.append(width)

                    # Enhancement factor (i.e. DY/MinBias) in each bin of the ratio histogram 
                    E_Data = ratio_Data.GetBinContent(i)
                    E_MC = ratio_MC.GetBinContent(i)
                    EError_Data = ratio_Data.GetBinError(i)
                    EError_MC = ratio_MC.GetBinError(i)
                    E_Data_list.append(E_Data)
                    E_MC_list.append(E_MC)
                    EError_Data_list.append(EError_Data)
                    EError_MC_list.append(EError_MC)

                    # Calculate the normalization and integral for Data and MC
                    normalization_Data += width * E_Data
                    normalization_MC += width * E_MC

                    integral_Data += width * E_Data**2
                    integral_MC += width * E_MC**2

                    bin_values.append((width, E_Data, EError_Data, E_MC, EError_MC))

                sigma_eff_Data = (normalization_Data / integral_Data if integral_Data != 0 else 0)
                sigma_eff_MC = (normalization_MC / integral_MC if integral_MC != 0 else 0)

        
                def sigma_eff_error(width_list, E_list, Eerror_list):
                    """
                    Gaussian error propagation for

                        sigma_eff = sum(width_i * E_i) / sum(width_i * E_i^2)

                    assuming only E_i has an uncertainty and the E_i uncertainties are statistically independent.
                    """

                    normalization = sum(width * E for width, E in zip(width_list, E_list))

                    integral = sum(width * E**2 for width, E in zip(width_list, E_list))

                    if integral == 0:
                        return 0

                    sigma_eff = normalization / integral

                    error_squared = 0.0

                    for width, E, Eerror in zip(width_list, E_list, Eerror_list):

                        derivative = (width * (1 - 2 * E * sigma_eff)/integral)

                        error_squared += (derivative * Eerror)**2

                    return np.sqrt(error_squared)
                

                sigma_eff_data_values.append(sigma_eff_Data)
                sigma_eff_mc_values.append(sigma_eff_MC)

                sigma_eff_error_Data = sigma_eff_error(width_list, E_Data_list, EError_Data_list)
                sigma_eff_error_MC = sigma_eff_error(width_list, E_MC_list, EError_MC_list)
                    
                        


        print(f"\nNormalization for Data: {normalization_Data}\n\n")
        print(f"Normalization for MC: {normalization_MC}\n\n")

        print(f"\n\nSigma_eff values for Data: {sigma_eff_data_values}")
        print(f"\n\nSigma_eff values for MC: {sigma_eff_mc_values}\n\n")

        # print(len(inv_mass))
        # print(len(sigma_eff_data_values))

        inv_mass_centers = [0.5 * (a + b) for a, b in inv_mass]
        rapidity_centers = [-2.2, -1.5, -0.75, -0.25, 0.25, 0.75, 1.5, 2.2]
        abs_rapidity_centers = [0.25, 0.75, 1.25, 1.75, 2.2]

        mass_edges = sorted(set(
            edge for bin_range in inv_mass for edge in bin_range
        ))
        abs_rapidity_edges = sorted(set(
            edge for bin_range in abs_rapidity for edge in bin_range
        ))

        plt.figure(figsize=(10, 6))
        plt.grid(zorder=0)

        if mass_rapidity == "mass":
            plt.errorbar(inv_mass_centers, sigma_eff_data_values, yerr=sigma_eff_error_Data, fmt='o', capsize=3, label='Data DY/MinBias', color='blue', zorder=3)
            plt.errorbar(inv_mass_centers, sigma_eff_mc_values, yerr=sigma_eff_error_MC, fmt='o', capsize=3, label='MC DY/MinBias', color='red', zorder=3)
            plt.xlabel(fr'$m_{{\mu\mu}}$ [GeV]', fontsize=22)
            plt.xticks(mass_edges)
        else:
            plt.errorbar(abs_rapidity_centers, sigma_eff_data_values, yerr=sigma_eff_error_Data, fmt='o', capsize=3, label='Data DY/MinBias', color='blue', zorder=3)
            plt.errorbar(abs_rapidity_centers, sigma_eff_mc_values, yerr=sigma_eff_error_MC, fmt='o', capsize=3, label='MC DY/MinBias', color='red', zorder=3)
            plt.xlabel(fr'$|y_{{\mu\mu}}|$', fontsize=22)
            plt.xticks(abs_rapidity_edges)

        
        
        plt.ylabel(fr'$\frac{{\sigma_{{\mathrm{{eff}}}}}}{{\sigma_{{0}}}}$', fontsize=26)
        plt.yscale('log')
        positive_sigma_eff_values = [value for value in sigma_eff_data_values + sigma_eff_mc_values if value > 0]
        plt.ylim(min(positive_sigma_eff_values) * 0.95, max(positive_sigma_eff_values) * 1.2)
        plt.grid(which='both', axis='y', zorder=0, alpha=0.5)
        plt.tick_params(axis='both', which='both', left=True, labelsize=14, length=6, width=0.8, direction='in')
        plt.legend(title=fr"{VARIABLESFORPYTHON[var]}; $p^{{\mu\mu}}_{{\mathrm{{T}}}} < 4 \, \mathrm{{GeV}}$", fontsize=14, loc='upper left', frameon=True, alignment = "left", handletextpad=0.1, title_fontsize=12)
        plt.tight_layout()

        if mass_rapidity == "mass":
            output_dir = f"new_plots/sigma_eff/{var}_SigmaEff_MassBins_4GeVZPtCut{out_suffix}.pdf"
        else:
            output_dir = f"new_plots/sigma_eff/{var}_SigmaEff_RapidityBins_4GeVZPtCut{out_suffix}.pdf"

        plt.savefig(output_dir)
        print(f"Saved plot: {output_dir}")

        plt.show()




        # output_dir = f"new_plots/sigma_eff"
        # os.makedirs(output_dir, exist_ok=True)

        # output_name = f"{output_dir}/{var}_SigmaEff{out_suffix}.pdf"
        # canvas.SaveAs(output_name)

        canvas.Close()






def EnhancementFactorRatioToZ(df_SingleMuon_var, df_MinBias_var, df_MCDYJets_var, df_MCMinBias_var, variables, pt_cuts, out_suffix, bins, b_bins, binweight, mass_rapidity):

    if mass_rapidity not in ["mass", "rapidity"]:
        raise ValueError("the flag \"--mass-rapidity\" must be either 'mass' or 'rapidity'")

    quantile_bins = array.array("d", bins)

    if b_bins is None:
        b_bins = array.array("d", np.linspace(0, 1, 10))
        # b_bins = array.array("d", np.concatenate([
        #                           np.arange(0.00, 0.10, 0.01),
        #                           np.arange(0.10, 0.20, 0.01),
        #                           np.arange(0.20, 1.05, 0.05)
        #                         ])
        #                     )
    else:
        b_bins = array.array("d", b_bins)

    pt_cuts = parse_pt_cuts(pt_cuts)

    def colors_func(n):
        base = [
            ROOT.kViolet - 6,
            ROOT.kBlue + 1,
            ROOT.kGreen + 2,
            ROOT.kMagenta + 1,
            ROOT.kOrange + 7,
            ROOT.kCyan + 1,
            ROOT.kViolet + 1,
            ROOT.kAzure + 1,
            ROOT.kPink + 7,
            ROOT.kTeal + 3,
            ROOT.kSpring + 5,
            ROOT.kYellow + 2,
            ROOT.kGray + 2,
            ROOT.kBlack,
            ROOT.kRed,
            ROOT.kOrange - 3,
            ROOT.kGreen - 3,
            ROOT.kMagenta - 3,
            ROOT.kCyan - 3,
            ROOT.kViolet - 3,
            ROOT.kAzure - 3,
            ROOT.kPink - 3,

        ]
        return [base[i % len(base)] for i in range(n)]

    colours = [
        ROOT.kViolet - 6,
        ROOT.kBlue + 1,
        ROOT.kGreen + 2,
        ROOT.kMagenta + 1,
        ROOT.kOrange + 7,
        ROOT.kCyan + 1,
        ROOT.kAzure + 1,
        ROOT.kPink + 7,
        ROOT.kTeal + 3,
        ROOT.kSpring + 5,
        ROOT.kYellow + 2,
        ROOT.kGray + 2,
        ROOT.kBlack,
        ROOT.kRed,
        ROOT.kOrange - 3,
        ROOT.kGreen - 3,
        ROOT.kMagenta - 3,
        ROOT.kCyan - 3,
        ROOT.kViolet - 3,
        ROOT.kAzure - 3,
        ROOT.kPink - 3,
        ]
    

    sigma0 = 70  # mb
    
    for var in variables:
        if var in ["PFCands_pt", "PFCands_eta", "PFCands_phi", "PFCands_pvAssocQuality"]:
            continue

        label = VARIABLES[var]
        binning = BINNING[var]
        y_title = "DY/MinBias relative to (DY/MinBias)_{Z}"

        q_column = f"{var}_InvQ"
        plot_xlabel = f"impact parameter b"
        b_column = f"{var}_b"

        dummy = ROOT.TObject()


        canvas = ROOT.TCanvas(f"c_quantile_ptscan_{var}", "", 1500, 1400)
        canvas.cd()
        canvas.SetBottomMargin(0.1)
        canvas.SetRightMargin(0.05)
        canvas.SetLeftMargin(0.1)
        canvas.SetTopMargin(0.05)

        legend = ROOT.TLegend(0.35, 0.65, 0.55, 0.95)
        legend.SetTextSize(0.02)
        legend.SetBorderSize(0)
        legend.SetFillStyle(0)
        
        legend_var = ROOT.TLegend(0.15, 0.85, 0.55, 0.95)
        legend_var.SetTextSize(0.02)
        legend_var.SetBorderSize(0)
        legend_var.SetFillStyle(0)
        legend_var.AddEntry(dummy, f"#bf{{{label}}}", "")

        legend_DataStyle = ROOT.TLine(0.0, 0.0, 0.5, 0.0)
        legend_DataStyle.SetLineColor(ROOT.kBlack)
        legend_DataStyle.SetLineWidth(2)
        legend_DataStyle.SetLineStyle(1)

        legend_MCStyle = ROOT.TLine(0.0, 0.0, 0.5, 0.0)
        legend_MCStyle.SetLineColor(ROOT.kBlack)
        legend_MCStyle.SetLineWidth(2)
        legend_MCStyle.SetLineStyle(2)

        legend.AddEntry(legend_DataStyle, "#bf{Data}", "l")
        legend.AddEntry(legend_MCStyle, "#bf{MC}", "l")



        BuildQuantile(df_MinBias_var, var, "MB")
        BuildQuantile(df_MCMinBias_var, var, "MCMB")

        df_MinBias_q = ApplyQuantileAndIP(df_MinBias_var, var, "MB")
        df_MCMinBias_q = ApplyQuantileAndIP(df_MCMinBias_var, var, "MCMB")

        h_MinBias_ptr = df_MinBias_q.Histo1D((f"h_MinBias_{var}_quantile", f"; {plot_xlabel}; {y_title}", len(b_bins) - 1, b_bins), b_column)
        h_MCMinBias_ptr = df_MCMinBias_q.Histo1D((f"h_MCMinBias_{var}_quantile", f"; {plot_xlabel}; {y_title}", len(b_bins) - 1, b_bins), b_column)

        h_MinBias = h_MinBias_ptr.GetValue()
        h_MCMinBias = h_MCMinBias_ptr.GetValue()

        NormaliseHist(h_MinBias, binweight)
        NormaliseHist(h_MCMinBias, binweight)




        df_SingleMuon_Z = df_SingleMuon_var.Filter("DiMuon_Mass >= 86 && DiMuon_Mass < 96")
        df_MCDYJets_Z = df_MCDYJets_var.Filter("DiMuon_Mass >= 86 && DiMuon_Mass < 96")

        df_SingleMuon_Z = DiMuonPtCut(df_SingleMuon_Z, 4)
        df_MCDYJets_Z = DiMuonPtCut(df_MCDYJets_Z, 4)

        df_SingleMuon_Z = ApplyQuantileAndIP(df_SingleMuon_Z, var, "MB")
        df_MCDYJets_Z = ApplyQuantileAndIP(df_MCDYJets_Z, var, "MCMB")

        h_Z_ptr = df_SingleMuon_Z.Histo1D(
            (
                f"h_Z_{var}",
                f"; {plot_xlabel}; {y_title}",
                len(b_bins) - 1,
                b_bins
            ),
            b_column
        )

        h_MCZ_ptr = df_MCDYJets_Z.Histo1D(
            (
                f"h_MCZ_{var}",
                f"; {plot_xlabel}; {y_title}",
                len(b_bins) - 1,
                b_bins
            ),
            b_column
        )

        h_Z = h_Z_ptr.GetValue()
        h_MCZ = h_MCZ_ptr.GetValue()

        NormaliseHist(h_Z, binweight)
        NormaliseHist(h_MCZ, binweight)

        ratio_Z_Data = h_Z.Clone(f"ratio_Z_Data_{var}")
        ratio_Z_Data.Divide(h_MinBias)

        ratio_Z_MC = h_MCZ.Clone(f"ratio_Z_MC_{var}")
        ratio_Z_MC.Divide(h_MCMinBias)

        x_values = []

        sigma_eff_data_values = []
        sigma_eff_mc_values = []
        sigma_eff_data_errors = []
        sigma_eff_mc_errors = []
        # inv_mass = [(0, 15), (15, 20), (20, 30), (30, 40), (40, 50), (50, 60), (60, 70), (70, 86), (86, 96), (96, 100), (100, 110), (110, 120), (120, 130), (130, 140), (140, 150)]
        # inv_mass = [(0, 10), (10, 20), (20, 30), (30, 40), (40, 50), (50, 60), (60, 70), (70, 80), (80, 90), (90, 100), (100, 110), (110, 120), (120, 130), (130, 140), (140, 150)]
        inv_mass = [(86, 96), 
                    # (0, 10),
                    # # (10, 20), 
                    # # (20, 30), 
                    # # (30, 40), 
                    # # (40, 50), 
                    # (50, 60), 
                    # (60, 70), 
                    # (70, 86), 
                    # (96, 100), 
                    # (100, 110), 
                    # (110, 120), 
                    # (120, 130), 
                    # (130, 140), 
                    # (140, 150)
                    (0, 30),
                    (30, 70),
                    (70, 86),
                    (96, 110),
                    (110, 130),
                    (130, 150)
                    ]
        rapidity = [(-2.4, -2), (-2, -1), (-1, -0.5), (-0.5, 0), (0, 0.5), (0.5, 1), (1, 2), (2, 2.4)]

        ratios_Data = []
        ratios_MC = []
        ratios_toZ_Data = []
        ratios_toZ_MC = []


        

        

        for index, pt_cut in enumerate(pt_cuts):
        
            canvas.cd()          

            print(f"\n\nProcessing DiMuon pT cut: {pt_cut} GeV...\n")


            if pt_cut is None or len(pt_cuts) == 0:
                print(f"\n\nNo DiMuon pT cut specified for quantile plot.\n")

                df_SingleMuon_q = df_SingleMuon_var
                df_MCDYJets_q = df_MCDYJets_var

            else:
                pt_cut = int(pt_cut)
                print(f"\n\nApplying DiMuon pT cuts for quantile plot: {pt_cut} GeV...\n")

                df_SingleMuon_q = DiMuonPtCut(df_SingleMuon_var, pt_cut)
                df_MCDYJets_q = DiMuonPtCut(df_MCDYJets_var, pt_cut)
                
    
            df_SingleMuon_q = ApplyQuantileAndIP(df_SingleMuon_q, var, "MB")
            df_MCDYJets_q = ApplyQuantileAndIP(df_MCDYJets_q, var, "MCMB")

            
            for idx, mass_rap in enumerate(inv_mass) if mass_rapidity == "mass" else enumerate(rapidity):

                print(f"\n\nProcessing DiMuon {mass_rap} range:...\n")

                if mass_rapidity == "mass":
                    mass = mass_rap

                    print(f"{mass[0]} - {mass[1]} GeV...\n")
        
                    df_SingleMuon_massrap = df_SingleMuon_q.Filter(f"DiMuon_Mass >= {mass[0]} && DiMuon_Mass < {mass[1]}")
                    df_MCDYJets_massrap = df_MCDYJets_q.Filter(f"DiMuon_Mass >= {mass[0]} && DiMuon_Mass < {mass[1]}")


                elif mass_rapidity == "rapidity":
                    rapidity = mass_rap
                    
                    print(f"{rapidity[0]} - {rapidity[1]}...\n")
        
                    df_SingleMuon_massrap = df_SingleMuon_q.Filter(f"DiMuon_Rapidity >= {rapidity[0]} && DiMuon_Rapidity < {rapidity[1]}")
                    df_MCDYJets_massrap = df_MCDYJets_q.Filter(f"DiMuon_Rapidity >= {rapidity[0]} && DiMuon_Rapidity < {rapidity[1]}")
                
                colour = colours[idx]

        


                if mass_rapidity == "mass":                
                    h_SingleMuon_ptr = df_SingleMuon_massrap.Histo1D((f"h_SingleMuon_{var}_{mass[0]}_{mass[1]}_{pt_cut}", f"; {plot_xlabel}; {y_title}", len(b_bins) - 1, b_bins), b_column)
                    h_MCDYJets_ptr = df_MCDYJets_massrap.Histo1D((f"h_MCDYJets_{var}_{mass[0]}_{mass[1]}_{pt_cut}", f"; {plot_xlabel}; {y_title}", len(b_bins) - 1, b_bins), b_column)
                else:
                    h_SingleMuon_ptr = df_SingleMuon_massrap.Histo1D((f"h_SingleMuon_{var}_{rapidity[0]}_{rapidity[1]}_{pt_cut}", f"; {plot_xlabel}; {y_title}", len(b_bins) - 1, b_bins), b_column)
                    h_MCDYJets_ptr = df_MCDYJets_massrap.Histo1D((f"h_MCDYJets_{var}_{rapidity[0]}_{rapidity[1]}_{pt_cut}", f"; {plot_xlabel}; {y_title}", len(b_bins) - 1, b_bins), b_column)

                h_SingleMuon = h_SingleMuon_ptr.GetValue()
                h_MCDYJets = h_MCDYJets_ptr.GetValue()

                NormaliseHist(h_SingleMuon, binweight)
                NormaliseHist(h_MCDYJets, binweight)


                ratio_Data = h_SingleMuon.Clone(f"ratio_sigmaeff_ptscan_data_{var}_pt{pt_cut}")
                ratio_Data.Divide(h_MinBias)
                ratios_Data.append(ratio_Data)
                
                ratio_MC = h_MCDYJets.Clone(f"ratio_sigmaeff_ptscan_mc_{var}_pt{pt_cut}")
                ratio_MC.Divide(h_MCMinBias)
                ratios_MC.append(ratio_MC)


                ratio_toZ_Data = ratio_Data.Clone(f"ratio_toZ_sigmaeff_ptscan_data_{var}_pt{pt_cut}")
                ratio_toZ_MC = ratio_MC.Clone(f"ratio_toZ_sigmaeff_ptscan_mc_{var}_pt{pt_cut}")
                ratio_toZ_Data.Divide(ratio_Z_Data)
                ratio_toZ_MC.Divide(ratio_Z_MC)

                ratio_toZ_Data.SetLineColor(colour)
                ratio_toZ_Data.SetLineWidth(2)
                ratio_toZ_Data.SetMarkerColor(colour)
                ratio_toZ_Data.GetXaxis().SetTitle(plot_xlabel)
                ratio_toZ_Data.GetYaxis().SetTitle(y_title)
                ratios_toZ_Data.append(ratio_toZ_Data)

                ratio_toZ_MC.SetLineColor(colour)
                ratio_toZ_MC.SetLineWidth(2)
                ratio_toZ_MC.SetLineStyle(2)
                ratio_toZ_MC.SetMarkerColor(colour)
                ratios_toZ_MC.append(ratio_toZ_MC)

                if idx == 0:
                    ratio_toZ_Data.Draw("hist")
                else:
                    ratio_toZ_Data.Draw("hist same")
                ratio_toZ_MC.Draw("hist same")



                if mass_rapidity == "mass":
                    legend.AddEntry(dummy, f"#color[{colour}]{{{mass[0]} GeV #leq m_{{#mu#mu}} < {mass[1]} GeV}}", "")
                else:
                    legend.AddEntry(dummy, f"#color[{colour}]{{{rapidity[0]} #leq y_{{#mu#mu}} < {rapidity[1]}}}", "")

            legend_var.AddEntry(dummy, f"p^{{#mu#mu}}_{{T}} < {pt_cut} GeV", "")
            
            ratios_toZ_Data[0].SetMaximum(max(hist.GetMaximum() for hist in ratios_toZ_Data + ratios_toZ_MC if hist.GetMaximum() > 0) * 1.1)
            ratios_toZ_Data[0].SetMinimum(min(hist.GetMinimum() for hist in ratios_toZ_Data + ratios_toZ_MC if hist.GetMinimum() != 0) * 0.9)

            

        legend.Draw()
        legend_var.Draw()

        output_dir = f"new_plots/sigma_eff"
        os.makedirs(output_dir, exist_ok=True)

        if mass_rapidity == "mass":
            output_name = f"{output_dir}/{var}_EnhFactorRatioToZ_MassBins_{out_suffix}.pdf"
        else:
            output_name = f"{output_dir}/{var}_EnhFactorRatioToZ_RapidityBins_{out_suffix}.pdf"
        
        canvas.SaveAs(output_name)

        canvas.Close()


def MassRapPt3D(df_SingleMuon_var, df_MinBias_var, df_MCDYJets_var, df_MCMinBias_var, variables, out_suffix, bins, b_bins, binweight, axes):

    sigma0 = 70  # mb
    if len(axes) != 2:
        raise ValueError("The 'axes' argument must contain exactly two elements, e.g., ['mass', 'pt'], ['absrapidity', 'pt'].")

    # Apply di-muon pT cut of 4 GeV for the 3D plot if pt is not specified
    if "pt" not in axes:
        df_SingleMuon_var = DiMuonPtCut(df_SingleMuon_var, 4)
        df_MCDYJets_var = DiMuonPtCut(df_MCDYJets_var, 4)

    quantile_bins = array.array("d", bins)

    if b_bins is None:
        b_bins = array.array("d", np.linspace(0, 1, 20))
        # b_bins = array.array("d", np.concatenate([
        #                           np.arange(0.00, 0.10, 0.01),
        #                           np.arange(0.10, 0.20, 0.01),
        #                           np.arange(0.20, 1.05, 0.05)
        #                         ])
        #                     )
    else:
        b_bins = array.array("d", b_bins)

    # pt_cuts = parse_pt_cuts(pt_cuts)
    # inv_mass = [(0, 15), (15, 20), (20, 30), (30, 40), (40, 50), (50, 60), (60, 70), (70, 86), (86, 96), (96, 100), (100, 110), (110, 120), (120, 130), (130, 140), (140, 150)]
    # inv_mass = [(0, 10), (10, 20), (20, 30), (30, 40), (40, 50), (50, 60), (60, 70), (70, 80), (80, 90), (90, 100), (100, 110), (110, 120), (120, 130), (130, 140), (140, 150)]
    inv_mass = [
                # (0, 10),
                # (10, 20), 
                # (20, 30), 
                # (30, 40), 
                # (40, 50), 
                # (50, 60), 
                # (60, 70), 
                # (70, 86),
                # (86, 96),
                # (96, 100), 
                # (100, 110), 
                # (110, 120), 
                # (120, 130), 
                # (130, 140), 
                # (140, 150)
                # (0, 50),
                (50, 70),
                (70, 86),
                (86, 96),
                (96, 110),
                (110, 130),
                (130, 150)
                ]
    pt_cuts = [
                (0, 1),
                (1, 2), 
                (2, 3), 
                (3, 4),
                (4, 5), 
                (5, 6), 
                (6, 7), 
                (7, 8), 
                (8, 9), 
                (9, 10), 
                # (10, 11), 
                # (11, 12), 
                # (12, 13), 
                # (13, 14), 
                # (14, 15), 
                # (15, 16), 
                # (16, 17), 
                # (17, 18), 
                # (18, 19), 
                # (19, 20)
                ]
    rapidity = [
                (-2.4, -2),
                (-2, -1),
                (-1, -0.5),
                (-0.5, 0),
                (0, 0.5),
                (0.5, 1),
                (1, 2),
                (2, 2.4)
                ]

    absrapidity = [
                (0, 0.5),
                (0.5, 1),
                (1, 1.5),
                (1.5, 2),
                (2, 2.4)
                ]


    
    colours = [
            ROOT.kBlue + 1,
            ROOT.kGreen + 2,
            ROOT.kMagenta + 1,
            ROOT.kOrange + 7,
            ROOT.kCyan + 1,
            ROOT.kViolet + 1,
            ROOT.kAzure + 1,
            ROOT.kPink + 7,
            ROOT.kTeal + 3,
            ROOT.kSpring + 5,
            ROOT.kYellow + 2,
            ROOT.kGray + 2,
            ROOT.kBlack,
            ROOT.kRed,
            ROOT.kOrange - 3,
            ROOT.kGreen - 3,
            ROOT.kMagenta - 3,
            ROOT.kCyan - 3,
            ROOT.kViolet - 3,
            ROOT.kAzure - 3,
            ROOT.kPink - 3,
        ]

    inv_mass_centers = [0.5 * (a + b) for a, b in inv_mass]
    pt_centers = [0.5 * (a + b) for a, b in pt_cuts]
    rapidity_centers = [0.5 * (a + b) for a, b in rapidity]
    absrapidity_centers = [0.5 * (a + b) for a, b in absrapidity]

    mass_edges = sorted(set(edge for bin_range in inv_mass for edge in bin_range))
    pt_edges = sorted(set(edge for bin_range in pt_cuts for edge in bin_range))
    rapidity_edges = sorted(set(edge for bin_range in rapidity for edge in bin_range))
    absrapidity_edges = sorted(set(edge for bin_range in absrapidity for edge in bin_range))

    mass_edges_arr = np.array(sorted(set(e for b in inv_mass for e in b)))
    pt_edges_arr = np.array(sorted(set(e for b in pt_cuts for e in b)))
    rapidity_edges_arr = np.array(sorted(set(e for b in rapidity for e in b)))
    absrapidity_edges_arr = np.array(sorted(set(e for b in absrapidity for e in b)))

    BIN_DEFS = {
                    "mass": inv_mass,
                    "pt": pt_cuts,
                    "rapidity": rapidity,
                    "absrapidity": absrapidity,
                }
    FILTER_COL = {
                    "mass": "DiMuon_Mass",
                    "pt": "DiMuon_Pt",
                    "rapidity": "DiMuon_Rapidity",
                    "absrapidity": "abs(DiMuon_Rapidity)",
                }

    AXIS_INFO = {
                    "mass": {
                        "label": r"$m_{\mu\mu}\,\mathrm{[GeV]}$",
                        "edges": mass_edges,
                        "edges_arr": mass_edges_arr,
                    },
                    "pt": {
                        "label": r"$p^{\mu\mu}_{T}\,\mathrm{[GeV]}$",
                        "edges": pt_edges,
                        "edges_arr": pt_edges_arr,
                    },
                    "rapidity": {
                        "label": r"$y_{\mu\mu}$",
                        "edges": rapidity_edges,
                        "edges_arr": np.array(rapidity_edges),
                    },
                    "absrapidity": {
                        "label": r"$|y_{\mu\mu}|$",
                        "edges": absrapidity_edges,
                        "edges_arr": absrapidity_edges_arr,
                    }
                }

    x_axis_name, y_axis_name = axes
    x_bins = BIN_DEFS[x_axis_name]
    y_bins = BIN_DEFS[y_axis_name]

    x_info = AXIS_INFO[x_axis_name]
    y_info = AXIS_INFO[y_axis_name]

    def sigma_eff_error(width_list, E_list, Eerror_list):
                """
                Gaussian error propagation for

                    sigma_eff = sum(width_i * E_i) / sum(width_i * E_i^2)

                assuming only E_i has an uncertainty and the E_i uncertainties are statistically independent.
                """

                normalization = sum(width * E for width, E in zip(width_list, E_list))

                integral = sum(width * E**2 for width, E in zip(width_list, E_list))

                if integral == 0:
                    return 0

                sigma_eff = normalization / integral

                error_squared = 0.0

                for width, E, Eerror in zip(width_list, E_list, Eerror_list):

                    derivative = (width * (1 - 2 * E * sigma_eff)/integral)

                    error_squared += (derivative * Eerror)**2

                return np.sqrt(error_squared)

    
    for var in variables:
        if var in ["PFCands_pt", "PFCands_eta", "PFCands_phi", "PFCands_pvAssocQuality"]:
            continue

        label = VARIABLES[var]
        binning = BINNING[var]
        y_title = "#sigma_{eff}"

        q_column = f"{var}_InvQ"
        plot_xlabel = f"impact parameter b"
        b_column = f"{var}_b"

        BuildQuantile(df_MinBias_var, var, "MB")
        BuildQuantile(df_MCMinBias_var, var, "MCMB")

        df_MinBias_q = ApplyQuantileAndIP(df_MinBias_var, var, "MB")
        df_MCMinBias_q = ApplyQuantileAndIP(df_MCMinBias_var, var, "MCMB")

        h_MinBias_ptr = df_MinBias_q.Histo1D((f"h_MinBias_{var}_quantile", f"; {plot_xlabel}; {y_title}", len(b_bins) - 1, b_bins), b_column)
        h_MCMinBias_ptr = df_MCMinBias_q.Histo1D((f"h_MCMinBias_{var}_quantile", f"; {plot_xlabel}; {y_title}", len(b_bins) - 1, b_bins), b_column)

        h_MinBias = h_MinBias_ptr.GetValue()
        h_MCMinBias = h_MCMinBias_ptr.GetValue()

        NormaliseHist(h_MinBias, binweight)
        NormaliseHist(h_MCMinBias, binweight)



        ratios_Data = []
        ratios_MC = []

        sigma_eff_data_values = []
        sigma_eff_mc_values = []
        sigma_eff_data_errors = []
        sigma_eff_mc_errors = []

        integrals_Data = []
        integrals_MC = []

        counts_Data = []
        counts_MC = []


        for y_low, y_high in y_bins:
            print(f"\n\nProcessing {y_axis_name} range: {y_low}-{y_high}...\n")

            df_SingleMuon_y = df_SingleMuon_var.Filter(
                f"{FILTER_COL[y_axis_name]} >= {y_low} && {FILTER_COL[y_axis_name]} < {y_high}"
            )
            df_MCDYJets_y = df_MCDYJets_var.Filter(
                f"{FILTER_COL[y_axis_name]} >= {y_low} && {FILTER_COL[y_axis_name]} < {y_high}"
            )

            for x_low, x_high in x_bins:
                print(f"Processing {y_axis_name} {y_low}-{y_high}, {x_axis_name} {x_low}-{x_high}...\n")

                df_SingleMuon_xy = df_SingleMuon_y.Filter(
                    f"{FILTER_COL[x_axis_name]} >= {x_low} && {FILTER_COL[x_axis_name]} < {x_high}"
                )
                df_MCDYJets_xy = df_MCDYJets_y.Filter(
                    f"{FILTER_COL[x_axis_name]} >= {x_low} && {FILTER_COL[x_axis_name]} < {x_high}"
                )

                count_Data = df_SingleMuon_xy.Count().GetValue()
                count_MC   = df_MCDYJets_xy.Count().GetValue()
                
                counts_Data.append((y_low, y_high, x_low, x_high, count_Data))
                counts_MC.append((y_low, y_high, x_low, x_high, count_MC))

                df_SingleMuon_xy = ApplyQuantileAndIP(df_SingleMuon_xy, var, "MB")
                df_MCDYJets_xy = ApplyQuantileAndIP(df_MCDYJets_xy, var, "MCMB")

                tag = f"{y_axis_name}{y_low}-{y_high}_{x_axis_name}{x_low}-{x_high}"

                h_SingleMuon_ptr = df_SingleMuon_xy.Histo1D((f"h_SingleMuon_{var}_{tag}", "; impact parameter b; #sigma_{eff}", len(b_bins) - 1, b_bins), b_column)
                h_MCDYJets_ptr = df_MCDYJets_xy.Histo1D((f"h_MCDYJets_{var}_{tag}", "; impact parameter b; #sigma_{eff}", len(b_bins) - 1, b_bins), b_column)

                h_SingleMuon = h_SingleMuon_ptr.GetValue()
                h_MCDYJets = h_MCDYJets_ptr.GetValue()

                NormaliseHist(h_SingleMuon, binweight)
                NormaliseHist(h_MCDYJets, binweight)


                ratio_Data = h_SingleMuon.Clone(f"ratio_data_{tag}")
                ratio_Data.Divide(h_MinBias)
                ratios_Data.append(ratio_Data)

                ratio_MC = h_MCDYJets.Clone(f"ratio_mc_{tag}")
                ratio_MC.Divide(h_MCMinBias)
                ratios_MC.append(ratio_MC)

                # Extract total normalized counts (integral of normalized histogram)
                # integral_Data = ratio_Data.Integral()
                # integral_MC = ratio_MC.Integral()

                # integrals_Data.append((y_low, y_high, x_low, x_high, integral_Data))
                # integrals_MC.append((y_low, y_high, x_low, x_high, integral_MC))

                width_list, E_Data_list, E_MC_list = [], [], []
                EError_Data_list, EError_MC_list = [], []
                normalization_Data = normalization_MC = 0.0
                integral_Data = integral_MC = 0.0


                for i in range(1, ratio_Data.GetNbinsX() + 1):

                    b_low = ratio_Data.GetBinLowEdge(i)
                    b_high = ratio_Data.GetBinLowEdge(i) + ratio_Data.GetBinWidth(i)

                    # Calculate the width each bin
                    width = np.pi * (b_high**2 - b_low**2)
                    width_list.append(width)

                    # Enhancement factor (i.e. DY/MinBias) in each bin of the ratio histogram 
                    E_Data = ratio_Data.GetBinContent(i)
                    E_MC = ratio_MC.GetBinContent(i)
                    EError_Data = ratio_Data.GetBinError(i)
                    EError_MC = ratio_MC.GetBinError(i)
                    E_Data_list.append(E_Data)
                    E_MC_list.append(E_MC)
                    EError_Data_list.append(EError_Data)
                    EError_MC_list.append(EError_MC)

                    # Calculate the normalization and integral for Data and MC
                    normalization_Data += width * E_Data
                    normalization_MC += width * E_MC

                    integral_Data += width * E_Data**2
                    integral_MC += width * E_MC**2


                sigma_eff_Data = (normalization_Data / integral_Data if integral_Data != 0 else 0)
                sigma_eff_MC = (normalization_MC / integral_MC if integral_MC != 0 else 0)

                sigma_eff_error_Data = sigma_eff_error(width_list, E_Data_list, EError_Data_list)
                sigma_eff_error_MC = sigma_eff_error(width_list, E_MC_list, EError_MC_list)
                

                sigma_eff_data_values.append((y_low, y_high, x_low, x_high, sigma_eff_Data))
                sigma_eff_mc_values.append((y_low, y_high, x_low, x_high, sigma_eff_MC))

                

        nData = np.array(counts_Data)[:, 4].reshape(len(y_bins), len(x_bins))
        nMC = np.array(counts_MC)[:, 4].reshape(len(y_bins), len(x_bins))

        
        
                
        print(f"Sigma_eff values for Data: {sigma_eff_data_values}")
        print(f"Sigma_eff values for MC: {sigma_eff_mc_values}")

        # print(f"Sigma_eff values for Data: {integrals_Data}")
        # print(f"Sigma_eff values for MC: {integrals_MC}")          
    


        data = np.array(sigma_eff_data_values)[:, 4].reshape(len(y_bins), len(x_bins))
        mc = np.array(sigma_eff_mc_values)[:, 4].reshape(len(y_bins), len(x_bins))
        # data = np.array(integrals_Data)[:, 4].reshape(len(y_bins), len(x_bins))
        # mc = np.array(integrals_MC)[:, 4].reshape(len(y_bins), len(x_bins))

        x_centers = [0.5 * (lo + hi) for lo, hi in x_bins]
        y_centers = [0.5 * (lo + hi) for lo, hi in y_bins]

        fig, (ax, ax_mc) = plt.subplots(1, 2, figsize=(14, 6))

        # --- Data (left) ---
        mesh = ax.pcolormesh(x_info["edges_arr"], y_info["edges_arr"], data, cmap='viridis')
        ax.set_title("Data", fontsize=14, fontweight='bold')
        cbar = fig.colorbar(mesh, ax=ax)
        cbar.set_label(r"$\sigma_\mathrm{eff} / \sigma_\mathrm{0}$", fontsize=12)
        # cbar.set_label(r"Event Density $\frac{1}{N} \frac{dN}{db}$", fontsize=12)
        ax.set_xlabel(x_info["label"], fontsize=12)
        ax.set_ylabel(y_info["label"], fontsize=12)
        ax.set_xticks(x_info["edges"])
        ax.set_yticks(y_info["edges"])

        threshold = (data.max() + data.min()) / 2.0
        for i, y_c in enumerate(y_centers):
            for j, x_c in enumerate(x_centers):
                value = data[i, j]
                color = "white" if value < threshold else "black"
                # if value == 0:
                # ax.text(x_c, y_c, f"{value:.2f}", ha="center", va="center", color=color, fontsize=9)
                ax.text(x_c, y_c, f"{value:.2f}\nN={int(nData[i, j])}", ha="center", va="center", color=color, fontsize=8)

        # --- MC (right) ---
        mesh_mc = ax_mc.pcolormesh(x_info["edges_arr"], y_info["edges_arr"], mc, cmap='viridis')
        ax_mc.set_title("MC", fontsize=14, fontweight='bold')
        cbar_mc = fig.colorbar(mesh_mc, ax=ax_mc)
        cbar_mc.set_label(r"$\sigma_\mathrm{eff} / \sigma_\mathrm{0}$", fontsize=12)
        # cbar_mc.set_label(r"Event Density $\frac{1}{N} \frac{dN}{db}$", fontsize=12)
        ax_mc.set_xlabel(x_info["label"], fontsize=12)
        ax_mc.set_ylabel(y_info["label"], fontsize=12)
        ax_mc.set_xticks(x_info["edges"])
        ax_mc.set_yticks(y_info["edges"])

        threshold_mc = (mc.max() + mc.min()) / 2.0
        for i, y_c in enumerate(y_centers):
            for j, x_c in enumerate(x_centers):
                value = mc[i, j]
                color = "white" if value < threshold_mc else "black"
                # if value == 0:
                # ax_mc.text(x_c, y_c, f"{value:.2f}", ha="center", va="center", color=color, fontsize=9)
                ax_mc.text(x_c, y_c, f"{value:.2f}\nN={int(nMC[i, j])}", ha="center", va="center", color=color, fontsize=8)


        fig.suptitle(f"Event Activity Observable used here: {VARIABLESFORPYTHON[var]}", fontsize=14, fontweight='bold', y=0.96)
        fig.tight_layout()

        output = f"new_plots/sigma_eff/{var}_PtMassRapidity3DSigmaEff_{x_axis_name.capitalize()}{y_axis_name.capitalize()}{out_suffix}.pdf"
        # output = f"new_plots/sigma_eff/{var}_PtMassRapidity3DEventDensity_{x_axis_name.capitalize()}{y_axis_name.capitalize()}{out_suffix}.pdf"
        plt.savefig(output)
        plt.show()
        print(f"\n\nPlotted: {output}!\n\n")



# def PocketFormulaRatio(df_SingleMuon_var, df_MCDYJets_var, df_NoMPI_var, cz_cuts, out_suffix, jet_pt_col="Jet_pt", jet_eta_col="Jet_eta"):
#     """
#     r_{x/2} ratio of arXiv:2307.05693, Eq. (6):

#         r_{loose/tight}(ptj,min) = <n(ptj,min)>^{pure-MPI}_{loose} / <n(ptj,min)>^{pure-MPI}_{tight}

#     <n(ptj,min)>_{C_Z} is the average number of jets with p_T > ptj,min per event with p^{mumu}_T < C_Z (Eq. 2).
#     The pure-MPI part is <n>_{C_Z} minus <n>_{C_Z} of a DY sample without MPI (Eq. 3), subtracted from both
#     Data and MC as in Eq. (A16). Without a no-MPI sample the inclusive ratio is plotted instead.
#     The pocket formula predicts r = 1.
#     """

#     cz_tight, cz_loose = sorted(cz_cuts)
#     mass_window = (66, 116)
#     jet_eta_max = 2.0                        # paper uses |y_j| < 2
#     ptj_min_values = list(range(20, 62, 2))  # NanoAOD jets are only stored above 15 GeV

#     colour_tight = "#7B2D8B"
#     colour_loose = "#C84B00"
#     LINESTYLE = {"DY": "-", "MC DY": "--", "MC DY (no MPI)": ":"}

#     datasets = [("DY", df_SingleMuon_var), ("MC DY", df_MCDYJets_var)]
#     if df_NoMPI_var is not None:
#         datasets.append(("MC DY (no MPI)", df_NoMPI_var))
#     else:
#         print("WARNING: no no-MPI sample given (--nompi-file), plotting the inclusive ratio without the pure-MPI subtraction.")

#     for name, df in datasets:
#         if jet_pt_col not in list(df.GetColumnNames()):
#             print(f"Warning: column '{jet_pt_col}' not found in {name} DataFrame, skipping PocketFormulaRatio.")
#             return

#     # Build all result pointers for all datasets × C_Z cuts × ptj,min thresholds
#     stats_ptrs = {}   # {(name, cz): [ResultPtr, ...]}
#     for name, df in datasets:
#         df = df.Filter(f"DiMuon_Mass > {mass_window[0]} && DiMuon_Mass < {mass_window[1]}")
#         for ptj_min in ptj_min_values:
#             df = df.Define(f"nJets_ptjmin{ptj_min}", f"Sum({jet_pt_col} > {ptj_min} && abs({jet_eta_col}) < {jet_eta_max})")

#         for cz in (cz_tight, cz_loose):
#             df_cz = DiMuonPtCut(df, cz)
#             stats_ptrs[(name, cz)] = [df_cz.Stats(f"nJets_ptjmin{ptj_min}") for ptj_min in ptj_min_values]

#     # Single RunGraphs call — one event loop per df
#     all_ptrs = [p for ptrs in stats_ptrs.values() for p in ptrs]
#     ROOT.RDF.RunGraphs(all_ptrs)

#     # <n(ptj,min)>_{C_Z} and its statistical error for every (name, cz)
#     n_jets = {}
#     for (name, cz), ptrs in stats_ptrs.items():
#         stats = [ptr.GetValue() for ptr in ptrs]
#         n_jets[(name, cz)] = (np.array([s.GetMean() for s in stats]), np.array([s.GetMeanErr() for s in stats]))
#         print(f"{name}: {stats[0].GetN()} events with p_T^mumu < {cz:g} GeV")

#     def pure_mpi(name, cz):
#         mean, err = n_jets[(name, cz)]
#         if df_NoMPI_var is None:
#             return mean, err
#         mean_noMPI, err_noMPI = n_jets[("MC DY (no MPI)", cz)]
#         return mean - mean_noMPI, np.sqrt(err**2 + err_noMPI**2)

#     def ratio(name):
#         num, num_err = pure_mpi(name, cz_loose)
#         den, den_err = pure_mpi(name, cz_tight)
#         den = np.where(den != 0, den, np.nan)
#         # Errors treated as uncorrelated (conservative: the tight selection is a subset of the loose one)
#         r = num / den
#         r_err = np.sqrt((num_err / den)**2 + (num * den_err / den**2)**2)
#         return r, r_err

#     fig, (ax_n, ax_r) = plt.subplots(2, 1, figsize=(9, 7), sharex=True, gridspec_kw={"height_ratios": [2, 1], "hspace": 0.05})

#     # Top: <n(ptj,min)>_{C_Z} for both C_Z cuts
#     for cz, colour in ((cz_tight, colour_tight), (cz_loose, colour_loose)):
#         for name, _ in datasets:
#             mean, err = n_jets[(name, cz)]
#             ax_n.errorbar(ptj_min_values, mean, yerr=err, color=colour, linestyle=LINESTYLE[name], marker="o", linewidth=1.8, markersize=4, label=f"{name}, $p^{{\\mu\\mu}}_T < {cz:g}$ GeV")

#     ax_n.set_yscale("log")
#     ax_n.set_ylabel(r"$\langle n(p_{T,j}^{\mathrm{min}}) \rangle_{C_Z}$", fontsize=13)
#     ax_n.legend(frameon=False, fontsize=10, ncol=2, loc="lower left")
#     ax_n.text(0.98, 0.95, f"AK4 jets, $|\\eta_j| < {jet_eta_max:g}$\n${mass_window[0]} < m_{{\\mu\\mu}} < {mass_window[1]}$ GeV", transform=ax_n.transAxes, fontsize=11, ha="right", va="top")

#     # Bottom: r_{loose/tight}
#     if df_NoMPI_var is not None:
#         r_label = rf"$r_{{{cz_loose:g}/{cz_tight:g}}}$"
#     else:
#         r_label = rf"$r^{{\mathrm{{incl}}}}_{{{cz_loose:g}/{cz_tight:g}}}$"

#     ax_r.axhline(1, color="black", linestyle="--", linewidth=0.8)
#     for name, colour, ls in (("DY", "black", "-"), ("MC DY", "dimgrey", "--")):
#         r, r_err = ratio(name)
#         ax_r.errorbar(ptj_min_values, r, yerr=r_err, color=colour, linestyle=ls, marker="o", linewidth=1.8, markersize=4, label=name)

#     ax_r.set_xlabel(r"$p_{T,j}^{\mathrm{min}}$ [GeV]", fontsize=13)
#     ax_r.set_ylabel(r_label, fontsize=13)
#     ax_r.set_xlim(ptj_min_values[0] - 1, ptj_min_values[-1] + 1)
#     if df_NoMPI_var is not None:
#         ax_r.set_ylim(0, 2)
#     else:
#         ax_r.set_ylim(bottom=0)
#     ax_r.legend(frameon=False, fontsize=10, ncol=2, loc="upper left")

#     output_dir = "new_plots/PocketFormulaRatio"
#     os.makedirs(output_dir, exist_ok=True)

#     tag = "PureMPI" if df_NoMPI_var is not None else "Inclusive"
#     output = f"{output_dir}/r{cz_loose:g}over{cz_tight:g}_{tag}{out_suffix}.pdf"
#     plt.savefig(output, bbox_inches='tight')
#     plt.close(fig)

#     print(f"\nSaved plot: {output}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Combined plotting driver for NanoAOD PF-candidate studies"
    )
    parser.add_argument(
        "--mode",
        choices=["compare", "compare-quantilebinning", "ptscan", "ptscan-quantilebinning", "quantile", "quantile-ptscan", "quantile-all", "DYMinBias", "quantile-all-ptscan", "quantiles", "momentumfractions", "mllyll", "sigmaeff", "enhfactorratiotoz", "massrappt", "histograms", "averageobservablesvszpt", "variancemethod", "rapidityvariancekinematics3d", "all"],
        default="all",
        help="Run compare plots, diMuon pT scan plots, quantile plots, quantile pT scan plots, all-together quantile plots, all-together quantile pT-cut plots, or all",
    )
    parser.add_argument(
        "--maxevents",
        type=int,
        default=None,
        help="If set, process only the first N Events from each dataframe",
    )
    parser.add_argument(
        "--save-event-counts",
        action="store_true",
        help="Save total and selected event counts to a 'txt' file",
    )
    parser.add_argument(
        "--no-plot",
        action="store_true",
        help="Print counts without producing plots",
    )

    parser.add_argument(
        "--pt-cuts",
        # type="*",
        nargs="+",
        default=[None],
        help="diMuon pT cuts (GeV) to scan in ptscan mode",
    )
    parser.add_argument(
        "--vars",
        nargs="+",
        default=VARIABLES.keys(),
        choices=sorted(VARIABLES.keys()),
        help="Variables to plot",
    )
    parser.add_argument(
        "--kin-filter",
        nargs="+",
        choices=["pt", "mass", "rapidity", "Ht"],
        default=[],
        help="Kinematic filter to apply to DY (two possible at the same time): 'pt', 'mass', 'rapidity'",
    )
    parser.add_argument(
        "--output-suffix",
        default="",
        help="Optional suffix appended to output plot filenames",
    )

    parser.add_argument(
        "--b-bins",
        type=float,
        nargs="+",
        default=None,
        help="Custom bin edges for impact parameter histograms",
    )
    parser.add_argument(
        "--q-bins",
        type=float,
        nargs="+",
        default=[0, 0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045, 0.05, 0.055, 0.06, 0.065, 0.07, 0.075, 0.08, 0.085, 0.09, 0.095, 0.1, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 1],
        help="Custom bin edges for quantile histograms (alternative to --quantile-bins)",
    )
    parser.add_argument(
        "--quantile-reference",
        choices=["Data", "MC", "both"],
        default="both",
        help='Use "Data" or "MC" or "both" as the reference histogram when deriving quantile bin edges in compare-quantilebinning mode',
    )
    parser.add_argument(
        "--zoomxmax",
        type=float,
        default=140,
        help='Maximum x-axis value for the zoomed-in plot in compare-quantilebinning mode',
    )
    parser.add_argument(
        "--nthreads",
        type=int,
        default=1,
        help="Number of threads for RDataFrame processing (default: 1, set >1 to enable multithreading)",
    )
    parser.add_argument(
        "--slurm",
        action="store_true",
        help="If set, adjust file paths for running on the CERN SLURM cluster",
    )
    parser.add_argument(
        "--ratio-pt-cuts",
        choices=["DataMC", "DYZeroBias"],
        default="DataMC",
        help='Which ratio to use for the pt-cut scan (default: "DataMC")',
    )
    parser.add_argument(
        "--dimuonmassbins",
        type=float,
        nargs="+",
        default=None,
        help="Cuts on the di-muon mass histograms",
    )
    parser.add_argument(
        "--nobinweight",
        dest="binweight",
        action="store_false",
        default=True,
        help="Disable bin width weighting when normalizing histograms",
    )
    parser.add_argument(
        "--dimuonmass_cut",
        type=float,
        nargs=2,
        default=[86, 96],
        help="Cuts on the di-muon mass histograms (two values: min and max; excluding the edges)",
    )
    parser.add_argument(
        "--mass-rapidity",
        choices=["mass", "rapidity"],
        default="mass",
        help='Choose whether to scan over "mass" or "rapidity" ranges for the enhancement factor ratio to Z plot',
    )
    parser.add_argument(
        "--axes",
        choices=["mass", "rapidity", "absrapidity", "pt"],
        default=["mass", "pt"],
        nargs="+",
        help='Choose which axes to use for the 3D enhancement factor plot: "mass", "rapidity", "absrapidity", or "pt"',
    )
    parser.add_argument(
        "--ratio",
        choices=["DataMC", "DYMinBias", "DYZ"],
        default="DYMinBias",
        help="Choose which ratio to use for the pt-cut scan (default: 'DYMinBias')",
    )
    parser.add_argument(
        "--axis",
        choices=["raw", "quantile", "IP"],
        default="raw",
        help="Choose which axis to use for the plot: 'raw', 'quantile', or 'IP' (default: 'raw')",
    )
    parser.add_argument(
        "--weight",
        action = "store_true",
        help = "If passed, apply weight to variance method",
    )        
    # parser.add_argument(
    #     "--cz-cuts",
    #     type=float,
    #     nargs=2,
    #     default=[2, 15],
    #     help="Tight and loose p^{mumu}_T cuts C_Z (GeV) for the r_{loose/tight} pocket-formula ratio (default: 2 15)",
    # )
    # parser.add_argument(
    #     "--nompi-file",
    #     default=None,
    #     help="DY MC file produced without MPI, used for the pure-MPI subtraction in the pocket-formula ratio",
    # )
    return parser.parse_args()
    

def main():

    start = time.time()

    args = parse_args()

    if args.nthreads > 1:
        if args.maxevents is not None:
            print("WARNING: --maxevents uses RDataFrame.Range(), which is incompatible with EnableImplicitMT.")
            print("Running single-threaded for this test job.")
        else:
            ROOT.ROOT.EnableImplicitMT(args.nthreads)
            print("Number of threads:", args.nthreads, "\n")


    pprint.pprint(vars(args))

    df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias = MakeDataframes(args.maxevents)

    # df_SingleMuon = df_SingleMuon.Filter(f"DiMuon_Mass > {args.dimuonmass_cut[0]} && DiMuon_Mass < {args.dimuonmass_cut[1]}")
    # df_MCDYJets = df_MCDYJets.Filter(f"DiMuon_Mass > {args.dimuonmass_cut[0]} && DiMuon_Mass < {args.dimuonmass_cut[1]}")

    # if args.slurm == True:
    #     totalEvents = TotalEvents()
    #     selectedEvents = SelectedEvents(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias)
    # else:
    #     totalEvents = TotalEvents_local()
    #     selectedEvents = SelectedEvents_local(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias)


    # for df in [(df_SingleMuon, "Data_DY"), (df_MinBias, "Data_MinBias"), (df_MCDYJets, "MC_DY"), (df_MCMinBias, "MC_MinBias")]:
    #     total_entries = df[0].Count().GetValue()

    #     print(f"--------{df[1]}--------")

    #     df_Less120GeV = df[0].Filter("PFSelection_PFCands_Ht <= 120").Count().GetValue()
    #     df_Greater120GeV = df[0].Filter("PFSelection_PFCands_Ht >= 120").Count().GetValue()
    #     df_120370GeV = df[0].Filter("PFSelection_PFCands_Ht >= 120", "PFSelection_PFCands_Ht <= 370").Count().GetValue()
    #     df_Greater370GeV = df[0].Filter("PFSelection_PFCands_Ht >= 370").Count().GetValue()

    #     print(f"N_Events with Ht <= 120 GeV: {df_Less120GeV} ({(df_Less120GeV / total_entries) * 100:.2f}%)")
    #     print(f"N_Events with Ht >= 120 GeV: {df_Greater120GeV} ({(df_Greater120GeV / total_entries) * 100:.2f}%)")
    #     print(f"N_Events with 120 GeV <= Ht <= 370 GeV: {df_120370GeV} ({(df_120370GeV / total_entries) * 10:.2f}%)")
    #     print(f"N_Events with Ht >= 370 GeV: {df_Greater370GeV} ({(df_Greater370GeV / total_entries) * 100:.2f}%)")


    if args.no_plot:
        print("Selections finished. Plotting disabled by --no-plot.")
        return

    if args.mode in ["momentumfractions", "all"]:
        MomentumFractions(df_SingleMuon, df_MCDYJets, args.pt_cuts, args.output_suffix)

    if args.mode in ["mllyll", "all"]:
        MassRapidity(df_SingleMuon, df_MCDYJets, args.pt_cuts, args.output_suffix)

    if args.mode in ["sigmaeff", "all"]:
        SigmaEff(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias, args.vars, args.pt_cuts, args.output_suffix, args.q_bins, args.b_bins, args.binweight, args.mass_rapidity)
    
    if args.mode in ["enhfactorratiotoz", "all"]:
        EnhancementFactorRatioToZ(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias, args.vars, args.pt_cuts, args.output_suffix, args.q_bins, args.b_bins, args.binweight, args.mass_rapidity)

    if args.mode in ["massrappt", "all"]:
        MassRapPt3D(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias, args.vars, args.output_suffix, args.q_bins, args.b_bins, args.binweight, args.axes)
    
    if args.mode in ["histograms", "all"]:
        Histograms(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias, args.vars, args.kin_filter, args.ratio, args.axis, args.output_suffix, args.q_bins, args.b_bins)

    if args.mode in ["averageobservablesvszpt", "all"]:
        AverageObservablesVsZpT(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias, args.vars, args.output_suffix)
    
    if args.mode in ["variancemethod", "all"]:
        RapidityVarianceMethod(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias, args.vars, args.output_suffix, args.weight)

    if args.mode in ["rapidityvariancekinematics3d", "all"]:
        RapidityVarianceKinematics3D(df_SingleMuon, df_MCDYJets, args.output_suffix, args.weight)

    # if args.mode in ["pocketformularatio", "all"]:
    #     df_NoMPI = None
    #     if args.nompi_file is not None:
    #         df_NoMPI = ROOT.RDataFrame("Events", args.nompi_file)
    #         if args.maxevents is not None:
    #             df_NoMPI = df_NoMPI.Range(args.maxevents)
    #     PocketFormulaRatio(df_SingleMuon, df_MCDYJets, df_NoMPI, args.cz_cuts, args.output_suffix)

    end = time.time()
    elapsed_time = end - start
    print(f"\nTotal execution time: {elapsed_time:.2f} seconds")
    # print("\nAll requested plots have been generated successfully.")

if __name__ == "__main__":
    main()
