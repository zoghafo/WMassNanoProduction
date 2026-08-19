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

ROOT.gROOT.SetBatch(True)



path = "/pnfs/psi.ch/cms/trivcat/store/user/zoghafoo/crabsubmission_files/selEvents"

scratch_path = "/scratch/zoghafoo"


DATASETS = [
            "SingleMuon",
            "MinBias",
            "MCDY",
            "MCMinBias"
           ]

FILES = [
         f"{path}/SingleMuon_SelectedEvents_RunII2016FGH.root",
         f"{path}/MinBias_SelectedEvents_RunII2016FGH.root",
         f"{path}/MCDY_SelectedEvents.root",
         f"{path}/MCMinBias_SelectedEvents.root"
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
}

VARIABLESFORPYTHON = {
    "PFCands_pt": r'$p_{T}\,\mathrm{[GeV]}$',
    "PFCands_eta": r'$\eta$',
    "PFCands_phi": r'$\phi$',
    "PFCands_pvAssocQuality": r'$^{\mathrm{PV}}\,\mathrm{association\,quality}$',
    "nPFCands": r'$N_{\mathrm{PF}}^{\mathrm{charged}}$',
    "PFCands_Ht": r'$H_{T}\,\mathrm{[GeV]}$',
    "PFCands_Pt2sum": r'$\sum_{\mathrm{PF\,cands}} p_{T}^{2}\,\mathrm{[GeV^{2}]}$',
    "PFCands_Psum": r'$\sum_{\mathrm{PF\,cands}} p\,\mathrm{[GeV]}$',
    "PFCands_P2sum": r'$\sum_{\mathrm{PF\,cands}} p^{2}\,\mathrm{[GeV^{2}]}$',
    "PFCands_InvariantMass": r'$m_{\mathrm{inv}}\,\mathrm{[GeV]}$',
}

BINNING = {
    "PFCands_pt": [20, 0, 100],
    "PFCands_eta": [20, -2.4, 2.4],
    "PFCands_phi": [20, -3.14, 3.14],
    "PFCands_InvariantMass": [0, 2, 5, 10, 15, 20, 25, 35, 45, 60, 80, 120, 160],
    "PFCands_pvAssocQuality": [9, 0, 9],
    "nPFCands": [3.0, 5.0, 8.0, 11.0, 15.0, 20.0, 27.0, 34.0, 43.0, 54.0, 65.0, 90.0, 130.0, 160.0],
    # "PFCands_Ht": [0, 5, 10, 15, 20, 30, 50, 70, 90, 110, 130, 150, 170, 200, 230, 260, 300, 350, 370],
    "PFCands_Ht": [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 60, 70, 80, 90, 100, 110, 120],
    "PFCands_Pt2sum": [0, 10, 20, 30, 40, 50, 70, 90, 120, 140, 160, 200, 250, 300, 350, 400],
    "PFCands_Psum": [0, 10, 20, 30, 40, 50, 60, 70, 100, 150, 200, 250, 300, 350, 400],
    "PFCands_P2sum": [0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 250, 300, 400, 500, 600, 800, 1000, 1500, 2000, 2500, 3000, 3500, 4000],
}


def MakeDataframes(maxevents=None):

    df_SingleMuon = ROOT.RDataFrame("Events", FILES[0])
    df_MinBias = ROOT.RDataFrame("Events", FILES[1])
    df_MCDYJets = ROOT.RDataFrame("Events", FILES[2])
    df_MCMinBias = ROOT.RDataFrame("Events", FILES[3])
    # print("DataFrames created for SingleMuon, MinBias, MCDY, and MCMinBias datasets.")

    if maxevents is not None:
        print(f"Processing only the first {maxevents} Events from each file.")
        df_SingleMuon = df_SingleMuon.Range(maxevents)
        df_MinBias = df_MinBias.Range(maxevents)
        df_MCDYJets = df_MCDYJets.Range(maxevents)
        df_MCMinBias = df_MCMinBias.Range(maxevents)

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

def MakeHist(df, var, label, y_title, bins, hist_name):
    title = f"; {label}; {y_title}"
    if len(bins) == 3:
        return df.Histo1D((hist_name, title, bins[0], bins[1], bins[2]), f"PFSelection_{var}")

    edges = array.array("d", bins)
    return df.Histo1D((hist_name, title, len(edges) - 1, edges), f"PFSelection_{var}")


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




# def AddInvQ(df, var, df_name):

#     column = f"PFSelection_{var}"

#     # Get the values after all filters applied to df
#     var_values = df.AsNumpy([column])[column]

#     # Number of entries actually present after filtering
#     N_Events = len(var_values)

#     # Sort the values
#     sorted_var_values = np.sort(var_values)

#     # Calculate 1 - quantile
#     inv_q = 1.0 - (
#         np.searchsorted(
#             sorted_var_values,
#             var_values,
#             side="right"
#         ) / N_Events
#     )

#     # Create a NEW RDataFrame containing the values and inverse quantiles
#     df_invq = ROOT.RDF.FromNumpy({column: var_values, f"{var}_InvQ": inv_q})

#     return df_invq




# def AddInvQ(df, var, df_name):

#     binning = BINNING[var]

#     column = f"PFSelection_{var}"

#     df = df.Define("InvQ_index", "rdfentry_")

#     # Create temporary histogram with the same binning as the old method
#     h_tmp_ptr = df.Histo1D(
#         (
#             f"h_{var}_quantile_tmp",
#             f"h_{var}_quantile_tmp",
#             len(binning) - 1,
#             np.array(binning, dtype="double")
#         ),
#         column
#     )

#     h_tmp = h_tmp_ptr.GetValue()

#     total = h_tmp.Integral()

#     if total <= 0:
#         print(f"Warning: histogram for {var} has zero integral")
#         return df

#     # Store histogram bin edges and corresponding CDF values
#     bin_edges = [h_tmp.GetBinLowEdge(1)]
#     cdf_values = [0.0]

#     # Build cumulative distribution function
#     cumulative = 0.0

#     for i in range(1, h_tmp.GetNbinsX() + 1):

#         # Add events in current bin
#         cumulative += h_tmp.GetBinContent(i)

#         # Get upper edge of current bin
#         edge = h_tmp.GetBinLowEdge(i + 1)

#         # Calculate CDF value at this edge
#         cdf = cumulative / total

#         # Store edge and CDF value
#         bin_edges.append(edge)
#         cdf_values.append(cdf)


#     # Get the actual event values after all filters
#     numpy_data = df.AsNumpy([column, "InvQ_index"])

#     var_values = numpy_data[column]
#     indices = numpy_data["InvQ_index"]


#     # Interpolate CDF for each event
#     cdf = np.interp(
#         var_values,
#         bin_edges,
#         cdf_values
#     )


#     # Calculate inverse quantile = 1 - CDF
#     inv_q = 1.0 - cdf


#     # Create a unique ROOT vector name
#     vector_name = f"inv_q_{df_name}_{var}_{id(df)}"

#     # Declare C++ vector in ROOT/Cling
#     ROOT.gInterpreter.Declare(
#         f"""
#         std::vector<double> {vector_name};
#         """
#     )

#     # Access the C++ vector
#     cpp_vec = getattr(ROOT, vector_name)

#     # fill dummy values up to maximum rdfentry
#     max_index = int(max(indices))

#     for _ in range(max_index + 1):
#         cpp_vec.push_back(-1.0)

#     for idx, value in zip(indices, inv_q):
#         cpp_vec[int(idx)] = float(value)


#     # Define new column
#     df = df.Define(
#         f"{var}_InvQ",
#         f"{vector_name}[rdfentry_]"
#     )


#     return df



# def QuantileAndIPCalculation(df, var, df_name, q_bins):

#     # Create histogram for MinBias to compute quantiles
#     h_ptr = MakeHist(df, var, "w ", "", q_bins, f"h_{df_name}_{var}_quantile")
#     h = h_ptr.GetValue()
#     total = h.Integral()

#     if total <= 0:
#         print(f"Warning: {df_name} histogram for '{var}' has zero integral; skipping quantile plot")
#         return None

#     # Store the lower edge of the first histogram bin
#     bin_edges = [h.GetBinLowEdge(1)]

#     # Initialise the CDF at the first bin edge with zero probability
#     cdf_values = [0.0]

#     # Total number of events so far
#     cumulative = 0.0

#     # Loop over all histogram bins
#     for i in range(1, h.GetNbinsX() + 1):

#         # Add the number of events in the current bin to the cumulative count
#         cumulative += h.GetBinContent(i)

#         # Get the upper edge of the current bin (lower edge of the next bin)
#         edge = h.GetBinLowEdge(i + 1)

#         # Compute the cumulative probability up to the current bin
#         cdf = cumulative / total if total > 0 else 0.0

#         # Store the current bin edge
#         bin_edges.append(edge)

#         # Store the CDF value at the current bin edge
#         cdf_values.append(cdf)

    
#     # # print numeric variable ranges corresponding to each quantile bin
#     # quantile_bins = bins  # the quantile bin edges passed into the function
#     # print(f"Quantile numeric ranges for {var}:")
#     # for qi in range(len(quantile_bins) - 1):
#     #     q_low = quantile_bins[qi]
#     #     q_high = quantile_bins[qi + 1]
#     #     # map quantile interval [q_low, q_high] in 1-F_MB to CDF range [1-q_high, 1-q_low]
#     #     cdf_low = 1.0 - q_high
#     #     cdf_high = 1.0 - q_low
#     #     x_low = inverse_cdf_from_hist(h, cdf_low)
#     #     x_high = inverse_cdf_from_hist(h, cdf_high)
#     #     if x_low is None or x_high is None:
#     #         print(f"  [{q_low:.3f}, {q_high:.3f}] -> (no events / undefined)")
#     #     else:
#     #         print(f"  [{q_low:.3f}, {q_high:.3f}] -> {x_low:.6g} - {x_high:.6g} (CDF {cdf_low:.3f}-{cdf_high:.3f})")
    

#     edges_cpp = ", ".join(f"{x:.17g}" for x in bin_edges)
#     cdf_cpp = ", ".join(f"{x:.17g}" for x in cdf_values)

#     ROOT.gInterpreter.Declare(
#         f"""
#         namespace {var}InvQMap{df_name} {{
#         static const std::vector<double> edges = {{{edges_cpp}}};
#         static const std::vector<double> cdf = {{{cdf_cpp}}};

#         double eval(double x) {{
#             if (edges.empty()) return 0.0;
#             if (x <= edges.front()) return 0.0;
#             if (x >= edges.back()) return 1.0;

#             for (size_t i = 1; i < edges.size(); ++i) {{
#                 if (x < edges[i]) {{
#                     double x1 = edges[i - 1];
#                     double x2 = edges[i];
#                     double y1 = cdf[i - 1];
#                     double y2 = cdf[i];
#                     return y1 + (x - x1) * (y2 - y1) / (x2 - x1);
#                 }}
#             }}
#             return 1.0;
#         }}
#         }}
#         """
#     )

#     df = df.Define(f"{var}_InvQ", f"{var}InvQMap{df_name}::eval(PFSelection_{var})")
#     df = df.Define(f"{var}_b", f"TMath::Sqrt({var}_InvQ)")

#     return df



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

# ---------------------- PLOTS ----------------------

def Plot_CompareTriggers(df_SingleMuon_var, df_MinBias_var, df_MCDYJets_var, df_MCMinBias_var, variables, out_suffix):


    for var in variables:

        label = VARIABLES[var]
        bins = BINNING[var]
        y_title = "Density #frac{1}{N} #frac{dN}{dx} (normalised)"

        h_SingleMuon_ptr = MakeHist(df_SingleMuon_var, var, label, y_title, bins, f"h_SingleMuon_{var}")
        h_MinBias_ptr = MakeHist(df_MinBias_var, var, label, y_title, bins, f"h_MinBias_{var}")
        h_MCDYJets_ptr = MakeHist(df_MCDYJets_var, var, label, y_title, bins, f"h_MCDYJets_{var}")
        h_MCMinBias_ptr = MakeHist(df_MCMinBias_var, var, label, y_title, bins, f"h_MCMinBias_{var}")

        h_SingleMuon= h_SingleMuon_ptr.GetValue()
        h_MinBias = h_MinBias_ptr.GetValue()
        h_MCDYJets = h_MCDYJets_ptr.GetValue()
        h_MCMinBias = h_MCMinBias_ptr.GetValue()
        NormaliseHist(h_SingleMuon, True)
        NormaliseHist(h_MinBias, True)
        NormaliseHist(h_MCDYJets, True)
        NormaliseHist(h_MCMinBias, True)

        canvas = ROOT.TCanvas(f"c_{var}")

        pad1 = ROOT.TPad("pad1", "pad1", 0, 0.35, 1, 1)
        pad1.Draw()
        pad1.cd()
        pad1.SetBottomMargin(0.08)
        pad1.SetRightMargin(0.04)
        pad1.SetLeftMargin(0.13)
        pad1.SetTopMargin(0.05)
        pad1.SetLogy()
        pad1.SetGridy()
        h_SingleMuon.GetXaxis().SetLabelSize(0)
        h_SingleMuon.SetLineColor(ROOT.kViolet - 6)
        h_SingleMuon.SetLineWidth(2)
        h_SingleMuon.GetXaxis().SetTitle("")
        h_SingleMuon.GetYaxis().SetTitle(y_title)
        h_SingleMuon.GetYaxis().SetLabelSize(0.048)
        h_SingleMuon.GetYaxis().SetTitleSize(0.06)
        h_SingleMuon.GetYaxis().SetTitleOffset(0.8)
        h_SingleMuon.GetYaxis().SetNdivisions(10, False)
        h_SingleMuon.Draw("hist e")

        h_MinBias.SetLineColor(ROOT.kOrange + 5)
        h_MinBias.SetLineWidth(2)
        h_MinBias.Draw("hist e same")

        h_MCDYJets.SetLineColor(ROOT.kViolet - 6)
        h_MCDYJets.SetLineWidth(2)
        h_MCDYJets.SetLineStyle(2)
        h_MCDYJets.Draw("hist e same")

        h_MCMinBias.SetLineColor(ROOT.kOrange + 5)
        h_MCMinBias.SetLineWidth(2)
        h_MCMinBias.SetLineStyle(2)
        h_MCMinBias.Draw("hist e same")

        h_SingleMuon.SetMaximum(max(h_SingleMuon.GetMaximum(), h_MinBias.GetMaximum(), h_MCDYJets.GetMaximum(), h_MCMinBias.GetMaximum()) * 1.3)

        dummy = ROOT.TObject()


        legend_mass = ROOT.TLegend(0.44, 0.84, 0.72, 0.92)
        legend_mass.SetBorderSize(0)
        # legend_mass.SetFillStyle(0)
        legend_mass.SetTextSize(0.06)
        legend_mass.SetMargin(0)
        legend_mass.AddEntry(dummy, " 86 GeV < m_{#mu#mu} < 96 GeV", "")
        legend_mass.Draw()


        legend = ROOT.TLegend(0.74, 0.62, 0.9, 0.92)
        legend.SetBorderSize(0)
        # legend.SetFillStyle(0)
        legend.SetTextSize(0.06)
        legend.SetMargin(0.25)
        

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

        DYMarker = ROOT.TMarker()
        DYMarker.SetMarkerStyle(20)
        DYMarker.SetMarkerSize(1)
        DYMarker.SetMarkerColor(h_SingleMuon.GetLineColor())

        ZeroBiasMarker = ROOT.TMarker()
        ZeroBiasMarker.SetMarkerStyle(20)
        ZeroBiasMarker.SetMarkerSize(1)
        ZeroBiasMarker.SetMarkerColor(h_MinBias.GetLineColor())

        legend.AddEntry(dummy, f"#color[{h_SingleMuon.GetLineColor()}]{{#bf{{DY}}}}", "")
        legend.AddEntry(dummy, f"#color[{h_MinBias.GetLineColor()}]{{#bf{{MinBias}}}}", "")


        legend.Draw()

        canvas.cd()
        pad2 = ROOT.TPad("pad2", "pad2", 0, 0.02, 1, 0.38)
        pad2.Draw()
        pad2.cd()
        pad2.SetTopMargin(0.05)
        pad2.SetBottomMargin(0.35)
        pad2.SetLeftMargin(0.13)
        pad2.SetRightMargin(0.04)
        # pad2.SetRightMargin(0.26)
        if var not in ["PFCands_eta", "PFCands_phi", "PFCands_pvAssocQuality"]:
            pad2.SetLogy()

        ratio_Data = h_SingleMuon.Clone(f"ratio_{var}")
        ratio_Data.Divide(h_MinBias)
        ratio_Data.SetLineColor(ROOT.kBlack)
        ratio_Data.SetMarkerStyle(20)
        ratio_Data.SetMarkerSize(0.8)
        ratio_Data.GetYaxis().SetTitle("Ratio")
        ratio_Data.GetXaxis().SetTitle(label)
        ratio_Data.GetXaxis().SetTitleSize(0.12)
        ratio_Data.GetXaxis().SetTitleOffset(1.2)
        ratio_Data.GetXaxis().SetLabelSize(0.1)
        ratio_Data.GetXaxis().SetTickLength(0.07)
        ratio_Data.GetYaxis().SetTitleSize(0.12)
        ratio_Data.GetYaxis().SetLabelSize(0.09)
        ratio_Data.GetYaxis().SetTitleOffset(0.4)
        ratio_Data.GetYaxis().SetNdivisions(10)

        ratio_MC = h_MCDYJets.Clone(f"ratio_{var}")
        ratio_MC.Divide(h_MCMinBias)
        ratio_MC.SetLineColor(ROOT.kGray + 2)
        ratio_MC.SetLineStyle(1)
        ratio_MC.SetMarkerColor(ROOT.kGray + 2)
        ratio_MC.SetMarkerStyle(20)
        ratio_MC.SetMarkerSize(0.8)
        pad2.SetGridy()

        if var not in ["PFCands_eta", "PFCands_phi", "PFCands_pvAssocQuality"]:

            min_val = ratio_Data.GetBinContent(ratio_Data.GetMinimumBin())
            if min_val <= 0:
                min_val = 1e-3
            max_val = ratio_Data.GetBinContent(ratio_Data.GetMaximumBin())
            if max_val <= 0:
                max_val = 10

            min_val = min_val * 0.2
            max_val = max_val * 10

        else:
            min_val = 0.5
            max_val = 1.5

        ratio_Data.SetMinimum(min_val)
        ratio_Data.SetMaximum(max_val)
        ratio_Data.Draw("pe")
        ratio_MC.Draw("pe same")

        ratio_DY = h_SingleMuon.Clone(f"ratio_{var}")
        ratio_DY.Divide(h_MCDYJets)
        ratio_DY.SetLineColor(ROOT.kViolet - 6)
        ratio_DY.SetMarkerColor(ROOT.kViolet - 6)
        ratio_DY.SetMarkerStyle(20)
        ratio_DY.SetMarkerSize(0.8)
        ratio_DY.GetYaxis().SetTitle("Ratio")
        ratio_DY.GetXaxis().SetTitle(label)
        ratio_DY.GetXaxis().SetTitleSize(0.12)
        ratio_DY.GetXaxis().SetTitleOffset(1.3)
        ratio_DY.GetXaxis().SetLabelSize(0.09)
        ratio_DY.GetXaxis().SetTickLength(0.07)
        ratio_DY.GetYaxis().SetTitleSize(0.12)
        ratio_DY.GetYaxis().SetLabelSize(0.09)
        ratio_DY.GetYaxis().SetTitleOffset(0.5)

        ratio_MinBias = h_MinBias.Clone(f"ratio_{var}")
        ratio_MinBias.Divide(h_MCMinBias)
        ratio_MinBias.SetLineColor(ROOT.kOrange + 5)
        ratio_MinBias.SetMarkerColor(ROOT.kOrange + 5)
        ratio_MinBias.SetMarkerStyle(20)
        ratio_MinBias.SetMarkerSize(0.8)
        pad2.SetGridy()

        if var not in ["PFCands_eta", "PFCands_phi", "PFCands_pvAssocQuality"]:

            min_val = ratio_DY.GetBinContent(ratio_DY.GetMinimumBin())
            if min_val <= 0:
                min_val = 1e-3
            max_val = ratio_DY.GetBinContent(ratio_DY.GetMaximumBin())
            if max_val <= 0:
                max_val = 10

            min_val = min_val * 0.2
            max_val = max_val * 10

        else:
            min_val = 0.5
            max_val = 1.5

        ratio_DY.SetMinimum(min_val)
        ratio_DY.SetMaximum(max_val)
        ratio_DY.Draw("pe same")
        ratio_MinBias.Draw("pe same")

        xmin_legendratio = 0.154
        xmax_legendratio = 0.3
        ymin_legendratio = 0.69
        ymax_legendratio = 0.93

        legend1_ratio = ROOT.TLegend(xmin_legendratio, ymin_legendratio, xmax_legendratio, ymax_legendratio)
        legend2_ratio = ROOT.TLegend(xmin_legendratio + 0.012, ymin_legendratio, xmax_legendratio, ymax_legendratio)

        for legend_ratio in [legend1_ratio, legend2_ratio]:
            # legend_ratio.SetBorderSize(0)
            # legend_ratio.SetFillStyle(0)
            legend_ratio.SetTextSize(0.08)

        legend1_ratio.SetMargin(0.1)
        legend2_ratio.SetMargin(0.13)
        legend2_ratio.SetBorderSize(0)
        legend2_ratio.SetFillStyle(0)

        legend1_ratio.AddEntry(ratio_DY, " ", "pe")
        legend2_ratio.AddEntry(ratio_MinBias, "Data/MC", "pe")

        legend1_ratio.AddEntry(ratio_Data, " ", "pe")
        legend2_ratio.AddEntry(ratio_MC, "DY/MinBias", "pe")

  

        legend1_ratio.Draw()
        legend2_ratio.Draw()

        output_name = f"new_plots/{var}{out_suffix}.pdf"
        canvas.SaveAs(output_name)
        canvas.Close()

def Plot_CompareTriggers_QuantileBinning(df_SingleMuon_var, df_MinBias_var, df_MCDYJets_var, df_MCMinBias_var, variables, out_suffix, quantile_bins=None, quantile_reference="both"):



    for var in variables:
        if var in ["PFCands_pt", "PFCands_eta", "PFCands_phi", "PFCands_pvAssocQuality"]:
            continue

        label = VARIABLES[var]
        bins = BINNING[var]
        y_title = "Density #frac{1}{N} #frac{dN}{dx} (normalised)"

        plot_bins = bins

        h_reference_ptr = MakeHist(
            df_MinBias_var, var, label, y_title, bins,
            f"h_SingleMuon_{var}_quantile_ref"
        )
        h_reference = h_reference_ptr.GetValue()

        if quantile_bins is not None:
            quantile_edges = quantile_edges_from_hist(h_reference, quantile_bins)

            if quantile_edges is not None and len(quantile_edges) > 1:
                plot_bins = array.array("d", quantile_edges)
            else:
                print(
                    f"Warning: could not derive quantile bin edges for '{var}' "
                    f"from {quantile_reference}; using the default binning"
                )

        h_SingleMuon_ptr = MakeHist(df_SingleMuon_var, var, label, y_title, plot_bins, f"h_SingleMuon_{var}")
        h_MinBias_ptr = MakeHist(df_MinBias_var, var, label, y_title, plot_bins, f"h_MinBias_{var}")
        h_MCDY_ptr = MakeHist(df_MCDYJets_var, var, label, y_title, plot_bins, f"h_MCDY_{var}")
        h_MCMinBias_ptr = MakeHist(df_MCMinBias_var, var, label, y_title, plot_bins, f"h_MCMinBias_{var}")

        h_SingleMuon = h_SingleMuon_ptr.GetValue()
        h_MinBias = h_MinBias_ptr.GetValue()
        NormaliseHist(h_SingleMuon, True)
        NormaliseHist(h_MinBias, True)
        h_MCDY = h_MCDY_ptr.GetValue()
        h_MCMinBias = h_MCMinBias_ptr.GetValue()
        NormaliseHist(h_MCDY, True)
        NormaliseHist(h_MCMinBias, True)


        if quantile_bins is not None:
            
            print(f"Quantile numeric ranges for {var} from the normal distributions ({quantile_reference} reference):")

            for qi in range(len(quantile_bins) - 1):
                q_low = quantile_bins[qi]
                q_high = quantile_bins[qi + 1]

                SingleMuon_low = None
                SingleMuon_high = None
                MinBias_low = None
                MinBias_high = None
                MCDY_low = None
                MCDY_high = None
                MCMinBias_low = None
                MCMinBias_high = None

                SingleMuon_low = inverse_cdf_from_hist(h_SingleMuon, 1.0 - q_high)
                SingleMuon_high = inverse_cdf_from_hist(h_SingleMuon, 1.0 - q_low)
                MinBias_low = inverse_cdf_from_hist(h_MinBias, 1.0 - q_high)
                MinBias_high = inverse_cdf_from_hist(h_MinBias, 1.0 - q_low)

                MCDY_low = inverse_cdf_from_hist(h_MCDY, 1.0 - q_high)
                MCDY_high = inverse_cdf_from_hist(h_MCDY, 1.0 - q_low)
                MCMinBias_low = inverse_cdf_from_hist(h_MCMinBias, 1.0 - q_high)
                MCMinBias_high = inverse_cdf_from_hist(h_MCMinBias, 1.0 - q_low)

                if SingleMuon_low is None or SingleMuon_high is None or MinBias_low is None or MinBias_high is None:
                    print(f"  [{q_low:.3f}, {q_high:.3f}] -> undefined")
                else:
                    print(
                        f"  [{q_low:.3f}, {q_high:.3f}] -> "
                        f"Data SingleMuon {SingleMuon_low:.6g} - {SingleMuon_high:.6g}, "
                        f"Data MinBias {MinBias_low:.6g} - {MinBias_high:.6g}"
                    )
                if MCDY_low is None or MCDY_high is None or MCMinBias_low is None or MCMinBias_high is None:
                    print(f"  [{q_low:.3f}, {q_high:.3f}] -> undefined")
                else:
                    print(
                        f"  [{q_low:.3f}, {q_high:.3f}] -> "
                        f"MCDY {MCDY_low:.6g} - {MCDY_high:.6g}, "
                        f"MCMinBias {MCMinBias_low:.6g} - {MCMinBias_high:.6g}"
                    )
                data_missing = SingleMuon_low is None or SingleMuon_high is None or MinBias_low is None or MinBias_high is None
                mc_missing = MCDY_low is None or MCDY_high is None or MCMinBias_low is None or MCMinBias_high is None
                if data_missing and mc_missing:
                    print(f"  [{q_low:.3f}, {q_high:.3f}] -> undefined")
                else:
                    parts = []
                    if not data_missing:
                        parts.append(f"Data SingleMuon {SingleMuon_low:.6g} - {SingleMuon_high:.6g}, Data MinBias {MinBias_low:.6g} - {MinBias_high:.6g}")
                    else:
                        parts.append("Data: undefined")
                    if not mc_missing:
                        parts.append(f"MCDY {MCDY_low:.6g} - {MCDY_high:.6g}, MCMinBias {MCMinBias_low:.6g} - {MCMinBias_high:.6g}")
                    else:
                        parts.append("MC: undefined")
                    print(f"  [{q_low:.3f}, {q_high:.3f}] -> " + "; ".join(parts))
                    

        canvas = ROOT.TCanvas(f"c_{var}")
        canvas.SetGridy(1)
        canvas.SetTicky(0)

        pad1 = ROOT.TPad("pad1", "pad1", 0, 0.32, 1, 1)
        pad1.Draw()
        pad1.cd()
        pad1.SetBottomMargin(0.07)
        pad1.SetRightMargin(0.26)
        pad1.SetLogy()
        pad1.SetGridy(1)
        pad1.SetTicky(0)

        h_SingleMuon.GetXaxis().SetLabelSize(0)
        h_SingleMuon.SetLineColor(ROOT.kViolet - 6)
        h_SingleMuon.SetLineWidth(2)
        h_SingleMuon.GetXaxis().SetTitle("")
        h_SingleMuon.GetYaxis().SetTitle(y_title)
        h_SingleMuon.GetYaxis().SetLabelSize(0.048)
        h_SingleMuon.GetYaxis().SetTitleSize(0.045)
        h_SingleMuon.GetYaxis().SetTitleOffset(1)
        h_SingleMuon.Draw("hist e")

        h_MinBias.SetLineColor(ROOT.kOrange + 5)
        h_MinBias.SetLineWidth(2)
        h_MinBias.Draw("hist e same")

        h_SingleMuon.SetMaximum(max(h_SingleMuon.GetMaximum(), h_MinBias.GetMaximum()) * 1.3)
        h_SingleMuon.GetYaxis().SetNdivisions(10, False)

        h_MCDY.GetXaxis().SetTitle("")
        h_MCDY.GetYaxis().SetTitle(y_title)
        h_MCDY.GetYaxis().SetLabelSize(0.048)
        h_MCDY.GetYaxis().SetTitleSize(0.045)
        h_MCDY.GetYaxis().SetTitleOffset(1)

        h_MCDY.SetLineColor(ROOT.kViolet - 6)
        h_MCDY.SetLineStyle(2)
        h_MCDY.SetLineWidth(2)
        h_MCDY.Draw("hist e same")

        h_MCMinBias.SetLineColor(ROOT.kOrange + 5)
        h_MCMinBias.SetLineWidth(2)
        h_MCMinBias.SetLineStyle(2)
        h_MCMinBias.Draw("hist e same")

        h_MCDY.SetMaximum(max(h_MCDY.GetMaximum(), h_MCMinBias.GetMaximum()) * 1.3)
        h_MCDY.GetYaxis().SetNdivisions(10, False)
        
        legend_mass = ROOT.TLegend(0.14, 0.82, 0.33, 0.87)
        legend_mass.SetBorderSize(0)
        # legend_mass.SetFillStyle(0)
        legend_mass.SetTextSize(0.04)
        legend_mass.SetMargin(0.02)

        dummy = ROOT.TObject()

        legend_mass.AddEntry(dummy, "86 GeV < m_{#mu#mu} < 96 GeV", "")
        legend_mass.Draw()

    

        legend = ROOT.TLegend(0.75, 0.5, 0.96, 0.87)
        legend.SetBorderSize(0)
        legend.SetFillStyle(0)
        legend.SetTextSize(0.06)
        legend.SetMargin(0.2)

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
        legend.AddEntry(dummy, f"#color[{h_SingleMuon.GetLineColor()}]{{#bf{{DY}}}}", "")
        legend.AddEntry(dummy, f"#color[{h_MinBias.GetLineColor()}]{{#bf{{MinBias}}}}", "")

        legend.Draw()

        canvas.cd()
        pad2 = ROOT.TPad("pad2", "pad2", 0, 0, 1, 0.35)
        pad2.Draw()
        pad2.cd()
        pad2.SetTopMargin(0.03)
        pad2.SetBottomMargin(0.35)
        pad2.SetRightMargin(0.26)

        pad2.SetGridy(1)
        pad2.SetTicky(0)

        if var not in ["PFCands_eta", "PFCands_phi", "PFCands_pvAssocQuality"]:
            pad2.SetLogy()

        ratio_SingleMuon = h_SingleMuon.Clone(f"ratio_{var}")
        ratio_SingleMuon.Divide(h_MinBias)
        ratio_SingleMuon.SetLineColor(ROOT.kBlack)
        ratio_SingleMuon.SetMarkerStyle(20)
        ratio_SingleMuon.SetMarkerSize(0.6)
        ratio_SingleMuon.GetYaxis().SetTitle("DY/ZeroBias")
        ratio_SingleMuon.GetXaxis().SetTitle(label)
        ratio_SingleMuon.GetXaxis().SetTitleSize(0.1)
        ratio_SingleMuon.GetXaxis().SetTitleOffset(1.3)
        ratio_SingleMuon.GetXaxis().SetLabelSize(0.09)
        ratio_SingleMuon.GetXaxis().SetTickLength(0.07)
        ratio_SingleMuon.GetYaxis().SetTitleSize(0.09)
        ratio_SingleMuon.GetYaxis().SetLabelSize(0.08)
        ratio_SingleMuon.GetYaxis().SetTitleOffset(0.5)
        ratio_SingleMuon.Draw("pe")
        ratio_SingleMuon.GetYaxis().SetNdivisions(10, False)

        ratio_MCDYJets = h_MCDY.Clone(f"ratio_{var}")
        ratio_MCDYJets.Divide(h_MCMinBias)
        ratio_MCDYJets.SetLineColor(ROOT.kGray + 2)
        ratio_MCDYJets.SetLineStyle(1)
        ratio_MCDYJets.SetMarkerColor(ROOT.kGray + 2)
        ratio_MCDYJets.SetMarkerStyle(20)
        ratio_MCDYJets.SetMarkerSize(0.6)
        ratio_MCDYJets.GetYaxis().SetTitle("DY/ZeroBias")
        ratio_MCDYJets.GetXaxis().SetTitle(label)
        ratio_MCDYJets.GetXaxis().SetTitleSize(0.1)
        ratio_MCDYJets.GetXaxis().SetTitleOffset(1.3)
        ratio_MCDYJets.GetXaxis().SetLabelSize(0.09)
        ratio_MCDYJets.GetYaxis().SetTitleSize(0.09)
        ratio_MCDYJets.GetYaxis().SetLabelSize(0.08)
        ratio_MCDYJets.GetYaxis().SetTitleOffset(0.5)
        ratio_MCDYJets.Draw("pe" if quantile_reference == "MC" else "pe same")
        ratio_MCDYJets.GetYaxis().SetNdivisions(10, False)



        min_val = ratio_SingleMuon.GetBinContent(ratio_SingleMuon.GetMinimumBin())
        # print(f"min_val for {var} (Data): {min_val}")
        if min_val <= 0:
            min_val = 1e-3
        max_val = ratio_SingleMuon.GetBinContent(ratio_SingleMuon.GetMaximumBin())
        # print(f"max_val for {var} (Data): {max_val}")
        if max_val <= 0:
            max_val = 10

        min_val = min_val * 0.9
        max_val = max_val * 2

        ratio_SingleMuon.SetMinimum(min_val)
        ratio_SingleMuon.SetMaximum(max_val)


        min_val = ratio_MCDYJets.GetBinContent(ratio_MCDYJets.GetMinimumBin())
        if min_val <= 0:
            min_val = 1e-3
        max_val = ratio_MCDYJets.GetBinContent(ratio_MCDYJets.GetMaximumBin())
        if max_val <= 0:
            max_val = 10

        min_val = min_val * 0.8
        max_val = max_val * 10

        ratio_MCDYJets.SetMinimum(min_val)
        ratio_MCDYJets.SetMaximum(max_val)


        # add small inset zoom (bottom-right)
        canvas.cd()
        inset = ROOT.TPad(f"inset_{var}", f"inset_{var}", 0.34, 0.49, 0.74, 0.94)
        inset.SetLogy()
        inset.SetFillStyle(0)
        inset.SetBorderSize(1)
        inset.SetRightMargin(0.05)
        inset.SetTopMargin(0.08)
        inset.SetBottomMargin(0.12)
        inset.Draw()
        inset.cd()

        max_bin = ratio_SingleMuon.GetMaximumBin()
        zoom_xmax = ratio_SingleMuon.GetBinLowEdge(max_bin) + 0.02 * ratio_SingleMuon.GetBinWidth(max_bin)
        
        print(f"zoom_xmax for {var}: {zoom_xmax}")


        inset.DrawFrame(0, 10**(-3), zoom_xmax, 1)
        frame = inset.DrawFrame(
                                0,
                                min(h_SingleMuon.GetMinimum(), h_MinBias.GetMinimum(), h_MCDY.GetMinimum(), h_MCMinBias.GetMinimum()),
                                zoom_xmax,
                                max(h_SingleMuon.GetMaximum(), h_MinBias.GetMaximum(), h_MCDY.GetMaximum(), h_MCMinBias.GetMaximum()) * 1.1
                                )
        frame.GetXaxis().SetLabelSize(0.05)
        frame.GetYaxis().SetLabelSize(0.05)
        frame.GetXaxis().SetTitleSize(0.05)
        frame.GetYaxis().SetTitleSize(0.05)
        frame.GetYaxis().SetNdivisions(10, False)
        inset.SetGridy(1)
        inset.SetTicky(0)
        
        # clone histograms so axis/range changes don't affect main pads
        h1 = h_SingleMuon.Clone(h_SingleMuon.GetName() + "_inset")
        h2 = h_MinBias.Clone(h_MinBias.GetName() + "_inset")
        h1MC = h_MCDY.Clone(h_MCDY.GetName() + "_inset")
        h2MC = h_MCMinBias.Clone(h_MCMinBias.GetName() + "_inset")

        for hh in (h1, h2, h1MC, h2MC) if quantile_reference == "both" else (h1, h2) if quantile_reference == "Data" else (h1MC, h2MC):
            hh.SetStats(0)
        h1.SetLineColor(ROOT.kViolet - 6)
        h1.SetLineWidth(2)
        h1.GetYaxis().SetTitle("")
        h2.SetLineColor(ROOT.kOrange + 5)
        h2.SetLineWidth(2)
        h1.Draw("hist e same")
        h2.Draw("hist e same")
        h1MC.SetLineColor(ROOT.kViolet - 6)
        h1MC.SetLineWidth(2)
        h1MC.GetYaxis().SetTitle("")
        h2MC.SetLineColor(ROOT.kOrange + 5)
        h2MC.SetLineWidth(2)
        h1MC.SetLineStyle(2)
        h2MC.SetLineStyle(2)
        h1MC.Draw("hist e same")
        h2MC.Draw("hist e same")

        canvas.cd()

        inset_ratio = ROOT.TPad(f"inset_ratio_{var}", f"inset_ratio_{var}", 0.75, 0, 0.999, 0.7)
        inset_ratio.SetLogy()
        inset_ratio.SetGridy()
        inset_ratio.SetFillStyle(0)
        inset_ratio.SetBorderSize(1)
        inset_ratio.SetLeftMargin(0.15)
        inset_ratio.SetBottomMargin(0.175)

        inset_ratio.Draw()
        inset_ratio.cd()
        ymin = (min(ratio_SingleMuon.GetMinimum(), ratio_MCDYJets.GetMinimum()))
        ymax = (max(ratio_SingleMuon.GetMaximum(), ratio_MCDYJets.GetMaximum()))
        inset_ratio.DrawFrame(0, ymin, zoom_xmax, ymax)
        frame_ratio = inset_ratio.DrawFrame(0, ymin, zoom_xmax, ymax)
        frame_ratio.GetXaxis().SetLabelSize(0.07)
        frame_ratio.GetYaxis().SetLabelSize(0.07)
        frame_ratio.GetXaxis().SetTitleSize(0.07)
        frame_ratio.GetYaxis().SetTitleSize(0.07)
        frame_ratio.GetXaxis().SetTitle("")
        frame_ratio.GetYaxis().SetTitle("")
        frame_ratio.GetXaxis().SetRangeUser(0, zoom_xmax)
        frame_ratio.GetYaxis().SetRangeUser(ymin, ymax)
        frame_ratio.GetYaxis().SetNdivisions(10, False)
        inset_ratio.SetGridy(1)
        inset_ratio.SetTicky(0)


        hdata_ratio = ratio_SingleMuon.Clone(ratio_SingleMuon.GetName() + "_insetratio")
        hdata_ratio.SetStats(0)
        hdata_ratio.SetLineWidth(2)
        hdata_ratio.Draw("pe same")

        hMC_ratio = ratio_MCDYJets.Clone(ratio_MCDYJets.GetName() + "_insetratio")
        hMC_ratio.SetStats(0)
        hMC_ratio.SetLineWidth(2)
        hMC_ratio.Draw("pe same")

        pad2.cd()
        legend_ratio = ROOT.TLegend(0.67, 0.4, 0.725, 0.58)
        legend_ratio.SetBorderSize(0)
        # legend_ratio.SetFillStyle(0)
        legend_ratio.SetTextSize(0.08)
        legend_ratio.AddEntry(ratio_SingleMuon, "Data", "pe")
        legend_ratio.AddEntry(ratio_MCDYJets, "MC", "pe")
        legend_ratio.Draw()

        output_name = f"new_plots/{var}_QuantileBinning{out_suffix}.pdf"
        canvas.SaveAs(output_name)
        canvas.Close()

def Plot_DiMuonPtCut(df_SingleMuon_var, df_MinBias_var, df_MCDYJets_var, df_MCMinBias_var, variables, pt_cuts, out_suffix):


    pt_cuts = parse_pt_cuts(pt_cuts)

    colours = [ROOT.kViolet - 6, ROOT.kBlue - 4, ROOT.kRed + 1, ROOT.kGreen + 3, ROOT.kCyan + 1, ROOT.kMagenta + 2]

    for var in variables:
        label = VARIABLES[var]
        bins = BINNING[var]
        y_title = "Density #frac{1}{N} #frac{dN}{dx} (normalised)"

        h_MinBias_ptr = MakeHist(df_MinBias_var, var, label, y_title, bins, f"h_MinBias_{var}_ptscan")
        h_MinBias = h_MinBias_ptr.GetValue()
        NormaliseHist(h_MinBias, True)

        h_MCMinBias_ptr = MakeHist(df_MCMinBias_var, var, label, y_title, bins, f"h_MCMinBias_{var}_ptscan")
        h_MCMinBias = h_MCMinBias_ptr.GetValue()
        NormaliseHist(h_MCMinBias, True)

        canvas = ROOT.TCanvas(f"c_ptscan_{var}")
        canvas.cd()
        canvas.SetRightMargin(0.08)
        canvas.SetLeftMargin(0.15)
        canvas.SetBottomMargin(0.15)
        canvas.SetLogy()

        pad1 = ROOT.TPad(f"pad1_{var}", "pad1", 0, 0.35, 1, 1)
        pad1.Draw()
        pad1.cd()
        pad1.SetBottomMargin(0.08)
        pad1.SetRightMargin(0.04)
        pad1.SetLeftMargin(0.13)
        pad1.SetTopMargin(0.05)
        pad1.SetLogy()    
        pad1.SetGridy()   


        legend_DataMCDYMinBias = ROOT.TLegend(0.52, 0.7, 0.67, 0.92)
        legend_DataMCDYMinBias.SetMargin(0.3)
        legend_col1 = ROOT.TLegend(0.66, 0.68, 0.95, 0.92)
        legend_col1.SetMargin(0.05)

        dummy = ROOT.TObject()
        
        for legend in (legend_DataMCDYMinBias, legend_col1):
            legend.SetBorderSize(0)
            # legend.SetFillStyle(0)
            legend.SetTextSize(0.06)
            

        legend_DataStyle = ROOT.TLine(0.0, 0.0, 0.5, 0.0)
        legend_DataStyle.SetLineColor(ROOT.kBlack)
        legend_DataStyle.SetLineWidth(2)
        legend_DataStyle.SetLineStyle(1)

        legend_MCStyle = ROOT.TLine(0.0, 0.0, 0.5, 0.0)
        legend_MCStyle.SetLineColor(ROOT.kBlack)
        legend_MCStyle.SetLineWidth(2)
        legend_MCStyle.SetLineStyle(2)

        legend_DataMCDYMinBias.AddEntry(legend_DataStyle, "#bf{Data}", "l")
        legend_DataMCDYMinBias.AddEntry(legend_MCStyle, "#bf{MC}", "l")

        legend_col1.AddEntry(dummy, " 86 GeV < m_{#mu#mu} < 96 GeV", "")
        legend_col1.AddEntry(dummy, "#bf{DY:}", "")

        
        histos = []
        ratios = []
        plot_max = 0


        h_MinBias.SetLineWidth(2)
        h_MinBias.SetLineColor(ROOT.kOrange + 5)
        h_MinBias.GetXaxis().SetTitle(label)
        h_MinBias.GetXaxis().SetTitleSize(0)
        h_MinBias.GetXaxis().SetLabelSize(0)
        h_MinBias.GetXaxis().SetTitleOffset(1.2)
        h_MinBias.GetYaxis().SetLabelSize(0.048)
        h_MinBias.GetYaxis().SetTitleSize(0.06)
        h_MinBias.GetYaxis().SetTitleOffset(0.8)
        h_MinBias.Draw("hist")

        h_MCMinBias.SetLineWidth(2)
        h_MCMinBias.SetLineStyle(2)
        h_MCMinBias.SetLineColor(ROOT.kOrange + 5)
        h_MCMinBias.GetXaxis().SetTitle(label)
        h_MCMinBias.GetXaxis().SetTitleSize(0)
        h_MCMinBias.GetXaxis().SetLabelSize(0)
        h_MCMinBias.GetXaxis().SetTitleOffset(1.2)
        h_MCMinBias.GetYaxis().SetLabelSize(0.048)
        h_MCMinBias.GetYaxis().SetTitleSize(0.06)
        h_MCMinBias.GetYaxis().SetTitleOffset(0.8)
        h_MCMinBias.Draw("hist e same")

        canvas.cd()

        pad2 = ROOT.TPad(f"pad2_{var}", "pad2", 0, 0.02, 1, 0.38)
        pad2.Draw()
        pad2.cd()
        pad2.SetTopMargin(0.05)
        pad2.SetBottomMargin(0.35)
        pad2.SetLeftMargin(0.13)
        pad2.SetRightMargin(0.04)
        pad2.SetLogy()
        pad2.SetGridy()

        for index, pt_cut in enumerate(pt_cuts):
            canvas.cd()
            pad1.cd()
            
            print(f"\n\nProcessing DiMuon pT cut: {pt_cut} GeV...\n")
            

            if pt_cut is None or len(pt_cuts) == 0:

                print(f"\n\nNo DiMuon pT cut specified.\n")
                df_SingleMuon_cut = df_SingleMuon_var
                df_MCDYJets_cut = df_MCDYJets_var

            else:
                print(f"Applying diMuon pT cut: {pt_cut} GeV...")

                df_SingleMuon_cut = DiMuonPtCut(df_SingleMuon_var, pt_cut)
                df_MCDYJets_cut = DiMuonPtCut(df_MCDYJets_var, pt_cut)

            colour = colours[index % len(colours)]

            h_SingleMuon_ptr = MakeHist(df_SingleMuon_cut, var, label, y_title, bins, f"h_SingleMuon_{var}_{pt_cut}GeV")
            h_MCDYJets_ptr = MakeHist(df_MCDYJets_cut, var, label, y_title, bins, f"h_MCDYJets_{var}_{pt_cut}GeV")

            h_SingleMuon= h_SingleMuon_ptr.GetValue()
            NormaliseHist(h_SingleMuon, True)

            h_MCDYJets= h_MCDYJets_ptr.GetValue()
            NormaliseHist(h_MCDYJets, True)


            h_SingleMuon.SetStats(0)
            h_SingleMuon.SetLineColor(colour)
            h_SingleMuon.SetLineWidth(2)
            h_SingleMuon.GetXaxis().SetTitle(label)
            h_SingleMuon.GetXaxis().SetTitleSize(0.035)
            h_SingleMuon.GetXaxis().SetLabelSize(0.035)
            h_SingleMuon.GetXaxis().SetTitleOffset(1.6)
            h_SingleMuon.GetYaxis().SetLabelSize(0.048)
            h_SingleMuon.GetYaxis().SetTitleSize(0.06)
            h_SingleMuon.GetYaxis().SetTitleOffset(0.8)


            h_MCDYJets.SetStats(0)
            h_MCDYJets.SetLineColor(colour)
            h_MCDYJets.SetLineWidth(2)
            h_MCDYJets.SetLineStyle(2)
            h_MCDYJets.GetXaxis().SetTitle(label)
            h_MCDYJets.GetXaxis().SetTitleSize(0.035)
            h_MCDYJets.GetXaxis().SetLabelSize(0.035)
            h_MCDYJets.GetXaxis().SetTitleOffset(1.2)
            h_MCDYJets.GetYaxis().SetLabelSize(0.048)
            h_MCDYJets.GetYaxis().SetTitleSize(0.06)
            h_MCDYJets.GetYaxis().SetTitleOffset(0.8)

            h_SingleMuon.Draw("hist e same")
            h_MCDYJets.Draw("hist e same")
 

            # max_val = max(h_SingleMuon.GetMaximum(), h_MCDYJets.GetMaximum(), h_MinBias.GetMaximum(), h_MCMinBias.GetMaximum())
            # if plot_max < max_val:
            #     plot_max = max_val
            # h_SingleMuon.SetMaximum(plot_max * 10)

            for h in [h_SingleMuon, h_MCDYJets, h_MinBias, h_MCMinBias]:
                histos.append(h)

            if pt_cut is None or len(pt_cuts) == 0:
                legend_col1.AddEntry(dummy, f"#color[{colour}]{{#bf{{  No p^{{#mu#mu}}_{{T}} cut}}}}", "")
            else:
                legend_col1.AddEntry(dummy, f"#color[{colour}]{{#bf{{  p^{{#mu#mu}}_{{T}} < {int(pt_cut)} GeV}}}}", "")

            canvas.cd()
            pad2.cd()

            ratio_Data = h_SingleMuon.Clone(f"ratio_Data_{var}_{pt_cut}GeV")
            ratio_Data.Divide(h_MinBias)
            ratio_Data.SetLineColor(colour)
            ratio_Data.SetMarkerColor(colour)
            ratio_Data.SetMarkerStyle(20)
            ratio_Data.GetXaxis().SetTitle(label)
            ratio_Data.GetXaxis().SetTitleSize(0.12)
            ratio_Data.GetXaxis().SetLabelSize(0.1)
            ratio_Data.GetXaxis().SetTitleOffset(1.2)
            ratio_Data.GetYaxis().SetTitle("DY/MinBias")
            ratio_Data.GetYaxis().SetLabelSize(0.09)
            ratio_Data.GetYaxis().SetTitleSize(0.12)
            ratio_Data.GetYaxis().SetTitleOffset(0.4)
            ratio_Data.GetYaxis().SetNdivisions(10)

            ratio_MC = h_MCDYJets.Clone(f"ratio_MC_{var}_{pt_cut}GeV")
            ratio_MC.Divide(h_MCMinBias)
            ratio_MC.SetLineColor(colour - 2)
            ratio_MC.SetMarkerColor(colour - 2)
            ratio_MC.SetMarkerStyle(20)
            ratio_MC.SetLineWidth(2)
            ratio_MC.SetLineStyle(2)

            ratio_Data.Draw("pe same")
            ratio_MC.Draw("pe same")

            ratios.append(ratio_Data)
            ratios.append(ratio_MC)
            

            print(f"Finished processing diMuon pT cut: {pt_cut} GeV!\n")



        canvas.cd()
        pad1.cd()
        legend_DataMCDYMinBias.AddEntry(dummy, f"#color[{ROOT.kOrange + 5}]{{#bf{{MinBias}}}}", "")
        
        legend_col1.Draw()
        legend_DataMCDYMinBias.Draw()

        canvas.cd()
        pad2.cd()
        
        legend_ratio = ROOT.TLegend(0.87, 0.4, 0.95, 0.58)
        ratios[0].SetMarkerSize(0.8)
        ratios[1].SetMarkerSize(0.8)
        legend_ratio.SetBorderSize(0)
        # legend_ratio.SetFillStyle(0)
        legend_ratio.SetTextSize(0.08)
        legend_ratio.SetMargin(0.3)
        legend_ratio.AddEntry(ratios[0], "Data", "pe")
        legend_ratio.AddEntry(ratios[1], "MC", "pe")
        legend_ratio.Draw()

        canvas.cd()


        if pt_cuts is None or len(pt_cuts) == 0:
            output_name = f"new_plots/{var}_NoGeVZPtCut{out_suffix}.pdf"
        else:
            output_name = f"new_plots/{var}_{int(pt_cut)}GeVZPtCut{out_suffix}.pdf"
        canvas.SaveAs(output_name)
        canvas.Close()

def Plot_DiMuonPtCut_QuantileBinning(df_SingleMuon_var, df_MinBias_var, df_MCDYJets_var, df_MCMinBias_var, variables, pt_cuts, out_suffix, quantile_bins=None, quantile_reference="both"):

    pt_cuts = parse_pt_cuts(pt_cuts)

    colours = [
                ROOT.kViolet - 6,
                ROOT.kBlue + 1,
                ROOT.kRed + 1,
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
                ROOT.kBlack
                ]

    for var in variables:
        if var in ["PFCands_pt", "PFCands_eta", "PFCands_phi", "PFCands_pvAssocQuality"]:
            continue

        label = VARIABLES[var]
        bins = BINNING[var]
        y_title = "Density #frac{1}{N} #frac{dN}{dx} (normalised)"

        plot_bins = bins

        h_reference_ptr = MakeHist(
            df_MinBias_var, var, label, y_title, bins,
            f"h_SingleMuon_{var}_quantile_ref"
        )

        h_reference = h_reference_ptr.GetValue()

        if quantile_bins is not None:
            quantile_edges = quantile_edges_from_hist(h_reference, quantile_bins)

            if quantile_edges is not None and len(quantile_edges) > 1:
                plot_bins = array.array("d", quantile_edges)
                print(f"\n\n{var} quantile edges:")
                print(quantile_edges)
                print()
                print()
            else:
                print(
                    f"Warning: could not derive quantile bin edges for '{var}' "
                    f"from {quantile_reference}; using the default binning"
                )

        h_SingleMuon_ptr = MakeHist(df_SingleMuon_var, var, label, y_title, plot_bins, f"h_SingleMuon_{var}")
        h_MinBias_ptr = MakeHist(df_MinBias_var, var, label, y_title, plot_bins, f"h_MinBias_{var}")
        h_MCDY_ptr = MakeHist(df_MCDYJets_var, var, label, y_title, plot_bins, f"h_MCDY_{var}")
        h_MCMinBias_ptr = MakeHist(df_MCMinBias_var, var, label, y_title, plot_bins, f"h_MCMinBias_{var}")

        h_SingleMuon = h_SingleMuon_ptr.GetValue()
        h_MinBias = h_MinBias_ptr.GetValue()
        NormaliseHist(h_SingleMuon, True)
        NormaliseHist(h_MinBias, True)
        h_MCDY = h_MCDY_ptr.GetValue()
        h_MCMinBias = h_MCMinBias_ptr.GetValue()
        NormaliseHist(h_MCDY, True)
        NormaliseHist(h_MCMinBias, True)


        if quantile_bins is not None:
            
            # print(f"Quantile numeric ranges for {var} from the normal distributions ({quantile_reference} reference):")

            for qi in range(len(quantile_bins) - 1):
                q_low = quantile_bins[qi]
                q_high = quantile_bins[qi + 1]

                SingleMuon_low = None
                SingleMuon_high = None
                MinBias_low = None
                MinBias_high = None
                MCDY_low = None
                MCDY_high = None
                MCMinBias_low = None
                MCMinBias_high = None

                SingleMuon_low = inverse_cdf_from_hist(h_SingleMuon, 1.0 - q_high)
                SingleMuon_high = inverse_cdf_from_hist(h_SingleMuon, 1.0 - q_low)
                MinBias_low = inverse_cdf_from_hist(h_MinBias, 1.0 - q_high)
                MinBias_high = inverse_cdf_from_hist(h_MinBias, 1.0 - q_low)

                MCDY_low = inverse_cdf_from_hist(h_MCDY, 1.0 - q_high)
                MCDY_high = inverse_cdf_from_hist(h_MCDY, 1.0 - q_low)
                MCMinBias_low = inverse_cdf_from_hist(h_MCMinBias, 1.0 - q_high)
                MCMinBias_high = inverse_cdf_from_hist(h_MCMinBias, 1.0 - q_low)

                if SingleMuon_low is None or SingleMuon_high is None or MinBias_low is None or MinBias_high is None:
                    print(f"  [{q_low:.3f}, {q_high:.3f}] -> undefined")
                else:
                    print(
                        f"  [{q_low:.3f}, {q_high:.3f}] -> "
                        f"Data SingleMuon {SingleMuon_low:.6g} - {SingleMuon_high:.6g}, "
                        f"Data MinBias {MinBias_low:.6g} - {MinBias_high:.6g}"
                    )
                if MCDY_low is None or MCDY_high is None or MCMinBias_low is None or MCMinBias_high is None:
                    print(f"  [{q_low:.3f}, {q_high:.3f}] -> undefined")
                else:
                    print(
                        f"  [{q_low:.3f}, {q_high:.3f}] -> "
                        f"MCDY {MCDY_low:.6g} - {MCDY_high:.6g}, "
                        f"MCMinBias {MCMinBias_low:.6g} - {MCMinBias_high:.6g}"
                    )
                data_missing = SingleMuon_low is None or SingleMuon_high is None or MinBias_low is None or MinBias_high is None
                mc_missing = MCDY_low is None or MCDY_high is None or MCMinBias_low is None or MCMinBias_high is None
                if data_missing and mc_missing:
                    print(f"  [{q_low:.3f}, {q_high:.3f}] -> undefined")
                else:
                    parts = []
                    if not data_missing:
                        parts.append(f"Data SingleMuon {SingleMuon_low:.6g} - {SingleMuon_high:.6g}, Data MinBias {MinBias_low:.6g} - {MinBias_high:.6g}")
                    else:
                        parts.append("Data: undefined")
                    if not mc_missing:
                        parts.append(f"MCDY {MCDY_low:.6g} - {MCDY_high:.6g}, MCMinBias {MCMinBias_low:.6g} - {MCMinBias_high:.6g}")
                    else:
                        parts.append("MC: undefined")
                    print(f"  [{q_low:.3f}, {q_high:.3f}] -> " + "; ".join(parts))

        canvas = ROOT.TCanvas(f"c_ptscan_{var}", "", 800, 700)
        canvas.cd()
        # canvas.SetRightMargin(0.17)
        canvas.SetLeftMargin(0.12)
        canvas.SetLogy()
        canvas.SetGridy(1)

        
        pad1 = ROOT.TPad(f"pad1_{var}", "", 0, 0.32, 1, 1)
        pad1.Draw()
        pad1.cd()
        pad1.SetBottomMargin(0.08)
        # pad1.SetRightMargin(0.17)
        pad1.SetLeftMargin(0.12)
        pad1.SetLogy()
        pad1.SetGridy(1)
        # pad1.SetTicky(0)

        canvas.cd()

        pad2 = ROOT.TPad(f"pad2_{var}", "", 0, 0, 1, 0.37)
        pad2.Draw()
        pad2.cd()
        pad2.SetTopMargin(0.04)
        pad2.SetBottomMargin(0.35)
        # pad2.SetRightMargin(0.17)
        pad2.SetLeftMargin(0.12)
        # pad2.SetLogy()
        pad2.SetGridy(1)
        # pad2.SetTicky(0)

            

       
        legend_col0 = ROOT.TLegend(0.55, 0.82, 0.68, 0.93)
        legend_col0.SetTextSize(0.025)
        legend_col0.SetMargin(0.3)
        legend_col1 = ROOT.TLegend(0.68, 0.85, 0.82, 0.93)
        legend_col1.SetTextSize(0.025)
        legend_col1.SetMargin(0.08)
        dummy = ROOT.TObject()



        legend_col1.AddEntry(dummy, "#bf{DY:}", "")


        for legend in (legend_col0, legend_col1):
            legend.SetBorderSize(0)
            # legend.SetFillStyle(0)

        legend_DataStyle = ROOT.TLine(0.0, 0.0, 0.5, 0.0)
        legend_DataStyle.SetLineColor(ROOT.kBlack)
        legend_DataStyle.SetLineWidth(2)
        legend_DataStyle.SetLineStyle(1)

        legend_MCStyle = ROOT.TLine(0.0, 0.0, 0.5, 0.0)
        legend_MCStyle.SetLineColor(ROOT.kBlack)
        legend_MCStyle.SetLineWidth(2)
        legend_MCStyle.SetLineStyle(2)
        
        histos = []
        ratios_pad2 = []
        plot_max = 0

        for index, pt_cut in enumerate(pt_cuts):
            
            print(f"\n\nProcessing DiMuon pT cut: {pt_cut} GeV...\n")
            

            if pt_cut is None or len(pt_cuts) == 0:

                print(f"\n\nNo DiMuon pT cut specified.\n")
                df_SingleMuon_cut = df_SingleMuon_var
                df_MCDYJets_cut = df_MCDYJets_var

            else:
                print(f"Applying diMuon pT cut: {pt_cut} GeV...")

                df_SingleMuon_cut = DiMuonPtCut(df_SingleMuon_var, pt_cut)
                df_MCDYJets_cut = DiMuonPtCut(df_MCDYJets_var, pt_cut)

            colour = colours[index % len(colours)]

            h_SingleMuon_ptr = MakeHist(df_SingleMuon_cut, var, label, y_title, plot_bins, f"h_SingleMuon_{var}_ptcut{pt_cut}GeV")
            h_SingleMuon = h_SingleMuon_ptr.GetValue()
            h_SingleMuon.SetDirectory(0)
            NormaliseHist(h_SingleMuon, True)

            
            h_SingleMuon.SetStats(0)
            h_SingleMuon.SetLineColor(colour)
            h_SingleMuon.SetLineWidth(2)
            h_SingleMuon.GetXaxis().SetTitle(label)
            h_SingleMuon.GetXaxis().SetTitleOffset(1.4)
            h_SingleMuon.GetYaxis().SetTitle(y_title)
            h_SingleMuon.GetYaxis().SetLabelSize(0.048)
            h_SingleMuon.GetYaxis().SetTitleSize(0.045)
            h_SingleMuon.GetYaxis().SetTitleOffset(1.2)
            h_SingleMuon.GetYaxis().SetNdivisions(10, False)

            h_MinBias.SetLineColor(ROOT.kOrange + 5)
            h_MinBias.SetLineWidth(2)

            histos.append(h_SingleMuon)
            histos.append(h_MinBias)
                

            h_MCDY_ptr = MakeHist(df_MCDYJets_cut, var, label, y_title, plot_bins, f"h_MCDY_{var}_ptcut{pt_cut}GeV")
            h_MCDY = h_MCDY_ptr.GetValue()
            h_MCDY.SetDirectory(0)
            NormaliseHist(h_MCDY, True)

            h_MCDY.SetStats(0)
            h_MCDY.SetLineColor(colour)
            h_MCDY.SetLineWidth(2)
            h_MCDY.SetLineStyle(2)
            h_MCDY.GetXaxis().SetTitle(label)
            h_MCDY.GetXaxis().SetTitleSize(0.03)
            h_MCDY.GetXaxis().SetLabelSize(0.03)
            h_MCDY.GetXaxis().SetTitleOffset(1.4)
            h_MCDY.GetYaxis().SetTitle("Number of Events (normalised)")
            if quantile_reference == "both":
                h_MCDY.GetYaxis().SetLabelSize(0.04)
                h_MCDY.GetYaxis().SetTitleSize(0.04)
            else:
                h_MCDY.GetYaxis().SetLabelSize(0.03)
                h_MCDY.GetYaxis().SetTitleSize(0.03)   
            h_MCDY.GetYaxis().SetNdivisions(10, False)

            histos.append(h_MCDY)
            histos.append(h_MCMinBias)
            h_MCMinBias.SetLineColor(ROOT.kOrange + 5)
            h_MCMinBias.SetLineWidth(2)
            h_MCMinBias.SetLineStyle(2)      
               

            pad1.cd()
            

            ymax = max(h_SingleMuon.GetMaximum(), h_MCDY.GetMaximum()) * 1.4
            ymin = min(h_SingleMuon.GetMinimum(), h_MCDY.GetMinimum()) * 0.8

            if index == 0:
                h_SingleMuon.Draw("hist e")
            else:
                h_SingleMuon.Draw("hist e same")
            h_MinBias.Draw("hist e same")
            h_MCDY.Draw("hist e same")
            h_MCMinBias.Draw("hist e same")


            
            if pt_cut is None or len(pt_cuts) == 0:
                legend_col1.AddEntry(dummy, f"#color[{colour}]{{#bf{{ No p^{{#mu#mu}}_{{T}} cut}}}}", "")
            else:
                legend_col1.AddEntry(dummy, f"  #color[{colour}]{{#bf{{p^{{#mu#mu}}_{{T}} < {int(pt_cut)} GeV}}}}", "")

            max_val = h_SingleMuon.GetBinContent(h_SingleMuon.GetMaximumBin())
            if plot_max < max_val:
                plot_max = max_val

            max_val = h_MCDY.GetBinContent(h_MCDY.GetMaximumBin())
            if plot_max < max_val:
                plot_max = max_val

            ratio = h_SingleMuon.Clone(f"ratio_{var}_{pt_cut}GeV_{index}")
            ratio.Divide(h_MinBias)
            ratio.SetDirectory(0)
            ratio.SetStats(0)
            ratio.SetLineColor(colour)
            ratio.SetMarkerColor(colour)
            ratio.SetMarkerStyle(20)
            ratio.SetMarkerSize(0.6)
            ratio.GetYaxis().SetTitle("DY/MinBias")
            ratio.GetXaxis().SetTitle(label)
            ratio.GetXaxis().SetTitleSize(0.08)
            ratio.GetXaxis().SetTitleOffset(1.3)
            ratio.GetXaxis().SetLabelSize(0.075)
            ratio.GetXaxis().SetTickLength(0.07)
            ratio.GetYaxis().SetTitleSize(0.08)
            ratio.GetYaxis().SetLabelSize(0.075)
            ratio.GetYaxis().SetTitleOffset(0.55)
            ratios_pad2.append(ratio)
            ratio.GetYaxis().SetNdivisions(505)
            ratio.GetYaxis().SetRangeUser(ratio.GetMinimum(), ratio.GetMaximum() * 1.2)
            canvas.cd()
            pad2.cd()
            ratio.Draw("pe") if index == 0 else ratio.Draw("pe same")

            ratioMC = h_MCDY.Clone(f"ratio_{var}_{pt_cut}GeV_{index}")
            ratioMC.Divide(h_MCMinBias)
            ratioMC.SetDirectory(0)
            ratioMC.SetStats(0)
            ratioMC.SetLineColor(colour - 2)
            ratioMC.SetLineWidth(2)
            ratioMC.SetLineStyle(2)
            ratioMC.SetMarkerColor(colour - 2)
            ratioMC.SetMarkerStyle(20)
            ratioMC.SetMarkerSize(0.6)
            ratioMC.GetYaxis().SetTitle("DY/MinBias")
            ratioMC.GetXaxis().SetTitle(label)
            ratioMC.GetXaxis().SetTitleSize(0.08)
            ratioMC.GetXaxis().SetTitleOffset(1.3)
            ratioMC.GetXaxis().SetLabelSize(0.075)
            ratioMC.GetXaxis().SetTickLength(0.07)
            ratioMC.GetYaxis().SetTitleSize(0.08)
            ratioMC.GetYaxis().SetLabelSize(0.075)
            ratioMC.GetYaxis().SetTitleOffset(0.55)
            ratios_pad2.append(ratioMC)
            ratioMC.GetYaxis().SetNdivisions(505)
            ratioMC.Draw("hist e same")

            print(f"Finished processing diMuon pT cut: {pt_cut} GeV!\n")
  
        ymin_ratio = (min(ratioMC.GetMinimum() for ratioMC in ratios_pad2) if ratios_pad2 else 1) * 0.8
        ymax_ratio = (max(ratioMC.GetMaximum() for ratioMC in ratios_pad2) if ratios_pad2 else 1)
        

        ratios_pad2[0].GetYaxis().SetRangeUser(ymin_ratio, ymax_ratio) if ratios_pad2 else None

        canvas.cd()
        if histos and plot_max > 0:
            histos[0].SetMaximum(plot_max * 2)
        legend_col0.AddEntry(legend_DataStyle, "Data", "l")
        legend_col0.AddEntry(legend_MCStyle, "MC", "l")

        canvas.cd()
        legend_col1.Draw()
        legend_col0.AddEntry(dummy, f"#color[{ROOT.kOrange + 5}]{{#bf{{MinBias}}}}", "")
        legend_col0.Draw()

        inset = ROOT.TPad(f"inset_{var}", f"inset_{var}", 0.3, 0.36, 0.9, 0.8)
        inset.SetLogy()
        inset.SetFillStyle(0)
        inset.SetBorderSize(1)
        inset.SetRightMargin(0.05)
        inset.SetTopMargin(0.08)
        inset.SetBottomMargin(0.12)
        inset.Draw()
        inset.cd()

        inset.cd()
        histos[0].SetMaximum(plot_max * 2)

        max_bin = ratios_pad2[0].GetMaximumBin()
        zoom_xmax = ratios_pad2[0].GetBinLowEdge(max_bin) + 0.01 * ratios_pad2[0].GetBinWidth(max_bin)
        print(f"Zooming in on x-axis range: 0 to {zoom_xmax:.3f}")

        frame = inset.DrawFrame(0,
                min(histos[0].GetMinimum(), histos[1].GetMinimum(), histos[2].GetMinimum(), histos[3].GetMinimum()) * 0.8, 
                zoom_xmax,
                max(histos[0].GetMaximum(), histos[1].GetMaximum(), histos[2].GetMaximum(), histos[3].GetMaximum()) * 1.5
            )
        frame.GetXaxis().SetLabelSize(0.05)
        frame.GetYaxis().SetLabelSize(0.05)
        frame.GetXaxis().SetTitleSize(0.05)
        frame.GetYaxis().SetTitleSize(0.05)
        frame.GetYaxis().SetNdivisions(10, False)
        inset.SetGridy(1)
        inset.SetTicky(0)

        for hh in histos:
            hh.SetStats(0)
            hh.GetXaxis().SetRangeUser(0, zoom_xmax)
            hh.Draw("hist e same")
        
        
        # ratio inset plot
    
        canvas.cd()

        inset_ratio = ROOT.TPad(f"inset_ratio_{var}", f"inset_ratio_{var}", 0.5, 0.145, 1, 0.365)
        # inset_ratio.SetLogy()
        inset_ratio.SetGridy()
        inset_ratio.SetFillStyle(0)
        inset_ratio.SetBorderSize(1)
        inset_ratio.Draw()
        inset_ratio.cd()

        # inset_ratio.DrawFrame(0, 10**(-1), zoom_xmax, 100)

        frame_ratio = inset_ratio.DrawFrame(0, ymin_ratio, zoom_xmax, ymax_ratio * 0.8)
        frame_ratio.GetXaxis().SetLabelSize(0.07)
        frame_ratio.GetYaxis().SetLabelSize(0.07)
        frame_ratio.GetXaxis().SetTitleSize(0.07)
        frame_ratio.GetYaxis().SetTitleSize(0.07)
        frame_ratio.GetXaxis().SetTitle("")
        frame_ratio.GetYaxis().SetTitle("")
        frame_ratio.GetXaxis().SetRangeUser(0, zoom_xmax)
        inset_ratio.SetGridy(1)
        inset_ratio.SetTicky(0)
        frame_ratio.GetYaxis().SetNdivisions(505)
        
        

        inset_ratios = []

        for i, h_ratio in enumerate(ratios_pad2):
            h_ratio = h_ratio.Clone(h_ratio.GetName() + "_insetratio")
            h_ratio.SetStats(0)
            h_ratio.SetLineWidth(2)
            h_ratio.GetXaxis().SetTitleSize(0)
            h_ratio.GetYaxis().SetTitleSize(0)
            # h_ratio.GetXaxis().SetLabelSize(0)
            h_ratio.GetXaxis().SetRangeUser(0, zoom_xmax)
            inset_ratios.append(h_ratio)
            h_ratio.Draw("pe same")
        
        legend_mass = ROOT.TLegend(0.36, 0.83, 0.52, 0.89)
        legend_mass.SetBorderSize(0)
        # legend_mass.SetFillStyle(0)
        legend_mass.SetTextSize(0.027)
        legend_mass.SetMargin(0)
        legend_mass.AddEntry(dummy, " 86 GeV < m_{#mu#mu} < 96 GeV", "")

        canvas.cd()
        pad1.cd()

        legend_mass.Draw()


        output_name = f"new_plots/{var}_pTscan_QuantileBinning{out_suffix}.pdf"
            
        canvas.SaveAs(output_name)
        canvas.Close()

def QuantilePerObservable(df_SingleMuon_var, df_MinBias_var, df_MCDYJets_var, df_MCMinBias_var, variables, out_suffix,bins, b_bins, pt_cuts, binweight):

    quantile_bins = array.array("d", bins)


    if b_bins is None:
        # b_bins = array.array("d", np.linspace(0, 1, 50))
        b_bins = array.array("d", np.concatenate([
                                  np.arange(0.00, 0.10, 0.01),
                                  np.arange(0.10, 0.20, 0.01),
                                  np.arange(0.20, 1.05, 0.05)
                                ])
                            )
    else:
        b_bins = array.array("d", b_bins)

    dataframes = [df_SingleMuon_var, df_MinBias_var, df_MCDYJets_var, df_MCMinBias_var]


    print(f"Bin weight: {binweight}")




    pt_cuts = parse_pt_cuts(pt_cuts)

    colours = [ROOT.kViolet - 6, ROOT.kBlue - 4, ROOT.kGreen + 3, ROOT.kOrange + 5, ROOT.kRed + 1]


    for var in variables:

        if var in ["PFCands_pt", "PFCands_eta", "PFCands_phi", "PFCands_pvAssocQuality"]:
            continue

      
        label = VARIABLES[var]
        binning = BINNING[var]
        y_title = "Cumulative Distribution Function (CDF)"

        
        canvas = ROOT.TCanvas(f"c_quantile_{var}", "", 1000, 800)
        canvas.cd()
        canvas.SetBottomMargin(0.13)
        canvas.SetLogy()

        pad1 = ROOT.TPad("pad1", "pad1", 0, 0.5, 1, 1)
        pad1.Draw()
        pad1.cd()
        pad1.SetBottomMargin(0.17)
        pad1.SetTopMargin(0.05)
        # pad1.SetRightMargin(0)
        # pad1.SetLeftMargin(0.12)
        pad1.SetGridy()
        # pad1.SetLogy()


        canvas.cd()

        pad2 = ROOT.TPad("pad2", "pad2", 0, 0, 1, 0.5)
        pad2.Draw()
        pad2.cd()
        pad2.SetTopMargin(0.05)
        pad2.SetBottomMargin(0.17)
        # pad2.SetLeftMargin(0)
        pad2.SetGridy()
        # pad2.SetLogy()

        legend_var = ROOT.TLegend(0.52, 0.73, 0.73, 0.92)
        legend_DataMC = ROOT.TLegend(0.73, 0.65, 0.89, 0.92)
        
        legend_var.SetMargin(0.05)
        legend_DataMC.SetMargin(0.25)


        for legend in [legend_DataMC, legend_var]:
            legend.SetBorderSize(0)
            # legend.SetFillStyle(0)
            legend.SetTextSize(0.05)

    
        dummy = ROOT.TObject()
        dummyData = ROOT.TLine()
        dummyData.SetLineColor(ROOT.kBlack)
        dummyData.SetLineWidth(2)
        dummyMC = ROOT.TLine()
        dummyMC.SetLineColor(ROOT.kBlack)
        dummyMC.SetLineWidth(2)
        dummyMC.SetLineStyle(2)            
        legend_DataMC.AddEntry(dummyData, f"#color[{ROOT.kBlack}]{{#bf{{Data}}}}", "l")
        legend_DataMC.AddEntry(dummyMC, f"#color[{ROOT.kBlack}]{{#bf{{MC}}}}", "l")
        legend_DataMC.AddEntry(dummy, f"#color[{ROOT.kViolet - 6}]{{#bf{{DY}}}}", "")
        legend_DataMC.AddEntry(dummy, f"#color[{ROOT.kOrange + 5}]{{#bf{{MinBias}}}}", "")


        legend_var.AddEntry(dummy, label, "")
        legend_var.AddEntry(dummy, f"#color[{ROOT.kBlack}]{{86 GeV < m_{{#mu#mu}} < 96 GeV}}", "")



        canvas.cd()
        pad1.cd()

        q_column = f"{var}_InvQ"
        plot_xlabel = f"q = 1 - F_{{MB}}({label})"
        b_column = f"{var}_b"
        # plot_xlabel = "impact parameter b"

        BuildQuantile(df_MinBias_var, var, "MB")
        BuildQuantile(df_MCMinBias_var, var, "MCMB")

        df_MinBias_q = ApplyQuantileAndIP(df_MinBias_var, var, "MB")
        df_MCMinBias_q = ApplyQuantileAndIP(df_MCMinBias_var, var, "MCMB")

        # df_MinBias_q.Display([f"{var}_InvQ", f"{var}_b"], 20).Print()


        # quantile plots
        h_MinBias_ptr = df_MinBias_q.Histo1D(
            (f"h_MinBias_{var}_quantile", f"; {plot_xlabel}; {y_title}", len(quantile_bins) - 1, quantile_bins),
            q_column,
        )
        h_MCMinBias_ptr = df_MCMinBias_q.Histo1D(
            (f"h_MCMinBias_{var}_quantile", f"; {plot_xlabel}; {y_title}", len(quantile_bins) - 1, quantile_bins),
            q_column,
        )

        h_MinBias = h_MinBias_ptr.GetValue()
        h_MCMinBias = h_MCMinBias_ptr.GetValue()

        NormaliseHist(h_MinBias, binweight)
        NormaliseHist(h_MCMinBias, binweight)

        h_MinBias.SetStats(0)
        h_MinBias.SetLineColor(ROOT.kOrange + 5)
        h_MinBias.SetLineWidth(2)
        h_MinBias.GetXaxis().SetTitle(plot_xlabel)
        h_MinBias.GetXaxis().SetTitleSize(0.05)
        h_MinBias.GetXaxis().SetLabelSize(0.05)
        h_MinBias.GetXaxis().SetTitleOffset(1.2)
        if binweight:
            h_MinBias.GetYaxis().SetTitle("Density #frac{1}{N} #frac{dN}{dq} (normalised)")
        else:
            h_MinBias.GetYaxis().SetTitle("Number of Events (normalised)")
        h_MinBias.GetYaxis().SetTitleSize(0.05)
        h_MinBias.GetYaxis().SetLabelSize(0.05)
        h_MinBias.GetYaxis().SetTitleOffset(0.8)


        h_MCMinBias.SetStats(0)
        h_MCMinBias.SetLineColor(ROOT.kOrange + 5)
        h_MCMinBias.SetLineWidth(2)
        h_MCMinBias.SetLineStyle(2)

        h_MinBias.Draw("hist e")
        h_MCMinBias.Draw("hist e same")


        # impact parameter plots
        h_MinBias_b_ptr = df_MinBias_q.Histo1D((f"h_MinBias_{var}_b", ";impact parameter b;Normalised density", len(b_bins) - 1, b_bins), b_column)
        h_MCMinBias_b_ptr = df_MCMinBias_q.Histo1D((f"h_MCMinBias_{var}_b", ";impact parameter b;Normalised density", len(b_bins) - 1, b_bins), b_column)

        h_MinBias_b = h_MinBias_b_ptr.GetValue()
        h_MCMinBias_b = h_MCMinBias_b_ptr.GetValue()

        NormaliseHist(h_MinBias_b, binweight)
        NormaliseHist(h_MCMinBias_b, binweight)

        canvas.cd()
        pad2.cd()

        h_MinBias_b.SetStats(0)
        h_MinBias_b.SetLineColor(ROOT.kOrange + 5)
        h_MinBias_b.SetLineWidth(2)
        h_MinBias_b.GetXaxis().SetTitle("impact parameter b")
        h_MinBias_b.GetXaxis().SetTitleSize(0.05)
        h_MinBias_b.GetXaxis().SetLabelSize(0.05)
        h_MinBias_b.GetXaxis().SetTitleOffset(1.2)
        if binweight:
            h_MinBias_b.GetYaxis().SetTitle("Density #frac{1}{N} #frac{dN}{db} (normalised)")
        else:
            h_MinBias_b.GetYaxis().SetTitle("Number of Events (normalised)")
        h_MinBias_b.GetYaxis().SetTitleSize(0.05)
        h_MinBias_b.GetYaxis().SetLabelSize(0.05)
        h_MinBias_b.GetYaxis().SetTitleOffset(0.8)
        # h_MinBias_b.GetXaxis().SetRangeUser(0, 2)


        h_MCMinBias_b.SetStats(0)
        h_MCMinBias_b.SetLineColor(ROOT.kOrange + 5)
        h_MCMinBias_b.SetLineWidth(2)
        h_MCMinBias_b.SetLineStyle(2)



        h_MinBias_b.Draw("hist e")
        h_MCMinBias_b.Draw("hist e same")


        


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

        
            colour = colours[index % len(colours)]

        
            h_SingleMuon_ptr = df_SingleMuon_q.Histo1D(
                (f"h_SingleMuon_{var}_quantile_{pt_cut}GeVCut", f"; {plot_xlabel}; {y_title}", len(quantile_bins) - 1, quantile_bins),
                q_column,
            )
            h_MCDYJets_ptr = df_MCDYJets_q.Histo1D(
                (f"h_MCDYJets_{var}_quantile_{pt_cut}GeVCut", f"; {plot_xlabel}; {y_title}", len(quantile_bins) - 1, quantile_bins),
                q_column,
            )

           

            h_SingleMuon = h_SingleMuon_ptr.GetValue()
            h_MCDYJets = h_MCDYJets_ptr.GetValue()


            NormaliseHist(h_SingleMuon, binweight)
            NormaliseHist(h_MCDYJets, binweight)

            pad1.cd()
            
            h_SingleMuon.SetLineColor(ROOT.kViolet - 6)
            h_SingleMuon.SetMarkerColor(ROOT.kViolet - 6)
            h_SingleMuon.SetLineWidth(2)
            # h_SingleMuon.GetXaxis().SetRangeUser(0, 2)

            h_MCDYJets.SetLineColor(ROOT.kViolet - 6)
            h_MCDYJets.SetMarkerColor(ROOT.kViolet - 6)
            h_MCDYJets.SetLineWidth(2)
            h_MCDYJets.SetLineStyle(2)
            # h_MCDYJets.GetXaxis().SetRangeUser(0, 2)

     

            h_MinBias.GetYaxis().SetRangeUser(0, max(h_SingleMuon.GetMaximum(), h_MinBias.GetMaximum(), h_MCDYJets.GetMaximum(), h_MCMinBias.GetMaximum()) * 1.2)

            h_SingleMuon.Draw("hist e same")
            h_MCDYJets.Draw("hist e same")


            canvas.cd()
            pad2.cd()

           

            h_SingleMuon_b_ptr = df_SingleMuon_q.Histo1D((f"h_SingleMuon_{var}_b", ";impact parameter b;Normalised density", len(b_bins) - 1, b_bins), b_column)

            h_MCDYJets_b_ptr = df_MCDYJets_q.Histo1D((f"h_MCDYJets_{var}_b", ";impact parameter b;Normalised density", len(b_bins) - 1, b_bins), b_column)

            h_SingleMuon_b = h_SingleMuon_b_ptr.GetValue()
            h_MCDYJets_b = h_MCDYJets_b_ptr.GetValue()



            NormaliseHist(h_SingleMuon_b, binweight)
            NormaliseHist(h_MCDYJets_b, binweight)


            h_SingleMuon_b.SetStats(0)
            h_SingleMuon_b.SetLineColor(colour)
            h_SingleMuon_b.SetMarkerColor(colour)
            h_SingleMuon_b.SetLineWidth(2)

    
            h_MCDYJets_b.SetStats(0)
            h_MCDYJets_b.SetLineColor(colour)
            h_MCDYJets_b.SetMarkerColor(colour)
            h_MCDYJets_b.SetLineWidth(2)
            h_MCDYJets_b.SetLineStyle(2)


            h_MinBias_b.GetYaxis().SetRangeUser(0, max(h_SingleMuon_b.GetMaximum(), h_MinBias_b.GetMaximum(), h_MCDYJets_b.GetMaximum(), h_MCMinBias_b.GetMaximum()) * 2)


            h_SingleMuon_b.Draw("hist e same")
            h_MCDYJets_b.Draw("hist e same")

            canvas.cd()
            pad1.cd()


    
            if pt_cut is None or len(pt_cuts) == 0:
                legend_var.AddEntry(dummy, f"#color[{ROOT.kBlack}]{{No p^{{#mu#mu}}_{{T}} cut}}", "")
            else:
                legend_var.AddEntry(dummy, f"#color[{ROOT.kBlack}]{{p^{{#mu#mu}}_{{T}} < {pt_cut} GeV}}", "")



            legend_DataMC.Draw()
            legend_var.Draw()


            canvas.cd()
            pad2.cd()

            legend_var_pad2 = ROOT.TLegend(0.125, 0.73, 0.335, 0.92)
            legend_DataMC_pad2 = ROOT.TLegend(0.335, 0.65, 0.495, 0.92)

            CopyLegend(legend_var, legend_var_pad2)
            CopyLegend(legend_DataMC, legend_DataMC_pad2)

            for entry in list(legend_DataMC_pad2.GetListOfPrimitives()):
                print(entry.GetLabel())
                if entry.GetLabel() == "#color[805]{#bf{MinBias}}":
                    legend_DataMC_pad2.GetListOfPrimitives().Remove(entry)



            legend_DataMC_pad2.AddEntry(dummy, f"#color[{ROOT.kOrange + 5}]{{#bf{{MinBias}}}}", "")
            # legend_DataMC_pad2.AddEntry(dummy, f"#color[{ROOT.kGreen + 3}]{{#bf{{MinBias eTe}}}}", "")


            legend_DataMC_pad2.Draw()
            legend_var_pad2.Draw()

        output_dir = f"new_plots/quantile_binning/{bins}"
        os.makedirs(output_dir, exist_ok=True)

        if pt_cut is None or len(pt_cuts) == 0:
            output_name = f"{output_dir}/{var}_Quantile_NoZPtCut{out_suffix}.pdf"
        else:
            output_name = f"{output_dir}/{var}_Quantile_{pt_cut}GeVZPtCut{out_suffix}.pdf"

        canvas.SaveAs(output_name)

        canvas.Close()

def DYMinBiasPerObservableRatio(df_SingleMuon_var, df_MinBias_var, df_MCDYJets_var, df_MCMinBias_var, variables, out_suffix, bins, b_bins, pt_cuts, binweight):

    quantile_bins = array.array("d", bins)


    if b_bins is None:
        # b_bins = array.array("d", np.linspace(0, 1, 50))
        b_bins = array.array("d", np.concatenate([
                                  np.arange(0.00, 0.10, 0.01),
                                  np.arange(0.10, 0.20, 0.01),
                                  np.arange(0.20, 1.05, 0.05)
                                ])
                            )
    else:
        b_bins = array.array("d", b_bins)



    print(f"Bin weight: {binweight}")





    pt_cuts = parse_pt_cuts(pt_cuts)

    colours = [ROOT.kViolet - 6, ROOT.kOrange + 5, ROOT.kBlue - 4, ROOT.kGreen + 3, ROOT.kRed + 1]

    for var in variables:
        if var in ["PFCands_pt", "PFCands_eta", "PFCands_phi", "PFCands_pvAssocQuality"]:
            continue
    
        label = VARIABLES[var]
        binning = BINNING[var]
        y_title = "Cumulative Distribution Function (CDF)"

    


        canvas = ROOT.TCanvas(f"c_quantile_{var}", "", 1000, 800)
        canvas.cd()
        canvas.SetBottomMargin(0.13)
        canvas.SetLogy()

        pad1 = ROOT.TPad("pad1", "pad1", 0, 0.5, 1, 1)
        pad1.Draw()
        pad1.cd()
        pad1.SetBottomMargin(0.17)
        pad1.SetTopMargin(0.05)
        # pad1.SetRightMargin(0)
        # pad1.SetLeftMargin(0.12)
        pad1.SetGridy()
        # pad1.SetLogy()


        canvas.cd()

        pad2 = ROOT.TPad("pad2", "pad2", 0, 0, 1, 0.5)
        pad2.Draw()
        pad2.cd()
        pad2.SetTopMargin(0.05)
        pad2.SetBottomMargin(0.17)
        # pad2.SetLeftMargin(0)
        pad2.SetGridy()
        # pad2.SetLogy()

        canvas.cd()
        pad1.cd()

        legend_var = ROOT.TLegend(0.56, 0.73, 0.77, 0.92)
        legend_DataMC = ROOT.TLegend(0.77, 0.65, 0.89, 0.92)

        legend_var.SetMargin(0.05)
        legend_DataMC.SetMargin(0.32)


        for legend in [legend_DataMC, legend_var]:
            legend.SetBorderSize(0)
            # legend.SetFillStyle(0)
            legend.SetTextSize(0.05)

    
        dummy = ROOT.TObject()
        dummyData = ROOT.TLine()
        dummyData.SetLineColor(ROOT.kBlack)
        dummyData.SetLineWidth(2)
        dummyMC = ROOT.TLine()
        dummyMC.SetLineColor(ROOT.kBlack)
        dummyMC.SetLineWidth(2)
        dummyMC.SetLineStyle(2)
        legend_DataMC.SetHeader("#bf{DY/MinBias:}", "L")


        legend_var.AddEntry(dummy, label, "")
        legend_var.AddEntry(dummy, f"#color[{ROOT.kBlack}]{{86 GeV < m_{{#mu#mu}} < 96 GeV}}", "")



        q_column = f"{var}_InvQ"
        plot_xlabel = f"q = 1 - F_{{MB}}({label})"
        # plot_xlabel = "impact parameter b"
        b_column = f"{var}_b"




        BuildQuantile(df_MinBias_var, var, "MB")
        BuildQuantile(df_MCMinBias_var, var, "MCMB")
        
        df_MinBias_q = ApplyQuantileAndIP(df_MinBias_var, var, "MB")
        df_MCMinBias_q = ApplyQuantileAndIP(df_MCMinBias_var, var, "MCMB")

        h_MinBias_ptr = df_MinBias_q.Histo1D(
                (f"h_MinBias_{var}_quantile", f"; {plot_xlabel}; {y_title}", len(quantile_bins) - 1, quantile_bins),
                q_column,
            )
        h_MCMinBias_ptr = df_MCMinBias_q.Histo1D(
                (f"h_MCMinBias_{var}_quantile", f"; {plot_xlabel}; {y_title}", len(quantile_bins) - 1, quantile_bins),
                q_column,
            )

        h_MinBias = h_MinBias_ptr.GetValue()
        h_MCMinBias = h_MCMinBias_ptr.GetValue()
 

        NormaliseHist(h_MinBias, binweight)
        NormaliseHist(h_MCMinBias, binweight)

        h_MinBias.SetStats(0)
        h_MinBias.SetLineColor(ROOT.kViolet - 6)
        h_MinBias.SetLineWidth(2)
        h_MinBias.GetXaxis().SetTitle(plot_xlabel)
        h_MinBias.GetXaxis().SetTitleSize(0.05)
        h_MinBias.GetXaxis().SetLabelSize(0.05)
        h_MinBias.GetXaxis().SetTitleOffset(1.2)
        if binweight:
            h_MinBias.GetYaxis().SetTitle("Density #frac{1}{N} #frac{dN}{dq} (normalised)")
        else:
            h_MinBias.GetYaxis().SetTitle("Number of Events (normalised)")
        h_MinBias.GetYaxis().SetTitleSize(0.05)
        h_MinBias.GetYaxis().SetLabelSize(0.05)
        h_MinBias.GetYaxis().SetTitleOffset(0.8)


        h_MCMinBias.SetStats(0)
        h_MCMinBias.SetLineColor(ROOT.kViolet - 6)
        h_MCMinBias.SetLineWidth(2)
        h_MCMinBias.SetLineStyle(2)

        legend_DataMC.AddEntry(h_MinBias, f"#bf{{Data}}", "l")
        legend_DataMC.AddEntry(h_MCMinBias, f"#bf{{MC}}", "l")

       
        # pad2_edges = array.array("d", edges)
        # row_edges = array.array("d", row_edges)

        # row_edges = array.array("d", [0, np.float64(0.06771917820510076), np.float64(0.095769380250414), np.float64(0.11729305729804548), np.float64(0.13543197247597957), np.float64(0.1514132657568233), np.float64(0.1658670074002681), np.float64(0.1791536268746254), np.float64(0.1915252179716987), np.float64(0.20314476664654912), np.float64(0.21413473168231043), np.float64(0.22458755622124144), np.float64(0.23457137141569767), np.float64(0.24415080459547), np.float64(0.25336831388591113), np.float64(0.2622620627886614), np.float64(0.27086075289080863), np.float64(0.27919474446161696), np.float64(0.28729008411666734), np.float64(0.29516055005737757), np.float64(0.30282938663040593), np.float64(0.31030875673065056), np.float64(0.31760932351260407), np.float64(0.32474847109556676), np.float64(0.3317340148005362), np.float64(0.3385729086239687), np.float64(0.34527887504286797), np.float64(0.3518570571235465), np.float64(0.35831449279148175), np.float64(0.36465522568973113), np.float64(0.3708922349388906), np.float64(0.3770214951649005), np.float64(0.3830526931047334), np.float64(0.38899039007821384), np.float64(0.39484099416090923), np.float64(0.4006061629165849), np.float64(0.4062895332930982), np.float64(0.41189239218749285), np.float64(0.41742212428033765), np.float64(0.4228775091171456), np.float64(0.4282654256578457), np.float64(0.43358639497875157), np.float64(0.43884285229161946), np.float64(0.4440351414987963), np.float64(0.4491693377587458), np.float64(0.4542455074950158), np.float64(0.45926369218327756), np.float64(0.4642294971827949), np.float64(0.46914274283139534), np.float64(0.4740087116128389), np.float64(0.4788162049539999), np.float64(0.4835830584725723), np.float64(0.4882998385419549), np.float64(0.492971490249194), np.float64(0.49759928464269626), np.float64(0.5021861558960953), np.float64(0.5067298028062975), np.float64(0.5112347603096676), np.float64(0.5157003657606397), np.float64(0.5201259704379984), np.float64(0.5245158836687824), np.float64(0.5288693594051539), np.float64(0.5331856685958746), np.float64(0.5374705326910176), np.float64(0.5417215057816172), np.float64(0.5459362121207153), np.float64(0.5501186286457918), np.float64(0.5542694863164835), np.float64(0.5583910373191109), np.float64(0.5624808516178347), np.float64(0.5665411426499725), np.float64(0.5705740560277086), np.float64(0.5745786634645293), np.float64(0.5785540583101089), np.float64(0.5825038072698504), np.float64(0.5864284285392442), np.float64(0.5903254940249333), np.float64(0.5941970009959288), np.float64(0.5980420000894316), np.float64(0.601863872456008), np.float64(0.6056616283573825), np.float64(0.6094357186457734), np.float64(0.6131837602394081), np.float64(0.6169104324776424), np.float64(0.6206161203163563), np.float64(0.6242984275768584), np.float64(0.627960519277854), np.float64(0.6316013781401101), np.float64(0.6352213692605598), np.float64(0.6388222008355665), np.float64(0.642401503249464), np.float64(0.645963649836947), np.float64(0.649504929331415), np.float64(0.653023033197035), np.float64(0.656523601833375), np.float64(0.6600056042509638), np.float64(0.6634693327660983), np.float64(0.6669176649603968), np.float64(0.6703443894717683), np.float64(0.6737524025470819), np.float64(0.677143263556282), np.float64(0.6805197699244779), np.float64(0.6838770771854776), np.float64(0.6872230154868856), np.float64(0.6905539939413767), np.float64(0.6938689819280623), np.float64(0.69716820754778), np.float64(0.700449424806787), np.float64(0.7037165715167543), np.float64(0.7069673967900283), np.float64(0.7102033421639492), np.float64(0.7134209743640362), np.float64(0.7166241595873099), np.float64(0.7198154930137515), np.float64(0.7229927398397871), np.float64(0.7261596569588128), np.float64(0.7293104513794623), np.float64(0.7324476920491245), np.float64(0.7355703769636873), np.float64(0.7386810316796251), np.float64(0.7417763107725434), np.float64(0.744862209766653), np.float64(0.7479330647971604), np.float64(0.750991362996463), np.float64(0.7540384037912521), np.float64(0.7570720390230188), np.float64(0.760094704209446), np.float64(0.7631042636793856), np.float64(0.7661031290514557), np.float64(0.7690891770275039), np.float64(0.772065915926859), np.float64(0.775030106275075), np.float64(0.7779818915059437), np.float64(0.7809236266165469), np.float64(0.7838543217363251), np.float64(0.786771902373721), np.float64(0.7896819883218182), np.float64(0.7925792077504382), np.float64(0.7954669620135625), np.float64(0.7983442708204654), np.float64(0.8012112467062821), np.float64(0.8040680001998644), np.float64(0.8069146398735019), np.float64(0.8097512723910703), np.float64(0.8125790665861962), np.float64(0.8153949333497883), np.float64(0.8182011092701583), np.float64(0.8209987468368584), np.float64(0.8237858339314312), np.float64(0.8265635233087143), np.float64(0.8293329519326298), np.float64(0.8320931632083416), np.float64(0.8348463198646578), np.float64(0.8375873301751731), np.float64(0.8403183708155048), np.float64(0.8430426154274755), np.float64(0.8457570628172195), np.float64(0.8484638450764913), np.float64(0.8511620195349171), np.float64(0.8538516677945489), np.float64(0.8565338796046945), np.float64(0.8592046994580039), np.float64(0.8618682459918864), np.float64(0.8645245864322801), np.float64(0.8671737870006458), np.float64(0.8698109428506454), np.float64(0.8724450824185024), np.float64(0.8750693166446882), np.float64(0.8776866896838177), np.float64(0.8802952983771481), np.float64(0.8828981582710494), np.float64(0.8854904379815871), np.float64(0.8880790451917464), np.float64(0.8906669241580049), np.float64(0.8933334481053092), np.float64(0.8958964988214294), np.float64(0.8984541625113627), np.float64(0.9010026466280597), np.float64(0.9035468133874577), np.float64(0.9060809737983706), np.float64(0.9086099694659432), np.float64(0.9111290986964), np.float64(0.913643174771448), np.float64(0.9161522392912171), np.float64(0.9187429166182601), np.float64(0.921234337568156), np.float64(0.9237209107894958), np.float64(0.9262054758187966), np.float64(0.9286778077102401), np.float64(0.9311445037418382), np.float64(0.9336046824881347), np.float64(0.9360685556522516), np.float64(0.9385499125115474), np.float64(0.9409898115134975), np.float64(0.9434234004247413), np.float64(0.9458507279511688), np.float64(0.9482736657206371), np.float64(0.9506940661991125), np.float64(0.9531110415729309), np.float64(0.9556259559796053), np.float64(0.958095465768445), np.float64(0.9604857149499038), np.float64(0.9628808058840664), np.float64(0.965292346657803), np.float64(0.9677371896854264), np.float64(0.9701036828076787), np.float64(0.9724661952636298), np.float64(0.9749107851910783), np.float64(0.977263446084068), np.float64(0.9796157523909592), np.float64(0.9820557513498427), np.float64(0.9845037545280869), np.float64(0.986837926278644), np.float64(0.9891665900160443), np.float64(0.9914958887431353), np.float64(0.9939171617603181), np.float64(0.9962700676858399), np.float64(0.9986537929948627), np.float64(1.0009558319643395), np.float64(1.0032534505508477), np.float64(1.005550978245815), np.float64(1.0078278264314433), np.float64(1.010103822237967), np.float64(1.0123755552601694), np.float64(1.0146396455992812), np.float64(1.0169012457512383), np.float64(1.019267259342583), np.float64(1.0215346955954112), np.float64(1.0240926467217102), np.float64(1.0263923847844072), np.float64(1.0286390720610987), np.float64(1.030883379075005), np.float64(1.0332843176393431), np.float64(1.0355193918899575), np.float64(1.037742153868499), np.float64(1.0401305853667524), np.float64(1.043252234541546), np.float64(1.0454618638118092), np.float64(1.0477955671591244), np.float64(1.049989871302913), np.float64(1.0524154098021752)])

        row_edges = array.array("d", bins)

        h_MinBias_b_ptr = df_MinBias_q.Histo1D(
                                                (
                                                    f"h_MinBias_{var}_b",
                                                    ";impact parameter b;Normalised density",
                                                    # len(pad2_edges) - 1, pad2_edges
                                                    # 50, 0, 1
                                                    len(b_bins) - 1, b_bins
                                                ),
                                                b_column,
                                            )

        h_MCMinBias_b_ptr = df_MCMinBias_q.Histo1D(
                                                    (
                                                        f"h_MCMinBias_{var}_b",
                                                        ";impact parameter b;Normalised density",
                                                        # len(pad2_edges) - 1, pad2_edges
                                                        # 50, 0, 1
                                                        len(b_bins) - 1, b_bins
                                                    ),
                                                    b_column,
                                                )

  

        h_MinBias_b = h_MinBias_b_ptr.GetValue()
        h_MCMinBias_b = h_MCMinBias_b_ptr.GetValue()

        NormaliseHist(h_MinBias_b, binweight)
        NormaliseHist(h_MCMinBias_b, binweight)

        canvas.cd()
        pad2.cd()

        h_MinBias_b.SetStats(0)
        h_MinBias_b.SetLineColor(ROOT.kViolet - 6)
        h_MinBias_b.SetLineWidth(2)
        h_MinBias_b.GetXaxis().SetTitle("impact parameter b")
        h_MinBias_b.GetXaxis().SetTitleSize(0.05)
        h_MinBias_b.GetXaxis().SetLabelSize(0.05)
        h_MinBias_b.GetXaxis().SetTitleOffset(1.2)
        if binweight:
            h_MinBias_b.GetYaxis().SetTitle("Density #frac{1}{N} #frac{dN}{db} (normalised)")
        else:
            h_MinBias_b.GetYaxis().SetTitle("Number of Events (normalised)")
        h_MinBias_b.GetYaxis().SetTitleSize(0.05)
        h_MinBias_b.GetYaxis().SetLabelSize(0.05)
        h_MinBias_b.GetYaxis().SetTitleOffset(0.8)
        h_MinBias_b.GetXaxis().SetRangeUser(0, 2)


        h_MCMinBias_b.SetStats(0)
        h_MCMinBias_b.SetLineColor(ROOT.kViolet - 6)
        h_MCMinBias_b.SetLineWidth(2)
        h_MCMinBias_b.SetLineStyle(2)



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

            

            colour = colours[index % len(colours)]

    
            h_SingleMuon_ptr = df_SingleMuon_q.Histo1D(
                (f"h_SingleMuon_{var}_quantile_{pt_cut}GeVCut", f"; {plot_xlabel}; {y_title}", len(quantile_bins) - 1, quantile_bins),
                q_column,
            )
            h_MCDYJets_ptr = df_MCDYJets_q.Histo1D(
                (f"h_MCDYJets_{var}_quantile_{pt_cut}GeVCut", f"; {plot_xlabel}; {y_title}", len(quantile_bins) - 1, quantile_bins),
                q_column,
            )

            h_SingleMuon = h_SingleMuon_ptr.GetValue()
            h_MCDYJets = h_MCDYJets_ptr.GetValue()

            NormaliseHist(h_SingleMuon, binweight)
            NormaliseHist(h_MCDYJets, binweight)

            pad1.cd()

            h_DYMinBias = h_SingleMuon.Clone(f"h_DYMinBias_{var}_quantile_{pt_cut}GeVCut")
            h_DYMinBias.Divide(h_MinBias)

            h_MCDYMinBias = h_MCDYJets.Clone(f"h_MCDYMinBias_{var}_quantile_{pt_cut}GeVCut")
            h_MCDYMinBias.Divide(h_MCMinBias)


    
            h_DYMinBias.SetStats(0)
            h_DYMinBias.SetLineColor(colour)
            h_DYMinBias.SetMarkerColor(colour)
            h_DYMinBias.SetLineWidth(2)
            h_DYMinBias.GetXaxis().SetTitle(plot_xlabel)
            h_DYMinBias.GetXaxis().SetTitleSize(0.05)
            h_DYMinBias.GetXaxis().SetLabelSize(0.05)
            h_DYMinBias.GetXaxis().SetTitleOffset(1.2)
            if binweight:
                h_DYMinBias.GetYaxis().SetTitle("Density #frac{1}{N} #frac{dN}{dq} (normalised)")
            else:
                h_DYMinBias.GetYaxis().SetTitle("Number of Events (normalised)")
            h_DYMinBias.GetYaxis().SetTitleSize(0.05)
            h_DYMinBias.GetYaxis().SetLabelSize(0.05)
            h_DYMinBias.GetYaxis().SetTitleOffset(0.8)


            h_MCDYMinBias.SetStats(0)
            h_MCDYMinBias.SetLineColor(colour)
            h_MCDYMinBias.SetMarkerColor(colour)
            h_MCDYMinBias.SetLineWidth(2)
            h_MCDYMinBias.SetLineStyle(2)

            h_DYMinBias.GetYaxis().SetRangeUser(0, max(h_DYMinBias.GetMaximum(), h_MCDYMinBias.GetMaximum()) * 1.1)
            
            if index == 0:
                h_DYMinBias.Draw("hist e")
            else:
                h_DYMinBias.Draw("hist e same")
            h_MCDYMinBias.Draw("hist e same")




            canvas.cd()
            pad2.cd()



            h_SingleMuon_b_ptr = df_SingleMuon_q.Histo1D(
                                                    (
                                                        f"h_SingleMuon_{var}_b_{pt_cut}GeVCut",
                                                        ";impact parameter b;Normalised density",
                                                        # len(pad2_edges) - 1, pad2_edges
                                                        # 50, 0, 1
                                                        len(b_bins) - 1, b_bins
                                                    ),
                                                    b_column,
                                                )
            h_MCDYJets_b_ptr = df_MCDYJets_q.Histo1D(
                                                    (
                                                        f"h_MCDYJets_{var}_b_{pt_cut}GeVCut",
                                                        ";impact parameter b;Normalised density",
                                                        # len(pad2_edges) - 1, pad2_edges
                                                        # 50, 0, 1
                                                        len(b_bins) - 1, b_bins
                                                    ),
                                                    b_column,
                                                )


            h_SingleMuon_b = h_SingleMuon_b_ptr.GetValue()
            h_MCDYJets_b = h_MCDYJets_b_ptr.GetValue()

            NormaliseHist(h_SingleMuon_b, binweight)
            NormaliseHist(h_MCDYJets_b, binweight)


            h_DYMinBias_b = h_SingleMuon_b.Clone(f"h_DYMinBias_{var}_quantile_b_{pt_cut}GeVCut")
            h_DYMinBias_b.Divide(h_MinBias_b)
            h_MCDYMinBias_b = h_MCDYJets_b.Clone(f"h_MCDYMinBias_{var}_quantile_b_{pt_cut}GeVCut")
            h_MCDYMinBias_b.Divide(h_MCMinBias_b)

            h_DYMinBias_b.SetStats(0)
            h_DYMinBias_b.SetLineColor(colour)
            h_DYMinBias_b.SetMarkerColor(colour)
            h_DYMinBias_b.SetLineWidth(2)
            h_DYMinBias_b.GetXaxis().SetTitle("impact parameter b")
            h_DYMinBias_b.GetXaxis().SetTitleSize(0.05)
            h_DYMinBias_b.GetXaxis().SetLabelSize(0.05)
            h_DYMinBias_b.GetXaxis().SetTitleOffset(1.4)
            if binweight:
                h_DYMinBias_b.GetYaxis().SetTitle("Density #frac{1}{N} #frac{dN}{db} (normalised)")
            else:
                h_DYMinBias_b.GetYaxis().SetTitle("Number of Events (normalised)")
            h_DYMinBias_b.GetYaxis().SetTitleSize(0.05)
            h_DYMinBias_b.GetYaxis().SetLabelSize(0.05)
            h_DYMinBias_b.GetYaxis().SetTitleOffset(0.8)


            h_MCDYMinBias_b.SetStats(0)
            h_MCDYMinBias_b.SetLineColor(colour)
            h_MCDYMinBias_b.SetMarkerColor(colour)
            h_MCDYMinBias_b.SetLineWidth(2)
            h_MCDYMinBias_b.SetLineStyle(2)


            h_DYMinBias_b.GetYaxis().SetRangeUser(0, max(h_DYMinBias_b.GetMaximum(), h_MCDYMinBias_b.GetMaximum()) * 1.1)
            

            if index == 0:
                h_DYMinBias_b.Draw("hist e")
            else:
                h_DYMinBias_b.Draw("hist e same")

            h_MCDYMinBias_b.Draw("hist e same")






            # ratio_SingleMuon.Scale(1 * (xsec_MINBIAS/xsec_DY) * (xsec_INEL/xsec_MINBIAS) * (Events_MINBIAS/Events_DY))
            # ratio_MCDYJets.Scale(1 * (xsec_MINBIAS/xsec_DY) * (xsec_INEL/xsec_MINBIAS) * (Events_MCMINBIAS/Events_MCDY))



   



            # ---------------------- from Pythia --------------------
            if pt_cut == 4:

                canvas.cd()
                pad2.cd()

                df_pythia = pd.read_hdf("simulated_enhf_vs_impactparam.hdf")

                values = df_pythia["values"]
                edges = df_pythia["edges"]

                index_pythia = 0


                if var == "PFCands_Ht":
                    index_pythia = 2
                elif var == "PFCands_Pt2sum":
                    index_pythia = 5
                elif var == "PFCands_InvariantMass":
                    index_pythia = 3
                elif var == "nPFCands":
                    index_pythia = 0
                elif var == "PFCands_Psum":
                    index_pythia = 1
                else:
                    print(f"Variable {var} not found in Pythia data; skipping Pythia overlay.")

                bins_new = array.array('d', np.asarray(df_pythia["edges"].iloc[index_pythia], dtype=np.float64))
                h_pythia = ROOT.TH1F("h_pythia", "", len(bins_new) - 1, bins_new)

                row_values = values.iloc[index_pythia]
                row_edges = edges.iloc[index_pythia]

                # print(f"Setting Pythia histogram for {var} with {len(row_values)} bins and edges: {row_edges}")


                for j in range(len(row_values)):
                    h_pythia.SetBinContent(j, row_values[j])
                # print(f"Set bin {j} content to {row_values[j]}")



                # NormaliseHist(h_pythia)

                h_pythia.SetLineColor(ROOT.kRed)
                h_pythia.SetLineWidth(2)
                # h_pythia.SetLineStyle(2)

                h_pythia.Draw("hist same")


                h_DYMinBias_b.SetMaximum(max(h_DYMinBias_b.GetMaximum(), h_MCDYMinBias_b.GetMaximum(), h_pythia.GetMaximum()) * 1.1)



            canvas.cd()
            pad1.cd()


        


            if pt_cut is None or len(pt_cuts) == 0:
                legend_var.AddEntry(dummy, f"#color[{ROOT.kBlack}]{{No p^{{#mu#mu}}_{{T}} cut}}", "")
            else:
                legend_var.AddEntry(dummy, f"#color[{ROOT.kBlack}]{{p^{{#mu#mu}}_{{T}} < {pt_cut} GeV}}", "")

            
        
        

            legend_DataMC.Draw()
            legend_var.Draw()


            canvas.cd()
            pad2.cd()

            legend_var_pad2 = legend_var.Clone()
            legend_DataMC_pad2 = legend_DataMC.Clone()

            legend_var_pad2.SetY1(0.68)

            

            for entry in list(legend_DataMC_pad2.GetListOfPrimitives()):
                if entry.GetLabel() == "MinBias":
                    legend_DataMC_pad2.GetListOfPrimitives().Remove(entry)
                if entry.GetLabel() == "#bf{Data}":
                    legend_DataMC_pad2.GetListOfPrimitives().Remove(entry)
                if entry.GetLabel() == "#bf{MC}":
                    legend_DataMC_pad2.GetListOfPrimitives().Remove(entry)            
            

            legend_DataMC_pad2.AddEntry(h_DYMinBias_b, f"#bf{{Data}}", "l")
            legend_DataMC_pad2.AddEntry(h_MCDYMinBias_b, f"#bf{{MC}}", "l")
            # legend_DataMC_pad2.AddEntry(dummy, f"#color[{ROOT.kOrange + 5}]{{#bf{{b: bTb}}}}", "")
            # legend_DataMC_pad2.AddEntry(dummy, f"#color[{ROOT.kGreen + 3}]{{#bf{{b: eTe}}}}", "")
            if pt_cut == 4:
                legend_DataMC_pad2.AddEntry(h_pythia, f"#bf{{Pythia}}", "l")


            legend_DataMC_pad2.Draw()
            legend_var_pad2.Draw()



        output_dir = f"new_plots/quantile_binning/{bins}"
        os.makedirs(output_dir, exist_ok=True)

        if pt_cut is None or len(pt_cuts) == 0:
            output_name = f"{output_dir}/{var}_DYMinBias_NoZPtCut{out_suffix}.pdf"
        else:
            output_name = f"{output_dir}/{var}_DYMinBias_{pt_cut}GeVZPtCut{out_suffix}.pdf"

        canvas.SaveAs(output_name)

        canvas.Close()

def Quantile_DiMuonPtCut(df_SingleMuon_var, df_MinBias_var, df_MCDYJets_var, df_MCMinBias_var, variables, pt_cuts, out_suffix, bins, b_bins):

    quantile_bins = array.array("d", bins)
    
    if b_bins is None:
        # b_bins = array.array("d", np.linspace(0, 1, 50))
        b_bins = array.array("d", np.concatenate([
                                  np.arange(0.00, 0.10, 0.01),
                                  np.arange(0.10, 0.20, 0.01),
                                  np.arange(0.20, 1.05, 0.05)
                                ])
                            )
    else:
        b_bins = array.array("d", b_bins)

    pt_cuts = parse_pt_cuts(pt_cuts)



    histos = []
    inset_histos = []

    def colors_func(n):
        base = [
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
    
    colours = colors_func(len(pt_cuts))


    for var in variables:
        if var in ["PFCands_pt", "PFCands_eta", "PFCands_phi", "PFCands_pvAssocQuality"]:
            continue

        label = VARIABLES[var]
        binning = BINNING[var]
        y_title = "Cumulative Distribution Function (CDF)"


        q_column = f"{var}_InvQ"
        plot_xlabel = f"impact parameter b"
        b_column = f"{var}_b"



        canvas = ROOT.TCanvas(f"c_quantile_ptscan_{var}", "", 1500, 1400)
        canvas.cd()
        canvas.SetBottomMargin(0.05)
        canvas.SetRightMargin(0.26)
        canvas.SetTopMargin(0.05)
        # canvas.SetLogy()

        pad1 = ROOT.TPad(f"pad1_{var}GeV", "pad1", 0, 0.4, 1, 1)
        pad1.SetLeftMargin(0.10)
        pad1.SetRightMargin(0.26)
        pad1.SetLogy()
        pad1.SetGridy(1)
        pad1.SetTicky(1)
        pad1.Draw()

        canvas.cd()

        # left bottom pad: y-axis only
        pad2 = ROOT.TPad(f"pad2_{var}GeV", "pad2", 0.0, 0, 0.4, 0.4)
        pad2.SetLeftMargin(0.18)
        pad2.SetRightMargin(0.03)
        pad2.SetBottomMargin(0.1)
        pad2.SetTopMargin(0)
        pad2.SetLogy()
        pad2.SetGridy(1)
        pad2.SetTicky(1)
        pad2.Draw()

        canvas.cd()

        # right bottom pad: x-axis only
        pad3 = ROOT.TPad(f"pad3_{var}GeV", "pad3", 0.43, 0, 0.86, 0.4)
        pad3.SetLeftMargin(0.03)
        pad3.SetRightMargin(0.26)
        pad3.SetBottomMargin(0.1)
        pad3.SetTopMargin(0)
        pad3.SetLogy()
        pad3.SetGridy(1)
        pad3.SetTicky(1)
        pad3.Draw()


        canvas.cd()
    
        inset = ROOT.TPad(f"inset_{var}", f"inset_{var}", 0.75, 0, 1, 1)
        inset.SetLogy()
        inset.SetFillStyle(0)
        inset.SetBorderSize(1)
        inset.SetRightMargin(0.05)
        inset.SetBottomMargin(0.13)
        inset.Draw()
        inset.cd()
        # inset.DrawFrame(0, 2, 0.08, 11)
        inset.SetGridy(1)
        inset.SetTicky(0)


    

        dummy = ROOT.TObject()


        legend_var = ROOT.TLegend(0.42, 0.8, 0.6, 0.89)
        legend_var.SetBorderSize(0)
        # legend_var.SetFillStyle(0)
        legend_var.SetTextSize(0.03)
        legend_var.SetMargin(0.2)
        legend_var.AddEntry(dummy, label, "")

        legend_col0 = ROOT.TLegend(0.53, 0.75, 0.72, 0.89001)
        legend_col0.SetBorderSize(0)
        # legend_col0.SetFillStyle(0)
        legend_col0.SetTextSize(0.03)
        legend_col0.SetMargin(0.2)
        

        legend_ptcuts = ROOT.TLegend(0.13, 0.13, 0.48, 0.51)
        legend_ptcuts.SetBorderSize(0)
        # legend_ptcuts.SetFillStyle(0)
        legend_ptcuts.SetTextSize(0.03)
        legend_ptcuts.SetMargin(0.05)
        legend_ptcuts.SetNColumns(2)
        # legend_ptcuts.SetColumnSeparation(0.001)

        legend_Data = ROOT.TLine(0.0, 0.0, 0.5, 0.0)
        legend_Data.SetLineColor(ROOT.kBlack)
        legend_Data.SetLineWidth(2)
        legend_Data.SetLineStyle(1)

        legend_MC = ROOT.TLine(0.0, 0.0, 0.5, 0.0)
        legend_MC.SetLineColor(ROOT.kBlack)
        legend_MC.SetLineWidth(2)
        legend_MC.SetLineStyle(2)
        
        legend_col0.AddEntry(legend_Data, f"#color[{ROOT.kBlack}]{{#bf{{Data}}}}", "l")
        legend_col0.AddEntry(legend_MC, f"#color[{ROOT.kBlack}]{{#bf{{MC}}}}", "l")
        legend_col0.AddEntry(dummy, "86 < m_{#mu#mu} < 96 GeV", "")
        # legend_col0.AddEntry(dummy, f"#color[{ROOT.kOrange + 5}]{{#bf{{MinBias}}}}", "")

        # legend_ptcuts.AddEntry(dummy, f"#color[{ROOT.kBlack}]{{#bf{{DY/MinBias:}}}}", "")
        legend_ptcuts.SetHeader("#bf{DY/MinBias:}", "L")

        df_pythia = pd.read_hdf("simulated_enhf_vs_impactparam.hdf")

        values = df_pythia["values"]
        edges = df_pythia["edges"]

        index_pythia = 0


        if var == "PFCands_Ht":
            index_pythia = 2
        elif var == "PFCands_Pt2sum":
            index_pythia = 5
        elif var == "PFCands_InvariantMass":
            index_pythia = 3
        elif var == "nPFCands":
            index_pythia = 0
        elif var == "PFCands_Psum":
            index_pythia = 1
        else:
            print(f"Variable {var} not found in Pythia data; skipping Pythia overlay.")

        bins_new = array.array('d', np.asarray(df_pythia["edges"].iloc[index_pythia], dtype=np.float64))
        h_pythia = ROOT.TH1F("h_pythia", "", len(bins_new) - 1, bins_new)

        row_values = values.iloc[index_pythia]
        row_edges = edges.iloc[index_pythia]

        # print(f"Setting Pythia histogram for {var} with {len(row_values)} bins and edges: {row_edges}")


        for j in range(len(row_values)):
            h_pythia.SetBinContent(j, row_values[j])
        # print(f"Set bin {j} content to {row_values[j]}")

        h_pythia.SetStats(0)
        h_pythia.SetLineColor(ROOT.kRed)
        h_pythia.SetMarkerColor(ROOT.kRed)
        h_pythia.SetLineWidth(2)
        h_pythia.SetLineStyle(6)
        h_pythia.SetDirectory(0)
        h_pythia.GetXaxis().SetTitle(plot_xlabel)
        h_pythia.GetXaxis().SetTitleSize(0.04)
        h_pythia.GetXaxis().SetLabelSize(0.04)
        h_pythia.GetXaxis().SetTickLength(0.04)
        h_pythia.GetYaxis().SetTitle("DY/MinBias")
        h_pythia.GetYaxis().SetTitleSize(0.03)
        h_pythia.GetYaxis().SetLabelSize(0.04)
        h_pythia.GetYaxis().SetTitleOffset(1)
        h_pythia.GetYaxis().SetNdivisions(505)
    

        canvas.cd()
        pad1.cd()

        h_pythia.Draw("hist")

        histos.append(h_pythia)

        h_pythia_clone = h_pythia.Clone(f"h_pythia_clone_{var}")
        inset_histos.append(h_pythia_clone)

        legend_var.AddEntry(h_pythia, "Pythia", "l")






        # b_bins = array.array("d", row_edges)



        BuildQuantile(df_MinBias_var, var, "MB")
        BuildQuantile(df_MCMinBias_var, var, "MCMB")

        df_MinBias_q = ApplyQuantileAndIP(df_MinBias_var, var, "MB")
        df_MCMinBias_q = ApplyQuantileAndIP(df_MCMinBias_var, var, "MCMB")


          
        h_MinBias_ptr = df_MinBias_q.Histo1D((f"h_MinBias_{var}_b", ";impact parameter b;Normalised density",
                # len(pad2_edges) - 1, pad2_edges
                # 50, 0, 1
                len(b_bins) - 1, b_bins
            ),
            b_column,
        )
        h_MCMinBias_ptr = df_MCMinBias_q.Histo1D(
            (
                f"h_MCMinBias_{var}_b",
                ";impact parameter b;Normalised density",
                # len(pad2_edges) - 1, pad2_edges
                # 50, 0, 1
                len(b_bins) - 1, b_bins
            ),
            b_column,
        )


        h_MinBias = h_MinBias_ptr.GetValue()
        h_MCMinBias = h_MCMinBias_ptr.GetValue()

        NormaliseHist(h_MinBias, True)
        NormaliseHist(h_MCMinBias, True)


        plot_max = 0


        for index, pt_cut in enumerate(pt_cuts):

            if index == len(pt_cuts) - 1:
                break

            if pt_cut is None:
                pt_cut = 0
                pt_cuts[index] = 0

            canvas.cd()
            
            
            print(f"\n\nProcessing DiMuon pT cut: {pt_cut} GeV...\n")

            df_SingleMuon_q = df_SingleMuon_var.Filter(f"DiMuon_Pt >= {pt_cuts[index]} && DiMuon_Pt < {pt_cuts[index + 1]}")
            df_MCDYJets_q = df_MCDYJets_var.Filter(f"DiMuon_Pt >= {pt_cuts[index]} && DiMuon_Pt < {pt_cuts[index + 1]}")

            df_SingleMuon_q = ApplyQuantileAndIP(df_SingleMuon_q, var, "MB")
            df_MCDYJets_q = ApplyQuantileAndIP(df_MCDYJets_q, var, "MCMB")
                
            colour = colours[index]

            h_SingleMuon_ptr = df_SingleMuon_q.Histo1D(
                (
                    f"h_SingleMuon_{var}_b_{pt_cut}GeV",
                    f"; {plot_xlabel}; DY/ZeroBias",
                    len(b_bins) - 1, b_bins
                ),
                b_column,
            )
            h_MCDYJets_ptr = df_MCDYJets_q.Histo1D(
                (
                    f"h_MCDYJets_{var}_b_{pt_cut}GeV",
                    f";{plot_xlabel}; DY/ZeroBias",
                    len(b_bins) - 1, b_bins
                ),
                b_column,
            )
   

            h_SingleMuon = h_SingleMuon_ptr.GetValue()
            h_MCDYJets = h_MCDYJets_ptr.GetValue()


            NormaliseHist(h_SingleMuon, True)
            NormaliseHist(h_MCDYJets, True)
            
            
            pad1.cd()


            ratio_Data = h_SingleMuon.Clone(f"Data_DYMinBias_final_{var}_{pt_cut}GeV")
            ratio_Data.Divide(h_MinBias)
            ratio_Data.SetLineColor(colour)
            ratio_Data.SetMarkerColor(colour)
            ratio_Data.SetLineWidth(2)
            ratio_Data.SetDirectory(0)
            ratio_Data.GetXaxis().SetTitle(plot_xlabel)
            ratio_Data.GetXaxis().SetTitleSize(0.03)
            ratio_Data.GetXaxis().SetLabelSize(0.03)
            ratio_Data.GetXaxis().SetTickLength(0.04)
            ratio_Data.GetYaxis().SetTitle("DY/MinBias")
            ratio_Data.GetYaxis().SetTitleSize(0.03)
            ratio_Data.GetYaxis().SetLabelSize(0.03)
            ratio_Data.GetYaxis().SetTitleOffset(1.5)
            ratio_Data.GetYaxis().SetNdivisions(505)
            histos.append(ratio_Data)

            ratio_MC = h_MCDYJets.Clone(f"MC_DYMinBias_final_{var}_{pt_cut}GeV")
            ratio_MC.Divide(h_MCMinBias)
            ratio_MC.SetLineColor(colour)
            ratio_MC.SetMarkerColor(colour)
            ratio_MC.SetLineStyle(2)
            ratio_MC.SetLineWidth(2)
            ratio_MC.SetDirectory(0)
            # ratio_MC.SetMarkerStyle(20)
            ratio_MC.SetMarkerSize(0.8)
            ratio_MC.GetXaxis().SetTitle(plot_xlabel)
            ratio_MC.GetXaxis().SetTitleSize(0.1)
            ratio_MC.GetXaxis().SetTitleOffset(1.3)
            ratio_MC.GetXaxis().SetLabelSize(0.085)
            ratio_MC.GetXaxis().SetTickLength(0.07)
            ratio_MC.GetYaxis().SetTitle("DY/MinBias")
            ratio_MC.GetYaxis().SetTitleSize(0.1)
            ratio_MC.GetYaxis().SetLabelSize(0.075)
            ratio_MC.GetYaxis().SetTitleOffset(0.5)
            ratio_MC.GetYaxis().SetNdivisions(10, False)

            histos.append(ratio_MC)


            ratio_Data.Draw("hist e same")
            ratio_MC.Draw("hist e same")



            legend_ptcuts.AddEntry(dummy, f"#color[{colour}]{{#bf{{{int(pt_cuts[index])} GeV #leq p^{{#mu#mu}}_{{T}} < {int(pt_cuts[index + 1])} GeV}}}}", "")



            print(f"Finished processing diMuon pT cut: {pt_cut} GeV!\n")


            canvas.cd()
            inset.cd()

            
            # clone histograms so axis/range changes don't affect main pads
            h1 = ratio_Data.Clone(ratio_Data.GetName() + "_inset")
            h1MC = ratio_MC.Clone(ratio_MC.GetName() + "_inset") 

            h1.GetXaxis().SetTitle(plot_xlabel)
            h1.GetXaxis().SetLabelSize(0.03)
            h1.GetYaxis().SetLabelSize(0.06)
            h1.GetYaxis().SetTitle("DY/MinBias")
            
            h1MC.GetXaxis().SetTitle(plot_xlabel)
            h1MC.GetXaxis().SetLabelSize(0.03)
            h1MC.GetYaxis().SetLabelSize(0.06)
            h1MC.GetYaxis().SetTitle("DY/MinBias")

            inset_histos.append((h1, h1MC))

            
        canvas.cd()
        inset.cd()

        xmin = 0
        xmax = 0.15
        yminInset_list = []
        ymaxInset_list = []


        for index, ih in enumerate(inset_histos):
            if index == 0:
                yminInset_list.append(min(ih.GetBinContent(i) for i in range(1, 5)))
                ymaxInset_list.append(max(ih.GetBinContent(i) for i in range(1, 5)))
            else:
                yminInset_list.append(min(ih[0].GetBinContent(i) for i in range(1, 5)))
                ymaxInset_list.append(max(ih[0].GetBinContent(i) for i in range(1, 5)))



        yminInset = min(yminInset_list) * 0.7
        if yminInset <= 0:
            yminInset = 0.0001
        ymaxInset = max(ymaxInset_list) * 1.2

        
        frame = inset.DrawFrame(xmin, yminInset, xmax, ymaxInset)
        frame.GetXaxis().SetLabelSize(0.05)
        frame.GetYaxis().SetLabelSize(0.06)
        frame.GetXaxis().SetTitleSize(0.05)
        frame.GetYaxis().SetTitleSize(0.01)
        frame.GetXaxis().SetLabelOffset(0)
        frame.GetYaxis().SetNdivisions(505)
        frame.GetXaxis().SetTitle("impact parameter b")
        frame.GetYaxis().SetTitle("DY/MinBias")
        frame.GetYaxis().SetTitleSize(0.06)

        frame.GetXaxis().SetTitleOffset(0.8)
        frame.GetYaxis().SetTitleOffset(0.8)

        frame.GetXaxis().SetRangeUser(xmin, xmax)

        # inset_histos[0].GetXaxis().SetTitle("impact parameter b")
        # inset_histos[0].GetYaxis().SetTitle("DY/MinBias")
        # inset_histos[0].GetXaxis().SetLabelSize(0.01)
        # inset_histos[0].GetXaxis().SetTitleSize(0.01)
        # inset_histos[0].GetYaxis().SetLabelSize(0.08)
        # inset_histos[0].GetXaxis().SetRangeUser(xmin, xmax)




        for index, ih in enumerate(inset_histos):
            if index == 0:
                ih.Draw("hist e same")
            else:
                ih[0].Draw("hist e same")


        max_hist = max(
            h_pythia.GetMaximum(),
            max(h.GetMaximum() for h in histos)
        ) * 1.2

        h_pythia.SetMaximum(max_hist)



        canvas.cd()
        pad2.cd()

        data_ref = histos[1].Clone("data_ref")
        mc_ref   = histos[2].Clone("mc_ref")

        data_ref.SetDirectory(0)
        mc_ref.SetDirectory(0)

        ratio_histos = []

        for index, h in enumerate(histos):

            if index == 0:
                continue

            ratio_left = h.Clone(f"{h.GetName()}_ratio_{index}")
            ratio_left.SetDirectory(0)

            if index % 2 != 0:
                ratio_left.Divide(data_ref)
            else:
                ratio_left.Divide(mc_ref)

            ratio_left.SetLineColor(h.GetLineColor())
            ratio_left.SetMarkerColor(h.GetMarkerColor())
            ratio_left.SetMarkerStyle(h.GetMarkerStyle())
            ratio_left.SetMarkerSize(h.GetMarkerSize())
            ratio_left.SetLineStyle(h.GetLineStyle())
            ratio_left.SetLineWidth(2)

            ratio_left.GetXaxis().SetTitle("")
            ratio_left.GetXaxis().SetTitleSize(0)
            ratio_left.GetXaxis().SetLabelSize(0.05)

            ratio_left.GetYaxis().SetTitle("#frac{DY/MinBias for a p^{#mu#mu}_{T} interval}{DY/MinBias for lowest p^{#mu#mu}_{T} interval}")
            ratio_left.GetYaxis().SetTitleSize(0.04)
            ratio_left.GetYaxis().SetLabelSize(0.06)
            ratio_left.GetYaxis().SetTitleOffset(1.4)

            ratio_histos.append(ratio_left)


        x_cut = 0.3

        ymin_ratio_left = min(
            h.GetBinContent(i)
            for h in ratio_histos
            for i in range(1, h.FindBin(x_cut)+1)
            if h.GetBinContent(i) > 0
        ) * 0.9

        ymax_ratio_left = max(
            h.GetBinContent(i)
            for h in ratio_histos
            for i in range(1, h.FindBin(x_cut)+1)
        ) * 1.1


        ratio_histos[0].GetXaxis().SetRangeUser(0, x_cut)
        ratio_histos[0].GetYaxis().SetRangeUser(
            ymin_ratio_left,
            ymax_ratio_left
        )


        # draw first histogram as frame
        ratio_histos[0].Draw("hist e")

        for ratio in ratio_histos[1:]:
            ratio.Draw("hist e same")

        

        canvas.cd()
        pad3.cd()

        ratio_histos_right = []

        for h in ratio_histos:

            ratio_right = h.Clone(f"{h.GetName()}_right")
            ratio_right.SetDirectory(0)

            ratio_right.SetLineColor(h.GetLineColor())
            ratio_right.SetMarkerColor(h.GetMarkerColor())
            ratio_right.SetMarkerStyle(h.GetMarkerStyle())
            ratio_right.SetMarkerSize(h.GetMarkerSize())
            ratio_right.SetLineStyle(h.GetLineStyle())
            ratio_right.SetLineWidth(2)


            ratio_right.GetXaxis().SetTitle(plot_xlabel)
            ratio_right.GetXaxis().SetTitleSize(0.05)
            ratio_right.GetXaxis().SetTitleOffset(0.95)
            ratio_right.GetXaxis().SetLabelSize(0.05)

            ratio_right.GetYaxis().SetTitle("")
            ratio_right.GetYaxis().SetTitleSize(0)
            ratio_right.GetYaxis().SetLabelSize(0.06)
            ratio_right.GetYaxis().SetLabelOffset(0.007)


            ratio_histos_right.append(ratio_right)



        ymin_ratio_right = min(
            h.GetBinContent(i)
            for h in ratio_histos_right
            for i in range(h.FindBin(x_cut), h.GetNbinsX()+1)
            if h.GetBinContent(i) > 0
        ) * 0.9


        ymax_ratio_right = max(
            h.GetBinContent(i)
            for h in ratio_histos_right
            for i in range(h.FindBin(x_cut), h.GetNbinsX()+1)
        ) * 1.1


        ratio_histos_right[0].GetXaxis().SetRangeUser(x_cut, 1)
        ratio_histos_right[0].GetYaxis().SetRangeUser(
            ymin_ratio_right,
            ymax_ratio_right
        )


        # draw first histogram as frame
        ratio_histos_right[0].Draw("hist e")

        for ratio in ratio_histos_right[1:]:
            ratio.Draw("hist e same")


        canvas.cd()
        pad1.cd()

        legend_ptcuts.Draw()
        legend_var.Draw()
        legend_col0.Draw()


        output_dir = f"new_plots/quantile_binning/{bins}"
        os.makedirs(output_dir, exist_ok=True)

        output_name = f"{output_dir}/{var}_QuantilePtScan{out_suffix}.pdf"
        canvas.SaveAs(output_name)

        canvas.Close()




def Quantile_AllTogether(df_SingleMuon_var, df_MinBias_var, df_MCDYJets_var, df_MCMinBias_var, variables, out_suffix, bins):

    colours = [ROOT.kViolet - 6, ROOT.kBlue - 4, ROOT.kGreen + 3, ROOT.kOrange + 5, ROOT.kRed + 1, ROOT.kCyan + 2]
    ratio_data_hists = []
    ratio_mc_hists = []
    ratio_final_hists = []

    for var in variables:
        if var in ["PFCands_pt", "PFCands_eta", "PFCands_phi", "PFCands_pvAssocQuality"]:
            continue

        label = VARIABLES[var]
        binning = BINNING[var]
        y_title = "Arbitrary Units"

        h_tmp_ptr = MakeHist(df_MinBias_var, var, label, y_title, binning, f"h_MinBias_{var}_quantile_all_tmp")
        h_tmp = h_tmp_ptr.GetValue()
        total = h_tmp.Integral()
        if total <= 0:
            print(f"Warning: MinBias histogram for '{var}' has zero integral; skipping all-together quantile plot")
            continue

        bin_edges = [h_tmp.GetBinLowEdge(1)]
        cdf_values = [0.0]
        cumulative = 0.0
        for i in range(1, h_tmp.GetNbinsX() + 1):
            cumulative += h_tmp.GetBinContent(i)
            edge = h_tmp.GetBinLowEdge(i + 1)
            cdf = cumulative / total if total > 0 else 0.0
            bin_edges.append(edge)
            cdf_values.append(cdf)

        edges_cpp = ", ".join(f"{x:.17g}" for x in bin_edges)
        cdf_cpp = ", ".join(f"{x:.17g}" for x in cdf_values)

        ROOT.gInterpreter.Declare(
            f"""
            namespace {var}InvQMapAllTogether {{
            static const std::vector<double> edges = {{{edges_cpp}}};
            static const std::vector<double> cdf = {{{cdf_cpp}}};

            double eval(double x) {{
                if (edges.empty()) return 0.0;
                if (x <= edges.front()) return 0.0;
                if (x >= edges.back()) return 1.0;

                for (size_t i = 1; i < edges.size(); ++i) {{
                    if (x < edges[i]) {{
                        double x1 = edges[i - 1];
                        double x2 = edges[i];
                        double y1 = cdf[i - 1];
                        double y2 = cdf[i];
                        return y1 + (x - x1) * (y2 - y1) / (x2 - x1);
                    }}
                }}
                return 1.0;
            }}
            }}
            """
        )

        h_MCtmp_ptr = MakeHist(df_MCMinBias_var, var, label, y_title, binning, f"h_MCMinBias_{var}_quantile_ptscan_tmp")
        h_MCtmp = h_MCtmp_ptr.GetValue()
        total_MC = h_MCtmp.Integral()
        if total_MC <= 0:
            print(f"Warning: MCMinBias histogram for '{var}' has zero integral; skipping quantile pT-scan plot")
            continue

        bin_edges_MC = [h_MCtmp.GetBinLowEdge(1)]
        cdf_values_MC = [0.0]
        cumulative_MC = 0.0
        for i in range(1, h_MCtmp.GetNbinsX() + 1):
            cumulative_MC += h_MCtmp.GetBinContent(i)
            edge_MC = h_MCtmp.GetBinLowEdge(i + 1)
            cdf_MC = cumulative_MC / total_MC if total_MC > 0 else 0.0
            bin_edges_MC.append(edge_MC)
            cdf_values_MC.append(cdf_MC)

        edges_cpp_MC = ", ".join(f"{x:.17g}" for x in bin_edges_MC)
        cdf_cpp_MC = ", ".join(f"{x:.17g}" for x in cdf_values_MC)

        ROOT.gInterpreter.Declare(
            f"""
            namespace {var}InvQMapAllTogetherMC {{
            static const std::vector<double> edges = {{{edges_cpp_MC}}};
            static const std::vector<double> cdf = {{{cdf_cpp_MC}}};

            double eval(double x) {{
                if (edges.empty()) return 0.0;
                if (x <= edges.front()) return 0.0;
                if (x >= edges.back()) return 1.0;

                for (size_t i = 1; i < edges.size(); ++i) {{
                    if (x < edges[i]) {{
                        double x1 = edges[i - 1];
                        double x2 = edges[i];
                        double y1 = cdf[i - 1];
                        double y2 = cdf[i];
                        return y1 + (x - x1) * (y2 - y1) / (x2 - x1);
                    }}
                }}
                return 1.0;
            }}
            }}
            """
        )

        df_MinBias_q = df_MinBias_var.Define(f"{var}_invQ_all", f"1.0 - {var}InvQMapAllTogether::eval(PFSelection_{var})")
        df_SingleMuon_q = df_SingleMuon_var.Define(f"{var}_invQ_all", f"1.0 - {var}InvQMapAllTogether::eval(PFSelection_{var})")
        df_MCDYJets_q = df_MCDYJets_var.Define(f"{var}_invQ_all", f"1.0 - {var}InvQMapAllTogetherMC::eval(PFSelection_{var})")
        df_MCMinBias_q = df_MCMinBias_var.Define(f"{var}_invQ_all", f"1.0 - {var}InvQMapAllTogetherMC::eval(PFSelection_{var})")


        plot_column = f"{var}_invQ_all"
        plot_xlabel = "1 - F_{MB}(x)"

        edges = array.array("d", bins)

        h_MinBias_ptr = df_MinBias_q.Histo1D(
            (f"h_MinBias_{var}_quantile_all", f"; {plot_xlabel}; {y_title}", len(edges) - 1, edges),
            plot_column,
        )
        h_SingleMuon_ptr = df_SingleMuon_q.Histo1D(
            (f"h_SingleMuon_{var}_quantile_all", f"; {plot_xlabel}; {y_title}", len(edges) - 1, edges),
            plot_column,
        )
        h_MCDYJets_ptr = df_MCDYJets_q.Histo1D(
            (f"h_MCDYJets_{var}_quantile_all", f"; {plot_xlabel}; {y_title}", len(edges) - 1, edges),
            plot_column,
        )
        h_MCMinBias_ptr = df_MCMinBias_q.Histo1D(
            (f"h_MCMinBias_{var}_quantile_all", f"; {plot_xlabel}; {y_title}", len(edges) - 1, edges),
            plot_column,
        )

        h_MinBias = h_MinBias_ptr.GetValue()
        h_SingleMuon = h_SingleMuon_ptr.GetValue()
        h_MCDYJets = h_MCDYJets_ptr.GetValue()
        h_MCMinBias = h_MCMinBias_ptr.GetValue()


        for h in [h_MinBias, h_SingleMuon, h_MCDYJets, h_MCMinBias]:
                
            # for i in range(0, h.GetNbinsX() + 1):  # ROOT bins start at 1
            #     I = h.GetBinContent(i)
            #     x_low = h.GetBinLowEdge(i)
            #     # print(f"Bin {i}: I = {I}, x_low = {x_low}")

            #     # for negatives
            #     if I < 0 or x_low < 0:
            #         new_val = 0.0
            #     else:
            #         new_val = math.sqrt((1.0 / (2 * math.pi)) * x_low)

            #     # print(f"Bin {i}: new_val = {new_val}")
                    

            #     h.SetBinContent(i, I)

            # print(f"Before rebinning: {h.GetName()} has {h.GetNbinsX()} bins")

            nbins = h.GetNbinsX()

            edges = []

            for i in range(1, nbins+2):     
                edge = h.GetBinLowEdge(i)
                edges.append(math.sqrt(edge/(2*math.pi)))

            h_new = ROOT.TH1D(
                h.GetName()+"_b",
                h.GetTitle(),
                nbins,
                array.array('d', edges)
            )

            for i in range(1, nbins+1):
                h_new.SetBinContent(i, h.GetBinContent(i))
                h_new.SetBinError(i, h.GetBinError(i))

        NormaliseHist(h_MinBias)
        NormaliseHist(h_SingleMuon)
        NormaliseHist(h_MCDYJets)
        NormaliseHist(h_MCMinBias)

        colour = colours[len(ratio_data_hists) % len(colours)]

        ratio_SingleMuon = h_SingleMuon.Clone(f"ratio_quantile_all_data_{var}")
        ratio_SingleMuon.Divide(h_MinBias)
        ratio_SingleMuon.SetLineColor(colour)
        ratio_SingleMuon.SetLineWidth(2)

        ratio_MCDYJets = h_MCDYJets.Clone(f"ratio_quantile_all_mc_{var}")
        ratio_MCDYJets.Divide(h_MCMinBias)
        ratio_MCDYJets.SetLineColor(colour)
        ratio_MCDYJets.SetLineWidth(2)
        ratio_MCDYJets.SetLineStyle(2)

        ratio_data_hists.append((var, label, ratio_SingleMuon))
        ratio_mc_hists.append((var, label, ratio_MCDYJets))

    if not ratio_data_hists:
        print("Warning: no valid histograms were produced for all-together quantile plot")
        return

    canvas = ROOT.TCanvas("c_quantile_all_together", "", 800, 700)
    canvas.cd()
    canvas.SetBottomMargin(0.13)
    canvas.SetRightMargin(0.25)
    canvas.SetLogy()

    pad1 = ROOT.TPad("pad1_all_together", "pad1", 0, 0.32, 1, 1)
    pad1.SetBottomMargin(0.05)
    pad1.SetRightMargin(0.25)
    pad1.SetLogy()
    pad1.Draw()

    pad2 = ROOT.TPad("pad2_all_together", "pad2", 0, 0, 1, 0.35)
    pad2.SetTopMargin(0.05)
    pad2.SetBottomMargin(0.35)
    pad2.SetRightMargin(0.25)
    pad2.SetGridy()
    pad2.Draw()

    first_ratio = ratio_data_hists[0][2]
    max_val = max(max(r.GetMaximum(), m.GetMaximum()) for (_, _, r), (_, _, m) in zip(ratio_data_hists, ratio_mc_hists))

    first_ratio.GetXaxis().SetTitle("impact parameter b")
    first_ratio.GetYaxis().SetTitle("DY/ZeroBias")
    first_ratio.GetXaxis().SetTitleSize(0.05)
    first_ratio.GetXaxis().SetTitleOffset(0.5)
    first_ratio.GetXaxis().SetLabelSize(0.05)
    first_ratio.GetXaxis().SetTickLength(0.03)
    first_ratio.GetYaxis().SetTitleSize(0.05)
    first_ratio.GetYaxis().SetLabelSize(0.05)
    first_ratio.GetYaxis().SetTitleOffset(0.9)
    first_ratio.SetMaximum(max_val * 1.2)
    pad1.cd()
    first_ratio.Draw("hist e")

    ratio_mc_hists[0][2].Draw("hist e same")

    for _, _, ratio in ratio_data_hists[1:]:
        ratio.Draw("hist e same")
    for _, _, ratio in ratio_mc_hists[1:]:
        ratio.Draw("hist e same")

    pad2.cd()
    for (var, label, ratio_data), (_, _, ratio_mc) in zip(ratio_data_hists, ratio_mc_hists):
        ratio = ratio_data.Clone(f"ratio_final_all_together_{var}")
        ratio.Divide(ratio_mc)
        ratio.SetLineColor(colours[len(ratio_final_hists) % len(colours)])
        ratio.SetMarkerColor(colours[len(ratio_final_hists) % len(colours)])
        ratio.SetMarkerStyle(20)
        ratio.SetMarkerSize(0.8)
        ratio.GetXaxis().SetTitle("impact parameter b")
        ratio.GetXaxis().SetTitleSize(0.1)
        ratio.GetXaxis().SetTitleOffset(1.4)
        ratio.GetXaxis().SetLabelSize(0.1)
        ratio.GetXaxis().SetTickLength(0.07)
        ratio.GetYaxis().SetTitle("Data/MC")
        ratio.GetYaxis().SetTitleSize(0.1)
        ratio.GetYaxis().SetLabelSize(0.1)
        ratio.GetYaxis().SetTitleOffset(0.5)
        ratio.SetMinimum(0.7)
        ratio.SetMaximum(1.8)
        ratio_final_hists.append(ratio)
        

        if var == ratio_final_hists[0][0]:  # Only draw the first ratio to set axes and labels
            ratio.Draw("pe")
        else:
            ratio.Draw("pe same")


    canvas.cd()

    legendVars = ROOT.TLegend(0.76, 0.58, 0.96, 0.9)
    legendStats = ROOT.TLegend(0.76, 0.51, 0.96, 0.58)
    dummy = ROOT.TObject()
    for legend in [legendVars, legendStats]:
        legend.SetBorderSize(0)
        legend.SetFillStyle(0)
        legend.SetTextSize(0.019)
        legend.SetMargin(0.2)
        
    legend_Data = ROOT.TLine(0.0, 0.0, 0.5, 0.0)
    legend_Data.SetLineColor(ROOT.kBlack)
    legend_Data.SetLineWidth(2)
    legend_Data.SetLineStyle(1)

    legend_MC = ROOT.TLine(0.0, 0.0, 0.5, 0.0)
    legend_MC.SetLineColor(ROOT.kBlack)
    legend_MC.SetLineWidth(2)
    legend_MC.SetLineStyle(2)

    for (var, label, ratio_data), (_, _, ratio_mc) in zip(ratio_data_hists, ratio_mc_hists):
        legendVars.AddEntry(ratio_data, f"{label}", "lf")
        # legend.AddEntry(ratio_mc, f"{label} (MC)", "l")

    legendStats.AddEntry(legend, "#bf{Data}", "l")

    # legendStats.AddEntry(dummy, f"DY ({(selectedEvents['SingleMuon'][0]/totalEvents['SingleMuon'][0]) * 100:.2f}%, {(selectedEvents['SingleMuon'][1]/totalEvents['SingleMuon'][1]) * 100:.2f}%)", "")
    # legendStats.AddEntry(dummy, f"{(selectedEvents['SingleMuon'][0]/totalEvents['SingleMuon'][0]) * 100:.2f}% selected Events", "")
    # legendStats.AddEntry(dummy, f"{(selectedEvents['SingleMuon'][1]/totalEvents['SingleMuon'][1]) * 100:.2f}% selected PFCands", "")

    # legendStats.AddEntry(dummy, f"ZeroBias ({(selectedEvents['MinBias'][0]/totalEvents['MinBias'][0]) * 100:.2f}%, {(selectedEvents['MinBias'][1]/totalEvents['MinBias'][1]) * 100:.2f}%)", "")
    # legendStats.AddEntry(dummy, f"{(selectedEvents['MinBias'][0]/totalEvents['MinBias'][0]) * 100:.2f}% selected Events", "")
    # legendStats.AddEntry(dummy, f"{(selectedEvents['MinBias'][1]/totalEvents['MinBias'][1]) * 100:.2f}% selected PFCands", "")

    legendStats.AddEntry(legend_MC, "#bf{MC}", "l")

    # legendStats.AddEntry(dummy, f"DY ({(selectedEvents['MCDY'][0]/totalEvents['MCDY'][0]) * 100:.2f}%, {(selectedEvents['MCDY'][1]/totalEvents['MCDY'][1]) * 100:.2f}%)", "")
    # legendStats.AddEntry(dummy, f"{(selectedEvents['MCDY'][0]/totalEvents['MCDY'][0]) * 100:.2f}% selected Events", "")
    # legendStats.AddEntry(dummy, f"{(selectedEvents['MCDY'][1]/totalEvents['MCDY'][1]) * 100:.2f}% selected PFCands", "")

    # legendStats.AddEntry(dummy, f"ZeroBias ({(selectedEvents['MCMinBias'][0]/totalEvents['MCMinBias'][0]) * 100:.2f}%, {(selectedEvents['MCMinBias'][1]/totalEvents['MCMinBias'][1]) * 100:.2f}%)", "")
    # legendStats.AddEntry(dummy, f"{(selectedEvents['MCMinBias'][0]/totalEvents['MCMinBias'][0]) * 100:.2f}% selected Events", "")
    # legendStats.AddEntry(dummy, f"{(selectedEvents['MCMinBias'][1]/totalEvents['MCMinBias'][1]) * 100:.2f}% selected PFCands", "")

    legendVars.Draw()
    legendStats.Draw()

    # output_name = f"new_plots/AllVariables_QuantileAllTogether{out_suffix}.pdf"
    # canvas.SaveAs(output_name)

    output_dir = f"new_plots/quantile_binning/{bins}"
    os.makedirs(output_dir, exist_ok=True)

    output_name = f"{output_dir}/AllVariables_QuantileAllTogether{out_suffix}.pdf"
    canvas.SaveAs(output_name)
    canvas.Close()

def Quantile_AllTogether_DiMuonPtCut(df_SingleMuon_var, df_MinBias_var, df_MCDYJets_var, df_MCMinBias_var, variables, pt_cuts, out_suffix, bins):

    def colors_func(n):
        base = [ROOT.kViolet - 6, ROOT.kBlue - 4, ROOT.kGreen + 3, ROOT.kOrange + 5, ROOT.kRed + 1, ROOT.kCyan + 2]
        return [base[i % len(base)] for i in range(n)]
    
    colours = colors_func(len(VARIABLES))

    for pt_index, pt_cut in enumerate(pt_cuts):
        print(f"\nApplying diMuon pT cut: {pt_cut} GeV for all-together quantile plot...")


        ratio_data_hists = []
        ratio_mc_hists = []
        ratio_final_hists = []

        for var_index, var in enumerate(variables):
            if var in ["PFCands_pt", "PFCands_eta", "PFCands_phi", "PFCands_pvAssocQuality"]:
                continue
            colour = colours[var_index % len(colours)]
            

            label = VARIABLES[var]
            binning = BINNING[var]
            y_title = "Number Of Events (normalised)"

            h_tmp_ptr = MakeHist(df_MinBias_var, var, label, y_title, binning, f"h_MinBias_{var}_quantile_all_ptscan_tmp")
            h_tmp = h_tmp_ptr.GetValue()
            total = h_tmp.Integral()
            if total <= 0:
                print(f"Warning: MinBias histogram for '{var}' has zero integral; skipping all-together quantile pT-cut plot")
                continue

            bin_edges = [h_tmp.GetBinLowEdge(1)]
            cdf_values = [0.0]
            cumulative = 0.0
            for i in range(1, h_tmp.GetNbinsX() + 1):
                cumulative += h_tmp.GetBinContent(i)
                edge = h_tmp.GetBinLowEdge(i + 1)
                cdf = cumulative / total if total > 0 else 0.0
                bin_edges.append(edge)
                cdf_values.append(cdf)

            edges_cpp = ", ".join(f"{x:.17g}" for x in bin_edges)
            cdf_cpp = ", ".join(f"{x:.17g}" for x in cdf_values)

            ROOT.gInterpreter.Declare(
                f"""
                namespace {var}InvQMapAllTogetherPtCut{pt_index} {{
                static const std::vector<double> edges = {{{edges_cpp}}};
                static const std::vector<double> cdf = {{{cdf_cpp}}};

                double eval(double x) {{
                    if (edges.empty()) return 0.0;
                    if (x <= edges.front()) return 0.0;
                    if (x >= edges.back()) return 1.0;

                    for (size_t i = 1; i < edges.size(); ++i) {{
                        if (x < edges[i]) {{
                            double x1 = edges[i - 1];
                            double x2 = edges[i];
                            double y1 = cdf[i - 1];
                            double y2 = cdf[i];
                            return y1 + (x - x1) * (y2 - y1) / (x2 - x1);
                        }}
                    }}
                    return 1.0;
                }}
                }}
                """
            )

            h_MCtmp_ptr = MakeHist(df_MCMinBias_var, var, label, y_title, binning, f"h_MCMinBias_{var}_quantile_ptscan_tmp")
            h_MCtmp = h_MCtmp_ptr.GetValue()
            total_MC = h_MCtmp.Integral()
            if total_MC <= 0:
                print(f"Warning: MCMinBias histogram for '{var}' has zero integral; skipping quantile pT-scan plot")
                continue

            bin_edges_MC = [h_MCtmp.GetBinLowEdge(1)]
            cdf_values_MC = [0.0]
            cumulative_MC = 0.0
            for i in range(1, h_MCtmp.GetNbinsX() + 1):
                cumulative_MC += h_MCtmp.GetBinContent(i)
                edge_MC = h_MCtmp.GetBinLowEdge(i + 1)
                cdf_MC = cumulative_MC / total_MC if total_MC > 0 else 0.0
                bin_edges_MC.append(edge_MC)
                cdf_values_MC.append(cdf_MC)

            edges_cpp_MC = ", ".join(f"{x:.17g}" for x in bin_edges_MC)
            cdf_cpp_MC = ", ".join(f"{x:.17g}" for x in cdf_values_MC)

            ROOT.gInterpreter.Declare(
                f"""
                namespace {var}InvQMapAllTogetherPtCutMC{pt_index} {{
                static const std::vector<double> edges = {{{edges_cpp_MC}}};
                static const std::vector<double> cdf = {{{cdf_cpp_MC}}};

                double eval(double x) {{
                    if (edges.empty()) return 0.0;
                    if (x <= edges.front()) return 0.0;
                    if (x >= edges.back()) return 1.0;

                    for (size_t i = 1; i < edges.size(); ++i) {{
                        if (x < edges[i]) {{
                            double x1 = edges[i - 1];
                            double x2 = edges[i];
                            double y1 = cdf[i - 1];
                            double y2 = cdf[i];
                            return y1 + (x - x1) * (y2 - y1) / (x2 - x1);
                        }}
                    }}
                    return 1.0;
                }}
                }}
                """
            )
            df_MinBias_q = df_MinBias_var.Define(f"{var}_invQ_all_pt", f"1.0 - {var}InvQMapAllTogetherPtCut{pt_index}::eval(PFSelection_{var})")
            df_SingleMuon_q = df_SingleMuon_var.Define(f"{var}_invQ_all_pt", f"1.0 - {var}InvQMapAllTogetherPtCut{pt_index}::eval(PFSelection_{var})")
            df_MCDYJets_q = df_MCDYJets_var.Define(f"{var}_invQ_all_pt", f"1.0 - {var}InvQMapAllTogetherPtCutMC{pt_index}::eval(PFSelection_{var})")
            df_MCMinBias_q = df_MCMinBias_var.Define(f"{var}_invQ_all_pt", f"1.0 - {var}InvQMapAllTogetherPtCutMC{pt_index}::eval(PFSelection_{var})")
            
            
            df_SingleMuon_q = DiMuonPtCut(df_SingleMuon_q, pt_cut)
            df_MCDYJets_q = DiMuonPtCut(df_MCDYJets_q, pt_cut)
            
            # Redefining the selected events and PFCands after the diMuon pT cut for Data_DY and MC_DY
            # selectedEvents['SingleMuon'][0] = df_SingleMuon_q.Count().GetValue()
            # selectedEvents['SingleMuon'][1] = df_SingleMuon_q.Sum("PFSelection_nPFCands").GetValue()

            # selectedEvents['MCDY'][0] = df_MCDYJets_q.Count().GetValue()
            # selectedEvents['MCDY'][1] = df_MCDYJets_q.Sum("PFSelection_nPFCands").GetValue()

            plot_column = f"{var}_invQ_all_pt"
            plot_xlabel = "impact parameter b"

            edges = array.array("d", bins)

            h_MinBias_ptr = df_MinBias_q.Histo1D(
                (f"h_MinBias_{var}_quantile_all_ptscan", f"; {plot_xlabel}; {y_title}", len(edges) - 1, edges),
                plot_column,
            )
            h_SingleMuon_ptr = df_SingleMuon_q.Histo1D(
                (f"h_SingleMuon_{var}_quantile_all_ptscan_{pt_index}", f"; {plot_xlabel}; {y_title}", len(edges) - 1, edges),
                plot_column,
            )
            h_MCDYJets_ptr = df_MCDYJets_q.Histo1D(
                (f"h_MCDYJets_{var}_quantile_all_ptscan_{pt_index}", f"; {plot_xlabel}; {y_title}", len(edges) - 1, edges),
                plot_column,
            )
            h_MCMinBias_ptr = df_MCMinBias_q.Histo1D(
                (f"h_MCMinBias_{var}_quantile_all_ptscan_{pt_index}", f"; {plot_xlabel}; {y_title}", len(edges) - 1, edges),
                plot_column,
            )

            h_MinBias = h_MinBias_ptr.GetValue()
            h_SingleMuon = h_SingleMuon_ptr.GetValue()
            h_MCDYJets = h_MCDYJets_ptr.GetValue()
            h_MCMinBias = h_MCMinBias_ptr.GetValue()

            for h in [h_MinBias, h_SingleMuon, h_MCDYJets, h_MCMinBias]:
                
                # for i in range(0, h.GetNbinsX() + 1):  # ROOT bins start at 1
                #     I = h.GetBinContent(i)
                #     x_low = h.GetBinLowEdge(i)
                #     # print(f"Bin {i}: I = {I}, x_low = {x_low}")

                #     # for negatives
                #     if I < 0 or x_low < 0:
                #         new_val = 0.0
                #     else:
                #         new_val = math.sqrt((1.0 / (2 * math.pi)) * x_low)

                #     # print(f"Bin {i}: new_val = {new_val}")
                        

                #     h.SetBinContent(i, I)

                # print(f"Before rebinning: {h.GetName()} has {h.GetNbinsX()} bins")

                nbins = h.GetNbinsX()

                edges = []

                for i in range(1, nbins+2):     
                    edge = h.GetBinLowEdge(i)
                    edges.append(math.sqrt(edge/(2*math.pi)))

                h_new = ROOT.TH1D(
                    h.GetName()+"_b",
                    h.GetTitle(),
                    nbins,
                    array.array('d', edges)
                )

                for i in range(1, nbins+1):
                    h_new.SetBinContent(i, h.GetBinContent(i))
                    h_new.SetBinError(i, h.GetBinError(i))

            NormaliseHist(h_MinBias)
            NormaliseHist(h_SingleMuon)
            NormaliseHist(h_MCDYJets)
            NormaliseHist(h_MCMinBias)

            colour = colours[len(ratio_data_hists) % len(colours)]

            ratio_SingleMuon = h_SingleMuon.Clone(f"ratio_quantile_all_data_{var}_pt{pt_index}")
            ratio_SingleMuon.Divide(h_MinBias)
            ratio_SingleMuon.SetLineColor(colour)
            ratio_SingleMuon.SetLineWidth(2)

            ratio_MCDYJets = h_MCDYJets.Clone(f"ratio_quantile_all_mc_{var}_pt{pt_index}")
            ratio_MCDYJets.Divide(h_MCMinBias)
            ratio_MCDYJets.SetLineColor(colour)
            ratio_MCDYJets.SetLineWidth(2)
            ratio_MCDYJets.SetLineStyle(2)

            ratio = ratio_SingleMuon.Clone(f"ratio_final_all_together_{var}_pt{pt_index}")
            ratio.Divide(ratio_MCDYJets)
            ratio.SetLineColor(colour)
            ratio.SetMarkerColor(colour)
            ratio.SetMarkerStyle(20)
            ratio.SetMarkerSize(0.8)


            ratio_data_hists.append((var, label, ratio_SingleMuon))
            ratio_mc_hists.append((var, label, ratio_MCDYJets))
            ratio_final_hists.append((var, label, ratio))


            print(f"Finished processing variable '{var}' for diMuon pT cut {pt_cut} GeV!")
            
        
        if not ratio_data_hists:
            print(f"Warning: no valid histograms were produced for all-together quantile pT-cut plot (pT < {pt_cut} GeV)")
            continue

        canvas = ROOT.TCanvas(f"c_quantile_all_together_pt_{pt_index}", "", 800, 700)
        canvas.cd()
        canvas.SetBottomMargin(0.13)
        canvas.SetRightMargin(0.22)
        canvas.SetLogy()

        pad1 = ROOT.TPad(f"pad1_{pt_index}GeV", "pad1", 0, 0.32, 1, 1)
        pad1.SetBottomMargin(0.05)
        pad1.SetRightMargin(0.22)
        pad1.SetLogy()
        pad1.Draw()

        pad2 = ROOT.TPad(f"pad2_{pt_index}GeV", "pad2", 0, 0, 1, 0.35)
        pad2.SetTopMargin(0.05)
        pad2.SetBottomMargin(0.35)
        pad2.SetRightMargin(0.22)
        pad2.SetGridy()
        pad2.Draw()

        first_ratio = ratio_data_hists[0][2]
        max_val = max(max(r.GetMaximum(), m.GetMaximum()) for (_, _, r), (_, _, m) in zip(ratio_data_hists, ratio_mc_hists))

        pad1.cd()

        first_ratio.GetXaxis().SetTitle(plot_xlabel)
        first_ratio.GetYaxis().SetTitle("DY/ZeroBias")
        first_ratio.GetXaxis().SetTitleSize(0.05)
        first_ratio.GetXaxis().SetTitleOffset(1.3)
        first_ratio.GetXaxis().SetLabelSize(0.05)
        first_ratio.GetXaxis().SetTickLength(0.03)
        first_ratio.GetYaxis().SetTitleSize(0.05)
        first_ratio.GetYaxis().SetLabelSize(0.05)
        first_ratio.GetYaxis().SetTitleOffset(0.9)
        first_ratio.SetMaximum(max_val * 2)
        first_ratio.Draw("hist e")

        ratio_mc_hists[0][2].Draw("hist e same")

        for _, _, ratio in ratio_data_hists[1:]:
            ratio.Draw("hist e same")
        for _, _, ratio in ratio_mc_hists[1:]:
            ratio.Draw("hist e same")


        pad2.cd()
        for var, label, ratio_final in ratio_final_hists:
            ratio_final.SetMarkerStyle(20)
            ratio_final.SetMarkerSize(0.8)
            ratio_final.GetXaxis().SetTitle(plot_xlabel)
            ratio_final.GetXaxis().SetTitleSize(0.1)
            ratio_final.GetXaxis().SetTitleOffset(1.3)
            ratio_final.GetXaxis().SetLabelSize(0.1)
            ratio_final.GetXaxis().SetTickLength(0.07)
            ratio_final.GetYaxis().SetTitle("Data/MC")
            ratio_final.GetYaxis().SetTitleSize(0.1)
            ratio_final.GetYaxis().SetLabelSize(0.1)
            ratio_final.GetYaxis().SetTitleOffset(0.5)
            ratio_final.SetMinimum(0.7)
            ratio_final.SetMaximum(2)

            if var == ratio_final_hists[0][0]:
                ratio_final.Draw("pe")
            else:
                ratio_final.Draw("pe same")



        pad1.cd()

        legendVars = ROOT.TLegend(0.785, 0.3, 0.935, 0.9)
        legendStats = ROOT.TLegend(0.45, 0.65, 0.935, 0.89)
        dummy = ROOT.TObject()
        for legend in (legendVars, legendStats):
            legend.SetBorderSize(0)
            legend.SetFillStyle(0)
            legend.SetTextSize(0.026)
            legend.SetMargin(0.2)
        legendStats.SetTextSize(0.044)
        legendStats.SetMargin(0.11)
        legendVars.SetTextSize(0.045)

        legend_Data = ROOT.TLine(0.0, 0.0, 0.5, 0.0)
        legend_Data.SetLineColor(ROOT.kBlack)
        legend_Data.SetLineWidth(2)
        legend_Data.SetLineStyle(1)

        legend_MC = ROOT.TLine(0.0, 0.0, 0.5, 0.0)
        legend_MC.SetLineColor(ROOT.kBlack)
        legend_MC.SetLineWidth(2)
        legend_MC.SetLineStyle(2)

        for (var, label, ratio_data), (_, _, ratio_mc) in zip(ratio_data_hists, ratio_mc_hists):
            legendVars.AddEntry(ratio_data, f"{label}", "lf")



        legendStats.AddEntry(legend_Data, "#bf{Data}", "l")

        # legendStats.AddEntry(dummy, f"DY ({(selectedEvents['SingleMuon'][0]/totalEvents['SingleMuon'][0]) * 100:.2f}%, {(selectedEvents['SingleMuon'][1]/totalEvents['SingleMuon'][1]) * 100:.2f}%)", "")
        # legendStats.AddEntry(dummy, f"{(selectedEvents['SingleMuon'][0]/totalEvents['SingleMuon'][0]) * 100:.2f}% selected Events", "")
        # legendStats.AddEntry(dummy, f"{(selectedEvents['SingleMuon'][1]/totalEvents['SingleMuon'][1]) * 100:.2f}% selected PFCands", "")

        # legendStats.AddEntry(dummy, f"ZeroBias ({(selectedEvents['MinBias'][0]/totalEvents['MinBias'][0]) * 100:.2f}%, {(selectedEvents['MinBias'][1]/totalEvents['MinBias'][1]) * 100:.2f}%)", "")
        # legendStats.AddEntry(dummy, f"{(selectedEvents['MinBias'][0]/totalEvents['MinBias'][0]) * 100:.2f}% selected Events", "")
        # legendStats.AddEntry(dummy, f"{(selectedEvents['MinBias'][1]/totalEvents['MinBias'][1]) * 100:.2f}% selected PFCands", "")

        legendStats.AddEntry(legend_MC, "#bf{MC}", "l")

        # legendStats.AddEntry(dummy, f"DY ({(selectedEvents['MCDY'][0]/totalEvents['MCDY'][0]) * 100:.2f}%, {(selectedEvents['MCDY'][1]/totalEvents['MCDY'][1]) * 100:.2f}%)", "")
        # legendStats.AddEntry(dummy, f"{(selectedEvents['MCDY'][0]/totalEvents['MCDY'][0]) * 100:.2f}% selected Events", "")
        # legendStats.AddEntry(dummy, f"{(selectedEvents['MCDY'][1]/totalEvents['MCDY'][1]) * 100:.2f}% selected PFCands", "")

        # legendStats.AddEntry(dummy, f"ZeroBias ({(selectedEvents['MCMinBias'][0]/totalEvents['MCMinBias'][0]) * 100:.2f}%, {(selectedEvents['MCMinBias'][1]/totalEvents['MCMinBias'][1]) * 100:.2f}%)", "")
        # legendStats.AddEntry(dummy, f"{(selectedEvents['MCMinBias'][0]/totalEvents['MCMinBias'][0]) * 100:.2f}% selected Events", "")
        # legendStats.AddEntry(dummy, f"{(selectedEvents['MCMinBias'][1]/totalEvents['MCMinBias'][1]) * 100:.2f}% selected PFCands", "")

        legendStats.AddEntry(dummy, f"p^{{#mu#mu}}_{{T}} < {pt_cut} GeV", "")
        legendStats.AddEntry(dummy, f"86 GeV < m_{{#mu#mu}} < 96 GeV", "")

        legendVars.Draw()
        legendStats.Draw()

        # output_name = f"new_plots/AllVariables_QuantileAllTogether_ZpT{pt_cut}GeV{out_suffix}.pdf"
        # canvas.SaveAs(output_name)

        output_dir = f"new_plots/quantile_binning/{bins}"
        os.makedirs(output_dir, exist_ok=True)

        output_name = f"{output_dir}/AllVariables_QuantileAllTogether_ZpT{pt_cut}GeV{out_suffix}.pdf"
        canvas.SaveAs(output_name)
        canvas.Close()

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

    


def SigmaEff(df_SingleMuon_var, df_MinBias_var, df_MCDYJets_var, df_MCMinBias_var, variables, pt_cuts, out_suffix, bins, b_bins, binweight):

    quantile_bins = array.array("d", bins)

    if b_bins is None:
        # b_bins = array.array("d", np.linspace(0, 1, 50))
        b_bins = array.array("d", np.concatenate([
                                  np.arange(0.00, 0.10, 0.01),
                                  np.arange(0.10, 0.20, 0.01),
                                  np.arange(0.20, 1.05, 0.05)
                                ])
                            )
    else:
        b_bins = array.array("d", b_bins)

    pt_cuts = parse_pt_cuts(pt_cuts)

    def colors_func(n):
        base = [
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
    
    colours = colors_func(len(pt_cuts))

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

        # NormaliseHist(h_MinBias, binweight)
        # NormaliseHist(h_MCMinBias, binweight)

        x_values = []

        sigma_eff_data_values = []
        sigma_eff_mc_values = []
        inv_mass = [(0, 15), (15, 20), (20, 30), (30, 40), (40, 50), (50, 60), (60, 70), (70, 86), (86, 96), (96, 100), (100, 110), (110, 120), (120, 130), (130, 140), (140, 150)]



        for mass in inv_mass:

            print(f"\n\nProcessing DiMuon mass range: {mass[0]} - {mass[1]} GeV...\n")
   
            df_SingleMuon_mass = df_SingleMuon_var.Filter(f"DiMuon_Mass >= {mass[0]} && DiMuon_Mass <= {mass[1]}")
            df_MCDYJets_mass = df_MCDYJets_var.Filter(f"DiMuon_Mass >= {mass[0]} && DiMuon_Mass <= {mass[1]}")

            for index, pt_cut in enumerate(pt_cuts):
            
                canvas.cd()          

                print(f"\n\nProcessing DiMuon pT cut: {pt_cut} GeV...\n")


                if pt_cut is None or len(pt_cuts) == 0:
                    print(f"\n\nNo DiMuon pT cut specified for quantile plot.\n")

                    df_SingleMuon_q = df_SingleMuon_mass
                    df_MCDYJets_q = df_MCDYJets_mass

                else:
                    pt_cut = int(pt_cut)
                    print(f"\n\nApplying DiMuon pT cuts for quantile plot: {pt_cut} GeV...\n")

                    df_SingleMuon_q = DiMuonPtCut(df_SingleMuon_mass, pt_cut)
                    df_MCDYJets_q = DiMuonPtCut(df_MCDYJets_mass, pt_cut)

                    

                df_SingleMuon_q = ApplyQuantileAndIP(df_SingleMuon_q, var, "MB")
                df_MCDYJets_q = ApplyQuantileAndIP(df_MCDYJets_q, var, "MCMB")

            
                colour = colours[index % len(colours)]

                    
                h_SingleMuon_ptr = df_SingleMuon_q.Histo1D((f"h_SingleMuon_{var}_{pt_cut}", f"; {plot_xlabel}; {y_title}", len(b_bins) - 1, b_bins), b_column)
                h_MCDYJets_ptr = df_MCDYJets_q.Histo1D((f"h_MCDYJets_{var}_{pt_cut}", f"; {plot_xlabel}; {y_title}", len(b_bins) - 1, b_bins), b_column)

                h_SingleMuon = h_SingleMuon_ptr.GetValue()
                h_MCDYJets = h_MCDYJets_ptr.GetValue()

                # NormaliseHist(h_SingleMuon, binweight)
                # NormaliseHist(h_MCDYJets, binweight)



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




                # Calculate the integral of DY/MinBias for Data and MC
                integral_Data = 0
                integral_MC = 0



                # for ratio_hists in [ratio_Data, ratio_MC]:

                #     for i in range(1, ratio_hists.GetNbinsX()+1):

                #         content = ratio_hists.GetBinContent(i)
                #         width = ratio_hists.GetBinWidth(i)

                #         if ratio_hists == ratio_Data:
                #             integral_Data += content * content * width * width
                #         else:
                #             integral_MC += content * content * width * width





                # for i in range(1, ratio_Data.GetNbinsX() + 1):

                #     b_low = ratio_Data.GetBinLowEdge(i)
                #     b_high = b_low + ratio_Data.GetBinWidth(i)

                #     delta_b2 = b_high**2 - b_low**2

                #     content_Data = ratio_Data.GetBinContent(i)
                #     content_MC = ratio_MC.GetBinContent(i)

                #     integral_Data += content_Data**2 * delta_b2
                #     integral_MC += content_MC**2 * delta_b2


                # # Calculate sigma_eff for Data and MC
                # sigma_eff_Data = (sigma0 * sigma0) / (integral_Data) if integral_Data != 0 else 0
                # sigma_eff_MC = (sigma0 * sigma0) / (integral_MC) if integral_MC != 0 else 0



            
            normalization_Data = 0.0
            normalization_MC = 0.0
            integral_Data = 0.0
            integral_MC = 0.0

            for i in range(1, ratio_Data.GetNbinsX() + 1):

                b_low = ratio_Data.GetBinLowEdge(i)
                b_high = ratio_Data.GetBinLowEdge(i) + ratio_Data.GetBinWidth(i)

                # Calculate the width each bin
                width = np.pi * (b_high**2 - b_low**2)

                # Enhancement factor (i.e. DY/MinBias) in each bin of the ratio histogram 
                E_Data = ratio_Data.GetBinContent(i)
                E_MC = ratio_MC.GetBinContent(i)

                # Calculate the normalization and integral for Data and MC
                normalization_Data += width * E_Data
                normalization_MC += width * E_MC

                integral_Data += width * E_Data**2
                integral_MC += width * E_MC**2

            sigma_eff_Data = (normalization_Data / integral_Data if integral_Data != 0 else 0) * sigma0
            sigma_eff_MC = (normalization_MC / integral_MC if integral_MC != 0 else 0) * sigma0

            # sigma_eff_Data = (normalization_Data / integral_Data if integral_Data != 0 else 0)
            # sigma_eff_MC = (normalization_MC / integral_MC if integral_MC != 0 else 0)

            sigma_eff_data_values.append(sigma_eff_Data)
            sigma_eff_mc_values.append(sigma_eff_MC)
                    
                        





        print(f"\n\nSigma_eff values for Data: {sigma_eff_data_values}")
        print(f"\n\nSigma_eff values for MC: {sigma_eff_mc_values}\n\n")

        # print(len(inv_mass))
        # print(len(sigma_eff_data_values))

        inv_mass_centers = [0.5 * (a + b) for a, b in inv_mass]

        mass_edges = sorted(set(
            edge for bin_range in inv_mass for edge in bin_range
        ))

        fig, axes = plt.subplots(1, 2, figsize=(16, 6))

        # Data
        axes[0].grid(zorder=0)

        for edge in mass_edges:
            axes[0].axvline(
                edge,
                linestyle="--",
                linewidth=1,
                color="gray",
                zorder=1
            )

        axes[0].scatter(
            inv_mass_centers,
            sigma_eff_data_values,
            marker='o',
            label='Data DY/MinBias',
            color='blue',
            zorder=3
        )

        axes[0].set_xlabel(fr'$m_{{\mu\mu}}$ [GeV]')
        axes[0].set_ylabel(
            fr'$\frac{{\sigma_{{\mathrm{{eff}}}}}}{{\sigma_{{0}}}}$',
            fontsize=20
        )
        axes[0].set_xticks(mass_edges)
        axes[0].legend(
            title=f'{VARIABLESFORPYTHON[var]}',
            loc='upper left'
        )

 

        # MC
        axes[1].grid(zorder=0)

        for edge in mass_edges:
            axes[1].axvline(
                edge,
                linestyle="--",
                linewidth=1,
                color="gray",
                zorder=1
            )

        axes[1].scatter(
            inv_mass_centers,
            sigma_eff_mc_values,
            marker='o',
            label='MC DY/MinBias',
            color='red',
            zorder=3
        )

        axes[1].set_xlabel(fr'$m_{{\mu\mu}}$ [GeV]')
        axes[1].set_xticks(mass_edges)
        axes[1].legend(
            title=f'{VARIABLESFORPYTHON[var]}',
            loc='upper left'
        )

        axes[0].set_ylim(0, max(sigma_eff_data_values) * 1.1)
        axes[1].set_ylim(0, max(sigma_eff_mc_values) * 1.1)

   

        plt.tight_layout()

        output_dir = f"new_plots/sigma_eff/{var}_SigmaEff{out_suffix}.pdf"
        plt.savefig(output_dir)
        print(f"Saved plot: {output_dir}")

        plt.show()




        # output_dir = f"new_plots/sigma_eff"
        # os.makedirs(output_dir, exist_ok=True)

        # output_name = f"{output_dir}/{var}_SigmaEff{out_suffix}.pdf"
        # canvas.SaveAs(output_name)

        canvas.Close()



def parse_args():
    parser = argparse.ArgumentParser(
        description="Combined plotting driver for NanoAOD PF-candidate studies"
    )
    parser.add_argument(
        "--mode",
        choices=["compare", "compare-quantilebinning", "ptscan", "ptscan-quantilebinning", "quantile", "quantile-ptscan", "quantile-all", "DYMinBias", "quantile-all-ptscan", "quantiles", "momentumfractions", "mllyll", "sigmaeff", "all"],
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
        "--charge",
        type=int,
        default=1,
        help="Absolute PF candidate charge to select (default: 1)",
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
        "--output-suffix",
        default="",
        help="Optional suffix appended to output plot filenames",
    )
    parser.add_argument(
        "--quantile-bins",
        type=float,
        nargs="+",
        default=[0, 0.25, 0.5, 0.75, 1],
        help="Custom bin edges for quantile histograms",
    )
    parser.add_argument(
        "--b-bins",
        type=float,
        nargs="+",
        default=None,
        help="Custom bin edges for impact parameter histograms",
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

    if args.mode in ["compare", "all"]:
        Plot_CompareTriggers(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias, args.vars, args.output_suffix)

    if args.mode in ["compare-quantilebinning", "all"]:
        Plot_CompareTriggers_QuantileBinning(
            df_SingleMuon,
            df_MinBias,
            df_MCDYJets,
            df_MCMinBias,
            args.vars,
            args.output_suffix,
            # totalEvents,
            # selectedEvents,
            args.quantile_bins,
            args.quantile_reference,
        )

    if args.mode in ["ptscan", "all"]:
        Plot_DiMuonPtCut(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias, args.vars, args.pt_cuts, args.output_suffix)

    if args.mode in ["ptscan-quantilebinning", "all"]:
        Plot_DiMuonPtCut_QuantileBinning(
            df_SingleMuon,
            df_MinBias,
            df_MCDYJets,
            df_MCMinBias,
            args.vars,
            args.pt_cuts,
            args.output_suffix,
            # totalEvents,
            # selectedEvents,
            args.quantile_bins,
            args.quantile_reference,
        )

    if args.mode in ["quantile", "quantiles", "all"]:
        QuantilePerObservable(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias, args.vars, args.output_suffix, args.quantile_bins, args.b_bins, args.pt_cuts, args.binweight)

    if args.mode in ["DYMinBias", "quantiles", "all"]:    
        DYMinBiasPerObservableRatio(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias, args.vars, args.output_suffix, args.quantile_bins, args.b_bins, args.pt_cuts, args.binweight)

    if args.mode in ["quantile-ptscan", "quantiles", "all"]:
        Quantile_DiMuonPtCut(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias, args.vars, args.pt_cuts, args.output_suffix, args.quantile_bins, args.b_bins)

    if args.mode in ["quantile-all", "quantiles", "all"]:
        Quantile_AllTogether(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias, args.vars, args.output_suffix, args.quantile_bins)

    if args.mode in ["quantile-all-ptscan", "quantiles", "all"]:
        Quantile_AllTogether_DiMuonPtCut(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias, args.vars, args.pt_cuts, args.output_suffix, args.quantile_bins)

    if args.mode in ["momentumfractions", "all"]:
        MomentumFractions(df_SingleMuon, df_MCDYJets, args.pt_cuts, args.output_suffix)

    if args.mode in ["mllyll", "all"]:
        MassRapidity(df_SingleMuon, df_MCDYJets, args.pt_cuts, args.output_suffix)

    if args.mode in ["sigmaeff", "all"]:
        SigmaEff(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias, args.vars, args.pt_cuts, args.output_suffix, args.quantile_bins, args.b_bins, args.binweight)

    end = time.time()
    elapsed_time = end - start
    print(f"\nTotal execution time: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main()
