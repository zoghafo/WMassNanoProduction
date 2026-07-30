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

BINNING = {
    "PFCands_pt": [20, 0, 100],
    "PFCands_eta": [20, -2.4, 2.4],
    "PFCands_phi": [20, -3.14, 3.14],
    "PFCands_InvariantMass": [0, 2, 5, 10, 15, 20, 25, 35, 45, 60, 80, 120, 160, 200, 300, 400],
    "PFCands_pvAssocQuality": [9, 0, 9],
    "nPFCands": [3.0, 5.0, 8.0, 11.0, 15.0, 20.0, 27.0, 34.0, 43.0, 54.0, 65.0, 90.0, 130.0, 160.0],
    "PFCands_Ht": [0, 5, 10, 15, 20, 30, 50, 70, 90, 110, 130, 150, 170, 200, 230, 260, 300, 350, 370],
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

    df_SingleMuon_var = df_SingleMuon_var.Filter("DiMuon_Mass > 86 && DiMuon_Mass < 96")
    df_MCDYJets_var = df_MCDYJets_var.Filter("DiMuon_Mass > 86 && DiMuon_Mass < 96")

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

    df_SingleMuon_var = df_SingleMuon_var.Filter("DiMuon_Mass > 86 && DiMuon_Mass < 96")
    df_MCDYJets_var = df_MCDYJets_var.Filter("DiMuon_Mass > 86 && DiMuon_Mass < 96")

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
    df_SingleMuon_var = df_SingleMuon_var.Filter("DiMuon_Mass > 86 && DiMuon_Mass < 96")
    df_MCDYJets_var = df_MCDYJets_var.Filter("DiMuon_Mass > 86 && DiMuon_Mass < 96")

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

    df_SingleMuon_var = df_SingleMuon_var.Filter("DiMuon_Mass > 86 && DiMuon_Mass < 96")
    df_MCDYJets_var = df_MCDYJets_var.Filter("DiMuon_Mass > 86 && DiMuon_Mass < 96") 

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

def QuantilePerObservable(df_SingleMuon_var, df_MinBias_var, df_MCDYJets_var, df_MCMinBias_var, variables, out_suffix,bins, pt_cuts, binweight):


    print(f"Bin weight: {binweight}")

    df_SingleMuon_var = df_SingleMuon_var.Filter("DiMuon_Mass > 86 && DiMuon_Mass < 96")
    df_MCDYJets_var = df_MCDYJets_var.Filter("DiMuon_Mass > 86 && DiMuon_Mass < 96")


    # selEvents_SingleMuon = df_SingleMuon_var.Count().GetValue()
    # sel_Events_MCDYJets = df_MCDYJets_var.Count().GetValue()


    # print(df_SingleMuon_var.Count().GetValue())
    
    # xsec_DY = 0.000001233
    # xsec_MINBIAS = 78.05

    # xsec_JPSI = 0.1180
    # xsec_UPSILON = 0.001636
    # xsec_LOW_MASS_DY = 0.000003144
    # xsec_HIGH_MASS_DY = 0.00000001725
    # xsec_DY_15_86 = 0.000002087
    # xsec_DY_96_120 = 0.0000000945
    # xsec_INEL = 56.42

    # xsec_ratioDYMinBias = xsec_DY / xsec_MINBIAS
    # xsec_ratioDYINEL = xsec_DY / xsec_INEL

    # Events_DY = df_SingleMuon_var.Count().GetValue() / 317494717
    # PFCands_DY = 361604529 / 481589284679

    # Events_MCDY = df_MCDYJets_var.Count().GetValue() / 96424820
    # PFCands_MCDY = 1131468878 / 134047192083



    # Events_MINBIAS = df_MinBias_var.Count().GetValue() / 69205921
    # PFCands_MINBIAS = 1004173250 / 80429995602

    # Events_MCMINBIAS = df_MCMinBias_var.Count().GetValue() / 499907600
    # PFCands_MCMINBIAS = 7118133993 / 52973764700




    # effEvents_DY = Events_DY / Events_MCDY
    # effEvents_MinBias = Events_MINBIAS / Events_MCMINBIAS


    # effEvents_ratioDYMinBias = effEvents_DY / effEvents_MinBias





    pt_cuts = parse_pt_cuts(pt_cuts)

    colours = [ROOT.kViolet - 6, ROOT.kBlue - 4, ROOT.kGreen + 3, ROOT.kOrange + 5, ROOT.kRed + 1]

    for var in variables:
        if var in ["PFCands_pt", "PFCands_eta", "PFCands_phi", "PFCands_pvAssocQuality"]:
            continue

        label = VARIABLES[var]
        binning = BINNING[var]
        y_title = "Cumulative Distribution Function (CDF)"

        h_tmp_ptr = MakeHist(df_MinBias_var, var, label, y_title, binning, f"h_MinBias_{var}_quantile_tmp")
        h_tmp = h_tmp_ptr.GetValue()
        total = h_tmp.Integral()

        print(
            f"\n\n{var} MB: range = [{h_tmp.GetXaxis().GetXmin()},",",{h_tmp.GetXaxis().GetXmax()}]\n",
            f"underflow = {h_tmp.GetBinContent(0)}\n",
            f"overflow = {h_tmp.GetBinContent(h_tmp.GetNbinsX() + 1)}\n",
            f"Integral = {h_tmp.Integral()}\n",
            f"Total events = {df_MinBias_var.Count().GetValue()}\n\n",
        )

        if total > 0:
            underflow_frac = h_tmp.GetBinContent(0) / total
            overflow_frac = h_tmp.GetBinContent(h_tmp.GetNbinsX() + 1) / total
            if underflow_frac > 0 or overflow_frac > 0:
                print(
                    f"Warning: {var} MinBias histogram has {underflow_frac:.3%} underflow and "
                    f"{overflow_frac:.3%} overflow; these events are clipped to q=1 and q=0, respectively."
                )

        MBupper_edge = h_tmp.GetXaxis().GetXmax()


        


        if total <= 0:
            print(f"Warning: MinBias histogram for '{var}' has zero integral; skipping quantile plot")
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

        
        # print numeric variable ranges corresponding to each quantile bin
        quantile_bins = bins  # the quantile bin edges passed into the function
        print(f"Quantile numeric ranges for {var}:")
        for qi in range(len(quantile_bins) - 1):
            q_low = quantile_bins[qi]
            q_high = quantile_bins[qi + 1]
            # map quantile interval [q_low, q_high] in 1-F_MB to CDF range [1-q_high, 1-q_low]
            cdf_low = 1.0 - q_high
            cdf_high = 1.0 - q_low
            x_low = inverse_cdf_from_hist(h_tmp, cdf_low)
            x_high = inverse_cdf_from_hist(h_tmp, cdf_high)
            if x_low is None or x_high is None:
                print(f"  [{q_low:.3f}, {q_high:.3f}] -> (no events / undefined)")
            else:
                print(f"  [{q_low:.3f}, {q_high:.3f}] -> {x_low:.6g} - {x_high:.6g} (CDF {cdf_low:.3f}-{cdf_high:.3f})")
        

        edges_cpp = ", ".join(f"{x:.17g}" for x in bin_edges)
        cdf_cpp = ", ".join(f"{x:.17g}" for x in cdf_values)

        ROOT.gInterpreter.Declare(
            f"""
            namespace {var}InvQMap {{
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


        h_MCtmp_ptr = MakeHist(df_MCMinBias_var, var, label, y_title, binning, f"h_MCMinBias_{var}_quantile_tmp")
        h_MCtmp = h_MCtmp_ptr.GetValue()
        total_MC = h_MCtmp.Integral()

        MCMBupper_edge = h_MCtmp.GetXaxis().GetXmax()


        print(
            f"\n\n{var} MC MB: range = [{h_MCtmp.GetXaxis().GetXmin()},",",{h_MCtmp.GetXaxis().GetXmax()}]\n",
            f"underflow = {h_MCtmp.GetBinContent(0)}\n",
            f"overflow = {h_MCtmp.GetBinContent(h_MCtmp.GetNbinsX() + 1)}\n",
            f"Integral = {h_MCtmp.Integral()}\n",
            f"Total events = {df_MCMinBias_var.Count().GetValue()}\n\n",
        )

        if total_MC > 0:
            underflow_frac_MC = h_MCtmp.GetBinContent(0) / total_MC
            overflow_frac_MC = h_MCtmp.GetBinContent(h_MCtmp.GetNbinsX() + 1) / total_MC
            if underflow_frac_MC > 0 or overflow_frac_MC > 0:
                print(
                    f"Warning: {var} MC MinBias histogram has {underflow_frac_MC:.3%} underflow and "
                    f"{overflow_frac_MC:.3%} overflow; these events are clipped to q=1 and q=0, respectively."
                )


        if total_MC <= 0:
            print(f"Warning: MCMinBias histogram for '{var}' has zero integral; skipping quantile plot")
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
            namespace {var}InvQMapMC {{
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

        df_MinBias_q = df_MinBias_var.Define(f"{var}_invQ", f"1.0 - {var}InvQMap::eval(PFSelection_{var})")
        df_MCMinBias_q = df_MCMinBias_var.Define(f"{var}_invQ", f"1.0 - {var}InvQMap::eval(PFSelection_{var})")

        

        plot_column = f"{var}_invQ"
        plot_xlabel = f"q = 1 - F_{{MB}}({label})"
        # plot_xlabel = "impact parameter b"


        quantile_edges = array.array("d", bins)

        # b_max = math.sqrt(1.0 / (2.0 * math.pi))
        # b_max = 2 # hard-sphere approximation

        # b_edges = (
        #     [i * 0.005 for i in range(21)]              # b = 0.000 ... 0.100
        #     + [0.10 + i * 0.02 for i in range(1, 15)]   # b = 0.120 ... 0.380
        #     + [b_max]
        # )
        # b_edges = array.array("d", b_edges)
        b_column = f"{var}_b"



        # df_MinBias_q = df_MinBias_var.Define(b_column, f"TMath::Sqrt({var}_invQ / (2.0 * TMath::Pi()))")
        # df_MCMinBias_q = df_MCMinBias_var.Define(b_column, f"TMath::Sqrt({var}_invQ / (2.0 * TMath::Pi()))")
        df_MinBias_q = df_MinBias_q.Define(b_column, f"2 * TMath::Sqrt({var}_invQ)")
        df_MCMinBias_q = df_MCMinBias_q.Define(b_column, f"2 * TMath::Sqrt({var}_invQ)")

        # df_MinBias_q.Display([f"{var}_invQ", f"{var}_b"], 20).Print()




        h_MinBias_ptr = df_MinBias_q.Histo1D(
                (f"h_MinBias_{var}_quantile", f"; {plot_xlabel}; {y_title}", len(quantile_edges) - 1, quantile_edges),
                plot_column,
            )
        h_MCMinBias_ptr = df_MCMinBias_q.Histo1D(
                (f"h_MCMinBias_{var}_quantile", f"; {plot_xlabel}; {y_title}", len(quantile_edges) - 1, quantile_edges),
                plot_column,
            )






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

        legend_var = ROOT.TLegend(0.5, 0.73, 0.73, 0.92)
        legend_DataMC = ROOT.TLegend(0.73, 0.65, 0.89, 0.92)
        
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
        legend_DataMC.AddEntry(dummyData, f"#color[{ROOT.kBlack}]{{#bf{{Data}}}}", "l")
        legend_DataMC.AddEntry(dummyMC, f"#color[{ROOT.kBlack}]{{#bf{{MC}}}}", "l")
        legend_DataMC.AddEntry(dummy, f"#color[{ROOT.kViolet - 6}]{{#bf{{DY}}}}", "")
        legend_DataMC.AddEntry(dummy, f"#color[{ROOT.kOrange + 5}]{{#bf{{MinBias}}}}", "")

        legend_var.AddEntry(dummy, f"#color[{ROOT.kBlack}]{{86 GeV < m_{{#mu#mu}} < 96 GeV}}", "")



        canvas.cd()
        pad1.cd()



        h_MinBias = h_MinBias_ptr.GetValue()
        h_MCMinBias = h_MCMinBias_ptr.GetValue()

        h_MinBias_pad2 = h_MinBias.Clone(f"h_MinBias_{var}_quantile_pad2")
        h_MCMinBias_pad2 = h_MCMinBias.Clone(f"h_MCMinBias_{var}_quantile_pad2")



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
            h_MinBias.GetYaxis().SetTitle("Density #frac{1}{N} #frac{dN}{db} (normalised)")
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




        MinBias_hists = []

        for h in [h_MinBias_pad2, h_MCMinBias_pad2]:

            nbins = h.GetNbinsX()

            edges = []
            for i in range(1, nbins+2):
                q = h.GetXaxis().GetBinLowEdge(i)
                # edges.append(math.sqrt(q/(2*math.pi)))
                edges.append(2 * math.sqrt(q))
            print(f"Edges for {h.GetName()}: {edges}")

            h_new = ROOT.TH1D(
                h.GetName()+"_b",
                h.GetTitle(),
                nbins,
                array.array("d", edges)
            )

            for i in range(1, nbins+1):
                h_new.SetBinContent(i, h.GetBinContent(i))
                h_new.SetBinError(i, h.GetBinError(i))

            

            # # debug: print first few bin stats (raw counts and widths)

            # # enable proper error propagation
            # h_new.Sumw2()
            # for bi in range(1, min(6, nbins+1)):
            #     w = h_new.GetBinWidth(bi)
            #     c = h_new.GetBinContent(bi)
            #     e = h_new.GetBinError(bi)
            #     print(f"DEBUG {h_new.GetName()} bin {bi}: content={c}, error={e}, width={w}, content/width={c/w if w>0 else float('nan')}")

            MinBias_hists.append(h_new)

        h_MinBias_pad2, h_MCMinBias_pad2 = MinBias_hists

        pad2_edges = array.array("d", edges)

        h_MinBias_pad2_2_ptr = df_MinBias_q.Histo1D(
                                                (
                                                    f"h_MinBias_{var}_b",
                                                    ";impact parameter b;Normalised density",
                                                    len(pad2_edges) - 1, pad2_edges
                                                ),
                                                b_column,
                                            )

        h_MCMinBias_pad2_2_ptr = df_MCMinBias_q.Histo1D(
                                                    (
                                                        f"h_MCMinBias_{var}_b",
                                                        ";impact parameter b;Normalised density",
                                                        len(pad2_edges) - 1, pad2_edges
                                                    ),
                                                    b_column,
                                                )

        h_MinBias_pad2_2 = h_MinBias_pad2_2_ptr.GetValue()
        h_MCMinBias_pad2_2 = h_MCMinBias_pad2_2_ptr.GetValue()


        for i in range(1, h_MinBias_pad2.GetNbinsX() + 1):
            print(f"1 Bin number: {i}, bin low edge: {h_MinBias_pad2.GetXaxis().GetBinLowEdge(i)}, bin content: {h_MinBias_pad2.GetBinContent(i)}")
            print(f"2 Bin number: {i}, bin low edge: {h_MinBias_pad2_2.GetXaxis().GetBinLowEdge(i)}, bin content: {h_MinBias_pad2_2.GetBinContent(i)}\n")

        NormaliseHist(h_MinBias_pad2, binweight)
        NormaliseHist(h_MCMinBias_pad2, binweight)

        NormaliseHist(h_MinBias_pad2_2, binweight)
        NormaliseHist(h_MCMinBias_pad2_2, binweight)


        canvas.cd()
        pad2.cd()

        h_MinBias_pad2.SetStats(0)
        h_MinBias_pad2.SetLineColor(ROOT.kOrange + 5)
        h_MinBias_pad2.SetLineWidth(2)
        h_MinBias_pad2.GetXaxis().SetTitle("impact parameter b")
        h_MinBias_pad2.GetXaxis().SetTitleSize(0.05)
        h_MinBias_pad2.GetXaxis().SetLabelSize(0.05)
        h_MinBias_pad2.GetXaxis().SetTitleOffset(1.2)
        if binweight:
            h_MinBias_pad2.GetYaxis().SetTitle("Density #frac{1}{N} #frac{dN}{db} (normalised)")
        else:
            h_MinBias_pad2.GetYaxis().SetTitle("Number of Events (normalised)")
        h_MinBias_pad2.GetYaxis().SetTitleSize(0.05)
        h_MinBias_pad2.GetYaxis().SetLabelSize(0.05)
        h_MinBias_pad2.GetYaxis().SetTitleOffset(0.8)
        h_MinBias_pad2.GetXaxis().SetRangeUser(0, 2)


        h_MCMinBias_pad2.SetStats(0)
        h_MCMinBias_pad2.SetLineColor(ROOT.kOrange + 5)
        h_MCMinBias_pad2.SetLineWidth(2)
        h_MCMinBias_pad2.SetLineStyle(2)

        h_MinBias_pad2_2.SetStats(0)
        h_MinBias_pad2_2.SetLineColor(ROOT.kGreen + 3)
        h_MinBias_pad2_2.SetLineWidth(1)

        h_MCMinBias_pad2_2.SetStats(0)
        h_MCMinBias_pad2_2.SetLineColor(ROOT.kGreen + 3)
        h_MCMinBias_pad2_2.SetLineWidth(1)
        h_MCMinBias_pad2_2.SetLineStyle(2)

        h_MinBias_pad2.Draw("hist e")
        h_MCMinBias_pad2.Draw("hist e same")
        h_MinBias_pad2_2.Draw("hist e same")
        h_MCMinBias_pad2_2.Draw("hist e same")


        


        for index, pt_cut in enumerate(pt_cuts):
            
            canvas.cd()

            print(f"\n\nProcessing DiMuon pT cut: {pt_cut} GeV...\n")

            df_SingleMuon_beforeptcut = df_SingleMuon_var.Define(f"{var}_invQ", f"1.0 - {var}InvQMap::eval(PFSelection_{var})")
            df_MCDYJets_beforeptcut = df_MCDYJets_var.Define(f"{var}_invQ", f"1.0 - {var}InvQMap::eval(PFSelection_{var})")

            # df_SingleMuon_beforeptcut = df_SingleMuon_beforeptcut.Define(b_column, f"TMath::Sqrt({var}_invQ / (2.0 * TMath::Pi()))")
            # df_SingleMuon_beforeptcut = df_SingleMuon_beforeptcut.Define(b_column, f"TMath::Sqrt({var}_invQ / (2.0 * TMath::Pi()))")
            # df_SingleMuon_beforeptcut = df_SingleMuon_beforeptcut.Define(b_column, f"2 * TMath::Sqrt({var}_invQ)")
            # df_MCDYJets_beforeptcut = df_MCDYJets_beforeptcut.Define(b_column, f"2 * TMath::Sqrt({var}_invQ)")

            



            if pt_cut is None or len(pt_cuts) == 0:
                print(f"\n\nNo DiMuon pT cut specified for quantile plot.\n")

                df_SingleMuon_q = df_SingleMuon_beforeptcut
                df_MCDYJets_q = df_MCDYJets_beforeptcut

            else:
                pt_cut = int(pt_cut)
                print(f"\n\nApplying DiMuon pT cuts for quantile plot: {pt_cut} GeV...\n")

                df_SingleMuon_q = DiMuonPtCut(df_SingleMuon_beforeptcut, pt_cut)
                df_MCDYJets_q = DiMuonPtCut(df_MCDYJets_beforeptcut, pt_cut)

            

            colour = colours[index % len(colours)]

            
            h_SingleMuon_ptr = df_SingleMuon_q.Histo1D(
                (f"h_SingleMuon_{var}_quantile_{pt_cut}GeVCut", f"; {plot_xlabel}; {y_title}", len(quantile_edges) - 1, quantile_edges),
                plot_column,
            )
            h_MCDYJets_ptr = df_MCDYJets_q.Histo1D(
                (f"h_MCDYJets_{var}_quantile_{pt_cut}GeVCut", f"; {plot_xlabel}; {y_title}", len(quantile_edges) - 1, quantile_edges),
                plot_column,
            )

           

            h_SingleMuon = h_SingleMuon_ptr.GetValue()
            h_MCDYJets = h_MCDYJets_ptr.GetValue()

            # print(
            #     "\n\n----------------------------------------\n",
            #     f"{var} DY underflow bin content: {h_SingleMuon.GetBinContent(0)}\n",
            #     f"{var} DY overflow bin content: {h_SingleMuon.GetBinContent(h_SingleMuon.GetNbinsX() + 1)}\n",
            #     f"{var} DY q=0-bin content: {h_SingleMuon.GetBinContent(1)}\n",
            #     f"\n\n{var} MC DY underflow bin content: {h_MCDYJets.GetBinContent(0)}\n",
            #     f"{var} MC DY overflow bin content: {h_MCDYJets.GetBinContent(h_MCDYJets.GetNbinsX() + 1)}\n",
            #     f"{var} MC DY q=0-bin content: {h_MCDYJets.GetBinContent(1)}\n",
            #     "----------------------------------------\n",
            # )

            # print(f"Upper edge of {var} MinBias histogram: {MBupper_edge}\n")
            # print(f"Upper edge of {var} MC MinBias histogram: {MCMBupper_edge}\n")


            # n_DY_total = df_SingleMuon_q.Count().GetValue()
            # n_DY_above = df_SingleMuon_q.Filter(
            #     f"PFSelection_{var} >= {MBupper_edge}"
            # ).Count().GetValue()

            # n_MCDY_total = df_MCDYJets_q.Count().GetValue()
            # n_MCDY_above = df_MCDYJets_q.Filter(
            #     f"PFSelection_{var} >= {MCMBupper_edge}"
            # ).Count().GetValue()

            # print(
            #     f"{var}: DY above CDF range: {n_DY_above}/{n_DY_total} "
            #     f"({100*n_DY_above/n_DY_total:.2f}%)\n"
            # )
            # print(
            #     f"{var}: MC DY above CDF range: {n_MCDY_above}/{n_MCDY_total} "
            #     f"({100*n_MCDY_above/n_MCDY_total:.2f}%)\n\n"
            # )

            # print("DY mapped exactly to q=0:",
            #     df_SingleMuon_q.Filter(f"{var}_invQ == 0.0").Count().GetValue())

            # print("MC DY mapped exactly to q=0:",
            #     df_MCDYJets_q.Filter(f"{var}_invQ == 0.0").Count().GetValue())


            # print("\n----------------------------------------\n\n")


            h_SingleMuon_pad2 = h_SingleMuon.Clone(f"h_SingleMuon_{var}_quantile_pad2_{pt_cut}GeVCut")
            h_MCDYJets_pad2 = h_MCDYJets.Clone(f"h_MCDYJets_{var}_quantile_pad2_{pt_cut}GeVCut")



            NormaliseHist(h_SingleMuon, binweight)
            NormaliseHist(h_MCDYJets, binweight)

            pad1.cd()
            
            h_SingleMuon.SetLineColor(ROOT.kViolet - 6)
            h_SingleMuon.SetMarkerColor(ROOT.kViolet - 6)
            h_SingleMuon.SetLineWidth(2)
            h_SingleMuon.GetXaxis().SetRangeUser(0, 2)

            h_MCDYJets.SetLineColor(ROOT.kViolet - 6)
            h_MCDYJets.SetMarkerColor(ROOT.kViolet - 6)
            h_MCDYJets.SetLineWidth(2)
            h_MCDYJets.SetLineStyle(2)
            h_MCDYJets.GetXaxis().SetRangeUser(0, 2)

     

            h_MinBias.GetYaxis().SetRangeUser(0, max(h_SingleMuon.GetMaximum(), h_MinBias.GetMaximum(), h_MCDYJets.GetMaximum(), h_MCMinBias.GetMaximum()) * 1.2)

            h_SingleMuon.Draw("hist e same")
            h_MCDYJets.Draw("hist e same")






            canvas.cd()
            pad2.cd()

            DY_hists = []

            for h in [h_SingleMuon_pad2, h_MCDYJets_pad2]:

                nbins = h.GetNbinsX()

                edges = []
                for i in range(1, nbins+2):
                    q = h.GetXaxis().GetBinLowEdge(i)
                    # edges.append(math.sqrt(q/(2*math.pi)))
                    edges.append(2 * math.sqrt(q))

                h_new = ROOT.TH1D(
                    h.GetName()+"_b",
                    h.GetTitle(),
                    nbins,
                    array.array("d", edges)
                )

                for i in range(1, nbins+1):
                    h_new.SetBinContent(i, h.GetBinContent(i))
                    h_new.SetBinError(i, h.GetBinError(i))

                DY_hists.append(h_new)

                # # enable proper error propagation and debug-print first bins
                # h_new.Sumw2()
                # for bi in range(1, min(6, nbins+1)):
                #     w = h_new.GetBinWidth(bi)
                #     c = h_new.GetBinContent(bi)
                #     e = h_new.GetBinError(bi)
                #     print(f"DEBUG {h_new.GetName()} bin {bi}: content={c}, error={e}, width={w}, content/width={c/w if w>0 else float('nan')}")

            h_SingleMuon_pad2, h_MCDYJets_pad2 = DY_hists

            # h_SingleMuon_pad2_ptr = df_SingleMuon_q.Histo1D(
            #                                         (
            #                                             f"h_SingleMuon_{var}_b",
            #                                             ";impact parameter b;Normalised density",
            #                                             len(b_edges) - 1,
            #                                             b_edges,
            #                                         ),
            #                                         b_column,
            #                                     )

            # h_MCDYJets_pad2_ptr = df_MCDYJets_q.Histo1D(
            #                                             (
            #                                                 f"h_MCDYJets_{var}_b",
            #                                                 ";impact parameter b;Normalised density",
            #                                                 len(b_edges) - 1,
            #                                                 b_edges,
            #                                             ),
            #                                             b_column,
            #                                         )

            # h_SingleMuon_pad2 = h_SingleMuon_pad2_ptr.GetValue()
            # h_MCDYJets_pad2 = h_MCDYJets_pad2_ptr.GetValue()



            NormaliseHist(h_SingleMuon_pad2, binweight)
            NormaliseHist(h_MCDYJets_pad2, binweight)


            h_SingleMuon_pad2.SetStats(0)
            h_SingleMuon_pad2.SetLineColor(colour)
            h_SingleMuon_pad2.SetMarkerColor(colour)
            h_SingleMuon_pad2.SetLineWidth(2)

    
            h_MCDYJets_pad2.SetStats(0)
            h_MCDYJets_pad2.SetLineColor(colour)
            h_MCDYJets_pad2.SetMarkerColor(colour)
            h_MCDYJets_pad2.SetLineWidth(2)
            h_MCDYJets_pad2.SetLineStyle(2)


            h_MinBias_pad2.GetYaxis().SetRangeUser(0, max(h_SingleMuon_pad2.GetMaximum(), h_MinBias_pad2.GetMaximum(), h_MCDYJets_pad2.GetMaximum(), h_MCMinBias_pad2.GetMaximum(), h_MinBias_pad2_2.GetMaximum()) * 1.3)


            h_SingleMuon_pad2.Draw("hist e same")
            h_MCDYJets_pad2.Draw("hist e same")





            # ratio_SingleMuon.Scale(1 * (xsec_MINBIAS/xsec_DY) * (xsec_INEL/xsec_MINBIAS) * (Events_MINBIAS/Events_DY))
            # ratio_MCDYJets.Scale(1 * (xsec_MINBIAS/xsec_DY) * (xsec_INEL/xsec_MINBIAS) * (Events_MCMINBIAS/Events_MCDY))



   



            # # ---------------------- from Pythia --------------------
            # if pt_cut == 4:

            #     canvas.cd()
            #     pad1.cd()
                
            #     df_pythia = pd.read_hdf("simulated_enhf_vs_impactparam.hdf")

            #     values = df_pythia["values"]
            #     edges = df_pythia["edges"]

            #     index_pythia = 0

            
            #     if var == "PFCands_Ht":
            #         index_pythia = 2
            #     elif var == "PFCands_Pt2sum":
            #         index_pythia = 5
            #     elif var == "PFCands_InvariantMass":
            #         index_pythia = 3
            #     elif var == "nPFCands":
            #         index_pythia = 0
            #     elif var == "PFCands_Psum":
            #         index_pythia = 1
            #     else:
            #         print(f"Variable {var} not found in Pythia data; skipping Pythia overlay.")
            #         continue

            #     bins_new = array.array('d', np.asarray(df_pythia["edges"].iloc[index_pythia], dtype=np.float64))
            #     h_pythia = ROOT.TH1F("h_pythia", "Histogram of values", len(bins_new) - 1, bins_new)

            #     row_values = values.iloc[index_pythia]
            #     row_edges = edges.iloc[index_pythia]


            #     for j in range(len(row_values)):
            #         h_pythia.SetBinContent(j, row_values[j])
            #     # print(f"Set bin {j} content to {row_values[j]}")



            #     # NormaliseHist(h_pythia)

            #     h_pythia.SetLineColor(ROOT.kRed)
            #     h_pythia.SetLineWidth(2)
            #     # h_pythia.SetLineStyle(2)
            #     h_pythia.Draw("hist same")


            #     ratio_MC.SetMaximum(max(ratio_MCDYJets.GetMaximum(), ratio_MC.GetMaximum(), h_pythia.GetMaximum()) * 1.2)
    






            canvas.cd()
            pad1.cd()


            



            # if pt_cut == 4:
            #     legend_var.AddEntry(h_pythia, f"#color[{ROOT.kRed}]{{#bf{{Pythia}}}}", "l")

            # legend_var.AddEntry(dummy, label, "")

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



            legend_DataMC_pad2.AddEntry(dummy, f"#color[{ROOT.kOrange + 5}]{{#bf{{MinBias bTb}}}}", "")
            legend_DataMC_pad2.AddEntry(dummy, f"#color[{ROOT.kGreen + 3}]{{#bf{{MinBias eTe}}}}", "")


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



def DYMinBiasPerObservableRatio(df_SingleMuon_var, df_MinBias_var, df_MCDYJets_var, df_MCMinBias_var, variables, out_suffix,bins, pt_cuts, binweight):

    print(f"Bin weight: {binweight}")

    df_SingleMuon_var = df_SingleMuon_var.Filter("DiMuon_Mass > 86 && DiMuon_Mass < 96")
    df_MCDYJets_var = df_MCDYJets_var.Filter("DiMuon_Mass > 86 && DiMuon_Mass < 96")


    # selEvents_SingleMuon = df_SingleMuon_var.Count().GetValue()
    # sel_Events_MCDYJets = df_MCDYJets_var.Count().GetValue()


    # print(df_SingleMuon_var.Count().GetValue())
    
    # xsec_DY = 0.000001233
    # xsec_MINBIAS = 78.05

    # xsec_JPSI = 0.1180
    # xsec_UPSILON = 0.001636
    # xsec_LOW_MASS_DY = 0.000003144
    # xsec_HIGH_MASS_DY = 0.00000001725
    # xsec_DY_15_86 = 0.000002087
    # xsec_DY_96_120 = 0.0000000945
    # xsec_INEL = 56.42

    # xsec_ratioDYMinBias = xsec_DY / xsec_MINBIAS
    # xsec_ratioDYINEL = xsec_DY / xsec_INEL

    # Events_DY = df_SingleMuon_var.Count().GetValue() / 317494717
    # PFCands_DY = 361604529 / 481589284679

    # Events_MCDY = df_MCDYJets_var.Count().GetValue() / 96424820
    # PFCands_MCDY = 1131468878 / 134047192083



    # Events_MINBIAS = df_MinBias_var.Count().GetValue() / 69205921
    # PFCands_MINBIAS = 1004173250 / 80429995602

    # Events_MCMINBIAS = df_MCMinBias_var.Count().GetValue() / 499907600
    # PFCands_MCMINBIAS = 7118133993 / 52973764700




    # effEvents_DY = Events_DY / Events_MCDY
    # effEvents_MinBias = Events_MINBIAS / Events_MCMINBIAS


    # effEvents_ratioDYMinBias = effEvents_DY / effEvents_MinBias





    pt_cuts = parse_pt_cuts(pt_cuts)

    colours = [ROOT.kOrange + 5, ROOT.kViolet - 6, ROOT.kBlue - 4, ROOT.kGreen + 3, ROOT.kRed + 1]

    for var in variables:
        if var in ["PFCands_pt", "PFCands_eta", "PFCands_phi", "PFCands_pvAssocQuality"]:
            continue

        # print(df_MinBias_var.Filter(f"PFSelection_{var} <= 600 and PFSelection_{var} >= 370").Count().GetValue())
        # print(df_MCMinBias_var.Filter(f"PFSelection_{var} <= 600 and PFSelection_{var} >= 370").Count().GetValue())

        label = VARIABLES[var]
        binning = BINNING[var]
        y_title = "Cumulative Distribution Function (CDF)"

        h_tmp_ptr = MakeHist(df_MinBias_var, var, label, y_title, binning, f"h_MinBias_{var}_quantile_tmp")
        h_tmp = h_tmp_ptr.GetValue()
        total = h_tmp.Integral()
        if total <= 0:
            print(f"Warning: MinBias histogram for '{var}' has zero integral; skipping quantile plot")
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

        
        # print numeric variable ranges corresponding to each quantile bin
        quantile_bins = bins  # the quantile bin edges passed into the function
        print(f"Quantile numeric ranges for {var}:")
        for qi in range(len(quantile_bins) - 1):
            q_low = quantile_bins[qi]
            q_high = quantile_bins[qi + 1]
            # map quantile interval [q_low, q_high] in 1-F_MB to CDF range [1-q_high, 1-q_low]
            cdf_low = 1.0 - q_high
            cdf_high = 1.0 - q_low
            x_low = inverse_cdf_from_hist(h_tmp, cdf_low)
            x_high = inverse_cdf_from_hist(h_tmp, cdf_high)
            if x_low is None or x_high is None:
                print(f"  [{q_low:.3f}, {q_high:.3f}] -> (no events / undefined)")
            else:
                print(f"  [{q_low:.3f}, {q_high:.3f}] -> {x_low:.6g} - {x_high:.6g} (CDF {cdf_low:.3f}-{cdf_high:.3f})")
        

        edges_cpp = ", ".join(f"{x:.17g}" for x in bin_edges)
        cdf_cpp = ", ".join(f"{x:.17g}" for x in cdf_values)

        ROOT.gInterpreter.Declare(
            f"""
            namespace {var}InvQMap {{
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


        h_MCtmp_ptr = MakeHist(df_MCMinBias_var, var, label, y_title, binning, f"h_MCMinBias_{var}_quantile_tmp")
        h_MCtmp = h_MCtmp_ptr.GetValue()
        total_MC = h_MCtmp.Integral()
        if total_MC <= 0:
            print(f"Warning: MCMinBias histogram for '{var}' has zero integral; skipping quantile plot")
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
            namespace {var}InvQMapMC {{
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

        df_MinBias_q = df_MinBias_var.Define(f"{var}_invQ", f"1.0 - {var}InvQMap::eval(PFSelection_{var})")
        df_MCMinBias_q = df_MCMinBias_var.Define(f"{var}_invQ", f"1.0 - {var}InvQMap::eval(PFSelection_{var})")
        plot_column = f"{var}_invQ"
        plot_xlabel = f"q = 1 - F_{{MB}}({label})"
        # plot_xlabel = "impact parameter b"
        b_column = f"{var}_b"


        df_MinBias_q = df_MinBias_q.Define(b_column, f"2 * TMath::Sqrt({var}_invQ)")
        df_MCMinBias_q = df_MCMinBias_q.Define(b_column, f"2 * TMath::Sqrt({var}_invQ)")


        quantile_edges = array.array("d", bins)

        

        h_MinBias_ptr = df_MinBias_q.Histo1D(
                (f"h_MinBias_{var}_quantile", f"; {plot_xlabel}; {y_title}", len(quantile_edges) - 1, quantile_edges),
                plot_column,
            )
        h_MCMinBias_ptr = df_MCMinBias_q.Histo1D(
                (f"h_MCMinBias_{var}_quantile", f"; {plot_xlabel}; {y_title}", len(quantile_edges) - 1, quantile_edges),
                plot_column,
            )


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



        h_MinBias = h_MinBias_ptr.GetValue()
        h_MCMinBias = h_MCMinBias_ptr.GetValue()

        h_MinBias_pad2 = h_MinBias.Clone(f"h_MinBias_{var}_quantile_pad2")
        h_MCMinBias_pad2 = h_MCMinBias.Clone(f"h_MCMinBias_{var}_quantile_pad2")


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

        # h_MinBias.Draw("hist e")
        # h_MCMinBias.Draw("hist e same")

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
        legend_DataMC.AddEntry(h_MinBias, f"#bf{{Data}}", "l")
        legend_DataMC.AddEntry(h_MCMinBias, f"#bf{{MC}}", "l")
        # legend_DataMC.AddEntry(dummyData, f"#color[{ROOT.kBlack}]{{#bf{{Data}}}}", "l")
        # legend_DataMC.AddEntry(dummyMC, f"#color[{ROOT.kBlack}]{{#bf{{MC}}}}", "l")
        # legend_DataMC.AddEntry(dummy, f"#color[{ROOT.kViolet - 6}]{{#bf{{DY}}}}", "")
        # legend_DataMC.AddEntry(dummy, f"#color[{ROOT.kOrange + 5}]{{#bf{{MinBias}}}}", "")
        # legend_DataMC.AddEntry(dummy, f"#bf{{DY/MinBias:}}", "")

        legend_var.AddEntry(dummy, f"#color[{ROOT.kBlack}]{{86 GeV < m_{{#mu#mu}} < 96 GeV}}", "")





        MinBias_hists = []

        for h in [h_MinBias_pad2, h_MCMinBias_pad2]:

            nbins = h.GetNbinsX()

            edges = []
            for i in range(1, nbins+2):
                q = h.GetBinLowEdge(i)
                # edges.append(math.sqrt(q/(2*math.pi)))
                edges.append(2 * math.sqrt(q))
            print(f"Edges for {h.GetName()}: {edges}")

            h_new = ROOT.TH1D(
                h.GetName()+"_b",
                h.GetTitle(),
                nbins,
                array.array("d", edges)
            )

            for i in range(1, nbins+1):
                h_new.SetBinContent(i, h.GetBinContent(i))
                h_new.SetBinError(i, h.GetBinError(i))

            MinBias_hists.append(h_new)

        h_MinBias_pad2, h_MCMinBias_pad2 = MinBias_hists

        pad2_edges = array.array("d", edges)

        h_MinBias_pad2_2_ptr = df_MinBias_q.Histo1D(
                                                (
                                                    f"h_MinBias_{var}_b",
                                                    ";impact parameter b;Normalised density",
                                                    len(pad2_edges) - 1, pad2_edges
                                                ),
                                                b_column,
                                            )

        h_MCMinBias_pad2_2_ptr = df_MCMinBias_q.Histo1D(
                                                    (
                                                        f"h_MCMinBias_{var}_b",
                                                        ";impact parameter b;Normalised density",
                                                        len(pad2_edges) - 1, pad2_edges
                                                    ),
                                                    b_column,
                                                )

  

        h_MinBias_pad2_2 = h_MinBias_pad2_2_ptr.GetValue()
        h_MCMinBias_pad2_2 = h_MCMinBias_pad2_2_ptr.GetValue()

        NormaliseHist(h_MinBias_pad2, binweight)
        NormaliseHist(h_MCMinBias_pad2, binweight)
        NormaliseHist(h_MinBias_pad2_2, binweight)
        NormaliseHist(h_MCMinBias_pad2_2, binweight)


        canvas.cd()
        pad2.cd()

        h_MinBias_pad2.SetStats(0)
        h_MinBias_pad2.SetLineColor(ROOT.kOrange + 5)
        h_MinBias_pad2.SetLineWidth(2)
        h_MinBias_pad2.GetXaxis().SetTitle("impact parameter b")
        h_MinBias_pad2.GetXaxis().SetTitleSize(0.05)
        h_MinBias_pad2.GetXaxis().SetLabelSize(0.05)
        h_MinBias_pad2.GetXaxis().SetTitleOffset(1.2)
        if binweight:
            h_MinBias_pad2.GetYaxis().SetTitle("Density #frac{1}{N} #frac{dN}{db} (normalised)")
        else:
            h_MinBias_pad2.GetYaxis().SetTitle("Number of Events (normalised)")
        h_MinBias_pad2.GetYaxis().SetTitleSize(0.05)
        h_MinBias_pad2.GetYaxis().SetLabelSize(0.05)
        h_MinBias_pad2.GetYaxis().SetTitleOffset(0.8)
        h_MinBias_pad2.GetXaxis().SetRangeUser(0, 2)


        h_MCMinBias_pad2.SetStats(0)
        h_MCMinBias_pad2.SetLineColor(ROOT.kOrange + 5)
        h_MCMinBias_pad2.SetLineWidth(2)
        h_MCMinBias_pad2.SetLineStyle(2)

        
        h_MinBias_pad2_2.SetStats(0)
        h_MinBias_pad2_2.SetLineColor(ROOT.kGreen + 3)
        h_MinBias_pad2_2.SetLineWidth(1)

        h_MCMinBias_pad2_2.SetStats(0)
        h_MCMinBias_pad2_2.SetLineColor(ROOT.kGreen + 3)
        h_MCMinBias_pad2_2.SetLineWidth(1)
        h_MCMinBias_pad2_2.SetLineStyle(2)



        for index, pt_cut in enumerate(pt_cuts):
            
            canvas.cd()

            print(f"\n\nProcessing DiMuon pT cut: {pt_cut} GeV...\n")

            df_SingleMuon_beforeptcut = df_SingleMuon_var.Define(f"{var}_invQ", f"1.0 - {var}InvQMap::eval(PFSelection_{var})")
            df_MCDYJets_beforeptcut = df_MCDYJets_var.Define(f"{var}_invQ", f"1.0 - {var}InvQMap::eval(PFSelection_{var})")

            df_SingleMuon_beforeptcut = df_SingleMuon_beforeptcut.Define(b_column, f"2 * TMath::Sqrt({var}_invQ)")
            df_MCDYJets_beforeptcut = df_MCDYJets_beforeptcut.Define(b_column, f"2 * TMath::Sqrt({var}_invQ)")

            



            if pt_cut is None or len(pt_cuts) == 0:
                print(f"\n\nNo DiMuon pT cut specified for quantile plot.\n")

                df_SingleMuon_q = df_SingleMuon_beforeptcut
                df_MCDYJets_q = df_MCDYJets_beforeptcut

            else:
                pt_cut = int(pt_cut)
                print(f"\n\nApplying DiMuon pT cuts for quantile plot: {pt_cut} GeV...\n")

                df_SingleMuon_q = DiMuonPtCut(df_SingleMuon_beforeptcut, pt_cut)
                df_MCDYJets_q = DiMuonPtCut(df_MCDYJets_beforeptcut, pt_cut)

            

            colour = colours[index % len(colours)]

            # print(df_SingleMuon_var.Filter(f"PFSelection_{var} <= 600 and PFSelection_{var} >= 370").Count().GetValue())
            # print(df_MCDYJets_var.Filter(f"PFSelection_{var} <= 600 and PFSelection_{var} >= 370").Count().GetValue())

            h_SingleMuon_ptr = df_SingleMuon_q.Histo1D(
                (f"h_SingleMuon_{var}_quantile_{pt_cut}GeVCut", f"; {plot_xlabel}; {y_title}", len(quantile_edges) - 1, quantile_edges),
                plot_column,
            )
            h_MCDYJets_ptr = df_MCDYJets_q.Histo1D(
                (f"h_MCDYJets_{var}_quantile_{pt_cut}GeVCut", f"; {plot_xlabel}; {y_title}", len(quantile_edges) - 1, quantile_edges),
                plot_column,
            )

           

            h_SingleMuon = h_SingleMuon_ptr.GetValue()
            h_MCDYJets = h_MCDYJets_ptr.GetValue()

            h_SingleMuon_pad2 = h_SingleMuon.Clone(f"h_SingleMuon_{var}_quantile_pad2_{pt_cut}GeVCut")
            h_MCDYJets_pad2 = h_MCDYJets.Clone(f"h_MCDYJets_{var}_quantile_pad2_{pt_cut}GeVCut")


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

            DY_hists = []

            for h in [h_SingleMuon_pad2, h_MCDYJets_pad2]:

                nbins = h.GetNbinsX()

                edges = []
                for i in range(1, nbins+2):
                    q = h.GetBinLowEdge(i)
                    # edges.append(math.sqrt(q/(2*math.pi)))
                    edges.append(2 * math.sqrt(q))

                h_new = ROOT.TH1D(
                    h.GetName()+"_b",
                    h.GetTitle(),
                    nbins,
                    array.array("d", edges)
                )

                for i in range(1, nbins+1):
                    h_new.SetBinContent(i, h.GetBinContent(i))
                    h_new.SetBinError(i, h.GetBinError(i))

                DY_hists.append(h_new)

            h_SingleMuon_pad2, h_MCDYJets_pad2 = DY_hists


            h_SingleMuon_pad2_2_ptr = df_SingleMuon_q.Histo1D(
                                                    (
                                                        f"h_SingleMuon_{var}_b_{pt_cut}GeVCut",
                                                        ";impact parameter b;Normalised density",
                                                        len(pad2_edges) - 1, pad2_edges
                                                    ),
                                                    b_column,
                                                )
            h_MCDYJets_pad2_2_ptr = df_MCDYJets_q.Histo1D(
                                                    (
                                                        f"h_MCDYJets_{var}_b_{pt_cut}GeVCut",
                                                        ";impact parameter b;Normalised density",
                                                        len(pad2_edges) - 1, pad2_edges
                                                    ),
                                                    b_column,
                                                )

            
            h_SingleMuon_pad2_2 = h_SingleMuon_pad2_2_ptr.GetValue()
            h_MCDYJets_pad2_2 = h_MCDYJets_pad2_2_ptr.GetValue()

            NormaliseHist(h_SingleMuon_pad2, binweight)
            NormaliseHist(h_MCDYJets_pad2, binweight)
            NormaliseHist(h_SingleMuon_pad2_2, binweight)
            NormaliseHist(h_MCDYJets_pad2_2, binweight)


            h_DYMinBias_pad2 = h_SingleMuon_pad2.Clone(f"h_DYMinBias_{var}_quantile_pad2_{pt_cut}GeVCut")
            h_DYMinBias_pad2.Divide(h_MinBias_pad2)
            h_MCDYMinBias_pad2 = h_MCDYJets_pad2.Clone(f"h_MCDYMinBias_{var}_quantile_pad2_{pt_cut}GeVCut")
            h_MCDYMinBias_pad2.Divide(h_MCMinBias_pad2)

            h_DYMinBias_pad2_2 = h_SingleMuon_pad2_2.Clone(f"h_DYMinBias_{var}_quantile_pad2_2_{pt_cut}GeVCut")
            h_DYMinBias_pad2_2.Divide(h_MinBias_pad2_2)
            h_MCDYMinBias_pad2_2 = h_MCDYJets_pad2_2.Clone(f"h_MCDYMinBias_{var}_quantile_pad2_2_{pt_cut}GeVCut")
            h_MCDYMinBias_pad2_2.Divide(h_MCMinBias_pad2_2)

            h_DYMinBias_pad2.SetStats(0)
            h_DYMinBias_pad2.SetLineColor(colour)
            h_DYMinBias_pad2.SetMarkerColor(colour)
            h_DYMinBias_pad2.SetLineWidth(2)
            h_DYMinBias_pad2.GetXaxis().SetTitle("impact parameter b")
            h_DYMinBias_pad2.GetXaxis().SetTitleSize(0.05)
            h_DYMinBias_pad2.GetXaxis().SetLabelSize(0.05)
            h_DYMinBias_pad2.GetXaxis().SetTitleOffset(1.4)
            if binweight:
                h_DYMinBias_pad2.GetYaxis().SetTitle("Density #frac{1}{N} #frac{dN}{db} (normalised)")
            else:
                h_DYMinBias_pad2.GetYaxis().SetTitle("Number of Events (normalised)")
            h_DYMinBias_pad2.GetYaxis().SetTitleSize(0.05)
            h_DYMinBias_pad2.GetYaxis().SetLabelSize(0.05)
            h_DYMinBias_pad2.GetYaxis().SetTitleOffset(0.8)


            h_MCDYMinBias_pad2.SetStats(0)
            h_MCDYMinBias_pad2.SetLineColor(colour)
            h_MCDYMinBias_pad2.SetMarkerColor(colour)
            h_MCDYMinBias_pad2.SetLineWidth(2)
            h_MCDYMinBias_pad2.SetLineStyle(2)

            h_DYMinBias_pad2_2.SetStats(0)
            h_DYMinBias_pad2_2.SetLineColor(ROOT.kGreen + 3)
            h_DYMinBias_pad2_2.SetMarkerColor(ROOT.kGreen + 3)
            h_DYMinBias_pad2_2.SetLineWidth(1)

            h_MCDYMinBias_pad2_2.SetStats(0)
            h_MCDYMinBias_pad2_2.SetLineColor(ROOT.kGreen + 3)
            h_MCDYMinBias_pad2_2.SetMarkerColor(ROOT.kGreen + 3)
            h_MCDYMinBias_pad2_2.SetLineWidth(1)
            h_MCDYMinBias_pad2_2.SetLineStyle(2)

            h_DYMinBias_pad2.GetYaxis().SetRangeUser(0, max(h_DYMinBias_pad2.GetMaximum(), h_MCDYMinBias_pad2.GetMaximum(), h_DYMinBias_pad2_2.GetMaximum(), h_MCDYMinBias_pad2_2.GetMaximum()) * 1.1)
            

            if index == 0:
                h_DYMinBias_pad2.Draw("hist e")
            else:
                h_DYMinBias_pad2.Draw("hist e same")

            h_MCDYMinBias_pad2.Draw("hist e same")

            h_DYMinBias_pad2_2.Draw("hist e same")
            h_MCDYMinBias_pad2_2.Draw("hist e same")






            # ratio_SingleMuon.Scale(1 * (xsec_MINBIAS/xsec_DY) * (xsec_INEL/xsec_MINBIAS) * (Events_MINBIAS/Events_DY))
            # ratio_MCDYJets.Scale(1 * (xsec_MINBIAS/xsec_DY) * (xsec_INEL/xsec_MINBIAS) * (Events_MCMINBIAS/Events_MCDY))



   



            # # ---------------------- from Pythia --------------------
            # if pt_cut == 4:

            #     canvas.cd()
            #     pad1.cd()
                
            #     df_pythia = pd.read_hdf("simulated_enhf_vs_impactparam.hdf")

            #     values = df_pythia["values"]
            #     edges = df_pythia["edges"]

            #     index_pythia = 0

            
            #     if var == "PFCands_Ht":
            #         index_pythia = 2
            #     elif var == "PFCands_Pt2sum":
            #         index_pythia = 5
            #     elif var == "PFCands_InvariantMass":
            #         index_pythia = 3
            #     elif var == "nPFCands":
            #         index_pythia = 0
            #     elif var == "PFCands_Psum":
            #         index_pythia = 1
            #     else:
            #         print(f"Variable {var} not found in Pythia data; skipping Pythia overlay.")
            #         continue

            #     bins_new = array.array('d', np.asarray(df_pythia["edges"].iloc[index_pythia], dtype=np.float64))
            #     h_pythia = ROOT.TH1F("h_pythia", "Histogram of values", len(bins_new) - 1, bins_new)

            #     row_values = values.iloc[index_pythia]
            #     row_edges = edges.iloc[index_pythia]


            #     for j in range(len(row_values)):
            #         h_pythia.SetBinContent(j, row_values[j])
            #     # print(f"Set bin {j} content to {row_values[j]}")



            #     # NormaliseHist(h_pythia)

            #     h_pythia.SetLineColor(ROOT.kRed)
            #     h_pythia.SetLineWidth(2)
            #     # h_pythia.SetLineStyle(2)
            #     h_pythia.Draw("hist same")


            #     ratio_MC.SetMaximum(max(ratio_MCDYJets.GetMaximum(), ratio_MC.GetMaximum(), h_pythia.GetMaximum()) * 1.2)
    



            canvas.cd()
            pad1.cd()


        

            # if pt_cut == 4:
            #     legend_var.AddEntry(h_pythia, f"#color[{ROOT.kRed}]{{#bf{{Pythia}}}}", "l")

            # legend_var.AddEntry(dummy, label, "")

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

            for entry in list(legend_DataMC_pad2.GetListOfPrimitives()):
                if entry.GetLabel() == "MinBias":
                    legend_DataMC_pad2.GetListOfPrimitives().Remove(entry)
                if entry.GetLabel() == "#bf{Data}":
                    legend_DataMC_pad2.GetListOfPrimitives().Remove(entry)
                if entry.GetLabel() == "#bf{MC}":
                    legend_DataMC_pad2.GetListOfPrimitives().Remove(entry)


            legend_DataMC_pad2.AddEntry(dummyData, f"#bf{{Data}}", "l")
            legend_DataMC_pad2.AddEntry(dummyMC, f"#bf{{MC}}", "l")
            legend_DataMC_pad2.AddEntry(dummy, f"#color[{ROOT.kOrange + 5}]{{#bf{{b: bTb}}}}", "")
            legend_DataMC_pad2.AddEntry(dummy, f"#color[{ROOT.kGreen + 3}]{{#bf{{b: eTe}}}}", "")


            legend_DataMC_pad2.Draw()
            legend_var_pad2.Draw()



        output_dir = f"new_plots/quantile_binning/{bins}"
        os.makedirs(output_dir, exist_ok=True)

        if pt_cut is None or len(pt_cuts) == 0:
            output_name = f"{output_dir}/{var}_DYMinBias_NoZPtCut{out_suffix}.pdf"
        else:
            output_name = f"{output_dir}/{var}_DYMinbias_{pt_cut}GeVZPtCut{out_suffix}.pdf"

        canvas.SaveAs(output_name)

        canvas.Close()


def Quantile_DiMuonPtCut(df_SingleMuon_var, df_MinBias_var, df_MCDYJets_var, df_MCMinBias_var, variables, pt_cuts, out_suffix, bins):

    pt_cuts = parse_pt_cuts(pt_cuts)

    df_SingleMuon_var = df_SingleMuon_var.Filter("DiMuon_Mass > 86 && DiMuon_Mass < 96")
    df_MCDYJets_var = df_MCDYJets_var.Filter("DiMuon_Mass > 86 && DiMuon_Mass < 96")


    def colors_func(n):
        base = [
            ROOT.kBlue + 1,
            ROOT.kRed + 1,
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
        ]
        return [base[i % len(base)] for i in range(n)]
    
    colours = colors_func(len(pt_cuts))


    for var in variables:
        if var in ["PFCands_pt", "PFCands_eta", "PFCands_phi", "PFCands_pvAssocQuality"]:
            continue

        label = VARIABLES[var]
        binning = BINNING[var]
        y_title = "Cumulative Distribution Function (CDF)"


        h_tmp_ptr = MakeHist(df_MinBias_var, var, label, y_title, binning, f"h_MinBias_{var}_quantile_ptscan_tmp")
        h_tmp = h_tmp_ptr.GetValue()
        total = h_tmp.Integral()
        if total <= 0:
            print(f"Warning: MinBias histogram for '{var}' has zero integral; skipping quantile pT-scan plot")
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
            namespace {var}InvQMapPtScan {{
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
            namespace {var}InvQMapPtScanMC {{
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

        def inverse_cdf(target, edges, cdf):
            return np.interp(target, cdf, edges)


        for i in range(len(bins)-1):

            q_low = bins[i]
            q_high = bins[i+1]

            # convert inverse quantile -> CDF
            cdf_low = 1 - q_high
            cdf_high = 1 - q_low

            ht_low = inverse_cdf(cdf_low, bin_edges, cdf_values)
            ht_high = inverse_cdf(cdf_high, bin_edges, cdf_values)

            print(
                f"Quantile bin {q_low:.3f}-{q_high:.3f}: "
                f"Ht = {ht_low:.2f} - {ht_high:.2f}"
            )

        df_MinBias_q = df_MinBias_var.Define(f"{var}_invQ", f"1.0 - {var}InvQMapPtScan::eval(PFSelection_{var})")
        df_SingleMuon_q = df_SingleMuon_var.Define(f"{var}_invQ", f"1.0 - {var}InvQMapPtScan::eval(PFSelection_{var})")
        df_MCDYJets_q = df_MCDYJets_var.Define(f"{var}_invQ", f"1.0 - {var}InvQMapPtScanMC::eval(PFSelection_{var})")
        df_MCMinBias_q = df_MCMinBias_var.Define(f"{var}_invQ", f"1.0 - {var}InvQMapPtScanMC::eval(PFSelection_{var})")



        plot_column = f"{var}_invQ"
        plot_xlabel = f"impact parameter b"
        # plot_xlabel = f"Quantiles of {label}"

        quantile_edges = array.array("d", bins)


        h_MinBias_ptr = df_MinBias_q.Histo1D(
            (f"h_MinBias_{var}_quantile_ptscan", f"; {plot_xlabel}; DY/ZeroBias", len(quantile_edges) - 1, quantile_edges),
            plot_column,
        )
        h_MCMinBias_ptr = df_MCMinBias_q.Histo1D(
            (f"h_MCMinBias_{var}_quantile_ptscan", f"; {plot_xlabel}; DY/ZeroBias", len(quantile_edges) - 1, quantile_edges),
            plot_column,
        )

        h_MinBias = h_MinBias_ptr.GetValue()
        h_MCMinBias = h_MCMinBias_ptr.GetValue()

        MinBias_hists = []

        for h in [h_MinBias, h_MCMinBias]:

            nbins = h.GetNbinsX()

            edges = []
            for i in range(1, nbins+2):
                q = h.GetBinLowEdge(i)
                edges.append(math.sqrt(q/(2*math.pi)))

            h_new = ROOT.TH1D(
                h.GetName()+"_b",
                h.GetTitle(),
                nbins,
                array.array("d", edges)
            )

            for i in range(1, nbins+1):
                h_new.SetBinContent(i, h.GetBinContent(i))
                h_new.SetBinError(i, h.GetBinError(i))

            MinBias_hists.append(h_new)

        h_MinBias, h_MCMinBias = MinBias_hists

    
        NormaliseHist(h_MinBias, True)
        NormaliseHist(h_MCMinBias, True)




        canvas = ROOT.TCanvas(f"c_quantile_ptscan_{var}", "", 1500, 1400)
        canvas.cd()
        canvas.SetBottomMargin(0.13)
        canvas.SetRightMargin(0.25)
        canvas.SetLogy()

        pad1 = ROOT.TPad(f"pad1_{var}GeV", "pad1", 0, 0.1, 1, 1)
        # pad1.SetBottomMargin(0)
        pad1.SetRightMargin(0.25)
        pad1.SetLogy()
        pad1.Draw()

        canvas.cd()


        # pad2 = ROOT.TPad(f"pad2_{var}GeV", "pad2", 0, 0, 1, 0.5)
        # pad2.SetTopMargin(0.05)
        # pad2.SetBottomMargin(0.35)
        # pad2.SetRightMargin(0.25)
        # pad2.SetGridy()
        # pad2.Draw()
        # pad2.cd()

        # canvas.cd()

        
        inset = ROOT.TPad(f"inset_{var}", f"inset_{var}", 0.75, 0, 0.99, 1)
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


        legend_var = ROOT.TLegend(0.12, 0.8, 0.34, 0.91)
        legend_var.SetBorderSize(0)
        legend_var.SetFillStyle(0)
        legend_var.SetTextSize(0.03)
        legend_var.SetMargin(0.2)
        legend_var.AddEntry(dummy, label, "")

        legend_col0 = ROOT.TLegend(0.3, 0.75, 0.52, 0.9)
        legend_col0.SetBorderSize(0)
        legend_col0.SetFillStyle(0)
        legend_col0.SetTextSize(0.03)
        legend_col0.SetMargin(0.2)
        

        legend_ptcuts = ROOT.TLegend(0.13, 0.22, 0.61, 0.4)
        legend_ptcuts.SetBorderSize(0)
        legend_ptcuts.SetFillStyle(0)
        legend_ptcuts.SetTextSize(0.03)
        legend_ptcuts.SetMargin(0)

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

        


        histos = []
        inset_histos = []
        plot_max = 0


        for index, pt_cut in enumerate(pt_cuts):
            if index == len(pt_cuts) - 1:
                break

            if pt_cut is None:
                pt_cuts[index] = 0

            canvas.cd()
            
            
            print(f"\n\nProcessing DiMuon pT cut: {pt_cut} GeV...\n")
            
            # if pt_cut is None or len(pt_cuts) == 0:

            #     print(f"\n\nNo DiMuon pT cut specified.\n")
            #     df_SingleMuon_cut = df_SingleMuon_q
            #     df_MCDYJets_cut = df_MCDYJets_q

            # else:
            #     print(f"Applying DiMuon pT cut: {pt_cut} GeV...")

            #     # df_SingleMuon_cut = DiMuonPtCut(df_SingleMuon_q, pt_cut)
            #     # df_MCDYJets_cut = DiMuonPtCut(df_MCDYJets_q, pt_cut)

            df_SingleMuon_cut = df_SingleMuon_q.Filter(f"DiMuon_Pt >= {pt_cuts[index]} && DiMuon_Pt < {pt_cuts[index + 1]}")
            df_MCDYJets_cut = df_MCDYJets_q.Filter(f"DiMuon_Pt >= {pt_cuts[index]} && DiMuon_Pt < {pt_cuts[index + 1]}")
                
            colour = colours[index]

            h_SingleMuon_ptr = df_SingleMuon_cut.Histo1D(
                (f"h_SingleMuon_{var}_quantile_{pt_cut}GeV", f"; {plot_xlabel}; DY/ZeroBias", len(quantile_edges) - 1, quantile_edges),
                plot_column,
            )
            h_MCDYJets_ptr = df_MCDYJets_cut.Histo1D(
                (f"h_MCDYJets_{var}_quantile_{pt_cut}GeV", f"; {plot_xlabel}; DY/ZeroBias", len(quantile_edges) - 1, quantile_edges),
                plot_column,
            )

            h_SingleMuon = h_SingleMuon_ptr.GetValue()
            h_MCDYJets = h_MCDYJets_ptr.GetValue()




            DY_hists = []

            for h in [h_SingleMuon, h_MCDYJets]:

                nbins = h.GetNbinsX()

                edges = []
                for i in range(1, nbins+2):
                    q = h.GetBinLowEdge(i)
                    edges.append(math.sqrt(q/(2*math.pi)))

                h_new = ROOT.TH1D(
                    h.GetName()+"_b",
                    h.GetTitle(),
                    nbins,
                    array.array("d", edges)
                )

                for i in range(1, nbins+1):
                    h_new.SetBinContent(i, h.GetBinContent(i))
                    h_new.SetBinError(i, h.GetBinError(i))

                DY_hists.append(h_new)

            h_SingleMuon, h_MCDYJets = DY_hists


            NormaliseHist(h_SingleMuon, True)
            NormaliseHist(h_MCDYJets, True)
            

            # NormaliseHist(h_SingleMuon)
            # NormaliseHist(h_MCDYJets)
            # NormaliseHist(h_MinBias)
            # NormaliseHist(h_MCMinBias)
            
          


            # ratio_SingleMuon = h_SingleMuon.Clone(f"ratio_quantile_SingleMuon_{var}_{pt_cut}GeV")
            # ratio_SingleMuon.Divide(h_MinBias)

            # h_SingleMuon.SetStats(0)
            # h_SingleMuon.SetLineColor(colour)
            # h_SingleMuon.SetMarkerColor(colour)
            # h_SingleMuon.SetLineWidth(2)
            # h_SingleMuon.GetXaxis().SetTitle(plot_xlabel)
            # h_SingleMuon.GetYaxis().SetTitle("Number of Events (normalised)")
            # h_SingleMuon.GetXaxis().SetTitleSize(0.04)
            # # h_SingleMuon.GetXaxis().SetTitleOffset(0.5)
            # h_SingleMuon.GetXaxis().SetLabelSize(0.03)
            # h_SingleMuon.GetXaxis().SetTickLength(0.027)
            # h_SingleMuon.GetYaxis().SetTitleSize(0.035)
            # h_SingleMuon.GetYaxis().SetLabelSize(0.04)
            # h_SingleMuon.GetYaxis().SetTitleOffset(1.2)

            # h_MinBias.SetStats(0)
            # h_MinBias.SetLineColor(ROOT.kOrange + 5)
            # h_MinBias.SetMarkerColor(ROOT.kOrange + 5)
            # h_MinBias.SetLineWidth(2)
            # h_MinBias.GetXaxis().SetTitle(plot_xlabel)
            # h_MinBias.GetYaxis().SetTitle("Number of Events (normalised)")
            # h_MinBias.GetXaxis().SetTitleSize(0.045)
            # h_MinBias.GetXaxis().SetTitleOffset(0.5)
            # h_MinBias.GetXaxis().SetLabelSize(0.05)
            # h_MinBias.GetXaxis().SetTickLength(0.027)
            # h_MinBias.GetYaxis().SetTitleSize(0.045)
            # h_MinBias.GetYaxis().SetLabelSize(0.05)

            # # ratio_MCDYJets = h_MCDYJets.Clone(f"ratio_quantile_MCDYJets_{var}_{pt_cut}GeV")
            # # ratio_MCDYJets.Divide(h_MCMinBias)
            # h_MCDYJets.SetStats(0)
            # h_MCDYJets.SetLineColor(colour)
            # h_MCDYJets.SetMarkerColor(colour)
            # h_MCDYJets.SetLineWidth(2)
            # h_MCDYJets.SetLineStyle(2)
            # h_MCDYJets.GetXaxis().SetTitleSize(0.045)
            # h_MCDYJets.GetXaxis().SetTitleOffset(1.5)
            # h_MCDYJets.GetXaxis().SetLabelSize(0.05)
            # h_MCDYJets.GetXaxis().SetTickLength(0.027)
            # h_MCDYJets.GetYaxis().SetTitleSize(0.045)
            # h_MCDYJets.GetYaxis().SetLabelSize(0.05)

            # h_MCMinBias.SetStats(0)
            # h_MCMinBias.SetLineColor(ROOT.kOrange + 5)
            # h_MCMinBias.SetMarkerColor(ROOT.kOrange + 5)
            # h_MCMinBias.SetLineWidth(2)
            # h_MCMinBias.SetLineStyle(2)
            # h_MCMinBias.GetXaxis().SetTitleSize(0.045)
            # h_MCMinBias.GetXaxis().SetTitleOffset(1.5)
            # h_MCMinBias.GetXaxis().SetLabelSize(0.05)
            # h_MCMinBias.GetXaxis().SetTickLength(0.027)
            # h_MCMinBias.GetYaxis().SetTitleSize(0.045)
            # h_MCMinBias.GetYaxis().SetLabelSize(0.05)

            # canvas.cd()

            # if index == 0:
                # ratio_SingleMuon.Draw("hist e")
                # ratio_MCDYJets.Draw("hist e same")
            #     h_SingleMuon.Draw("hist e")
            # else:
            #     h_SingleMuon.Draw("hist e same")

            # h_MCDYJets.Draw("hist e same")
            # h_MinBias.Draw("hist e same")
            # h_MCMinBias.Draw("hist e same")


            # max_val = h_SingleMuon.GetBinContent(h_SingleMuon.GetMaximumBin())
            # if plot_max < max_val:
            #     plot_max = max_val

            # histos.append(ratio_SingleMuon)
            # histos.append(ratio_MCDYJets)
            # histos.append(h_SingleMuon)
            # histos.append(h_MCDYJets)
            
            pad1.cd()

            # print(h_SingleMuon.GetNbinsX(), h_MinBias.GetNbinsX())

            # for i in range(1, h_SingleMuon.GetNbinsX()+2):
            #     print(i, h_SingleMuon.GetXaxis().GetBinLowEdge(i), h_MinBias.GetXaxis().GetBinLowEdge(i))


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
            ratio_Data.GetYaxis().SetTitle("Density #frac{1}{N} #frac{dN}{db} (normalised)")
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
            # ratio_MC.SetMinimum(0)
            # ratio_MC.SetMaximum(2)
            histos.append(ratio_MC)

            max_bin = h_MCDYJets.GetMaximumBin()
            q_peak = h_MCDYJets.GetBinCenter(max_bin)

            cdf_peak = 1 - q_peak

            # Convert CDF -> Ht
            Ht_peak = np.interp(
                cdf_peak,
                cdf_values_MC,
                bin_edges_MC
            )

            print(
                f"MC maximum at quantile {q_peak:.3f} "
                f"corresponds to Ht = {Ht_peak:.3f}"
            )



        

            ymax = max(ratio_Data.GetMaximum(), ratio_MC.GetMaximum()) * 1.3
            ymin = min(ratio_Data.GetMinimum(), ratio_MC.GetMinimum()) * 0.8
            ratio_Data.SetMinimum(ymin * 0.8)
            ratio_Data.SetMaximum(ymax * 8)



            if index == 0:
                ratio_Data.Draw("hist e")
                
            else:
                ratio_Data.Draw("hist e same")
            ratio_MC.Draw("hist e same")


            # canvas.cd()
            # pad2.cd()

            # ratio = ratio_Data.Clone(f"ratio_final_{var}_{pt_cut}GeV")
            # ratio.Divide(ratio_MC)
            # ratio.SetLineColor(colour)
            # ratio.SetMarkerColor(colour)
            # ratio.SetLineWidth(2)
            # ratio.SetDirectory(0)
            # ratio.GetXaxis().SetTitle(plot_xlabel)
            # ratio.GetXaxis().SetTitleSize(0.11)
            # ratio.GetXaxis().SetTitleOffset(1.3)
            # ratio.GetXaxis().SetLabelSize(0.11)
            # ratio.GetXaxis().SetTickLength(0.07)
            # ratio.GetYaxis().SetTitle("Data/MC")
            # ratio.GetYaxis().SetTitleSize(0.11)
            # ratio.GetYaxis().SetLabelSize(0.11)
            # ratio.GetYaxis().SetTitleOffset(0.5)
            # ratio.GetYaxis().SetNdivisions(10, False)
            # if index == 0:
            #     ratio.Draw("hist e")
            # else:
            #     ratio.Draw("hist e same")

            

            


            # ---------------------- from Pythia --------------------
            if pt_cut == 4:

                canvas.cd()
                pad1.cd()
                
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
                    continue

                bins_new = array.array('d', np.asarray(df_pythia["edges"].iloc[index_pythia], dtype=np.float64))
                h_pythia = ROOT.TH1F("h_pythia", "Histogram of values", len(bins_new) - 1, bins_new)

                row_values = values.iloc[index_pythia]
                row_edges = edges.iloc[index_pythia]


                for j in range(len(row_values)):
                    h_pythia.SetBinContent(j, row_values[j])
                # print(f"Set bin {j} content to {row_values[j]}")



                # NormaliseHist(h_pythia)

                h_pythia.SetLineColor(colour)
                h_pythia.SetLineWidth(4)
                h_pythia.SetLineStyle(6)
                h_pythia.Draw("hist same")


                ratio_Data.SetMaximum(max(ratio_Data.GetMaximum(), ratio_MC.GetMaximum(), h_pythia.GetMaximum()) * 5)

                legend_var.AddEntry(h_pythia, "Pythia", "l")


            canvas.cd()
            # pad1.cd()
            # if pt_cut is None:
            #     legend_ptcuts.AddEntry(dummy, f"#color[{colour}]{{#bf{{No p^{{#mu#mu}}_{{T}} cut}}}}", "")
            # else:
            legend_ptcuts.AddEntry(dummy, f"#color[{colour}]{{#bf{{{int(pt_cuts[index])} GeV #leq p^{{#mu#mu}}_{{T}} < {int(pt_cuts[index + 1])} GeV}}}}", "")



            print(f"Finished processing diMuon pT cut: {pt_cut} GeV!\n")

            if histos and plot_max > 0:
                histos[0].SetMaximum(plot_max * 5)

            canvas.cd()
            inset.cd()

            
            # clone histograms so axis/range changes don't affect main pads
            h1 = ratio_Data.Clone(ratio_Data.GetName() + "_inset")
            h1MC = ratio_MC.Clone(ratio_MC.GetName() + "_inset")

            
            xmin = 0
            xmax = 0.15

            histYmin = min(h1MC.GetBinContent(1), h1MC.GetBinContent(2), h1MC.GetBinContent(3), h1MC.GetBinContent(4))
            histYmax = max(h1MC.GetBinContent(1), h1MC.GetBinContent(2), h1MC.GetBinContent(3), h1MC.GetBinContent(4))
            
    
            if index == 0:
                ymin = histYmin * 0.9
                ymax = histYmax * 1.05
            else:
                ymin = min(ymin, histYmin) * 0.9
                ymax = max(ymax, histYmax) * 1.05
            
            frame = inset.DrawFrame(xmin, ymin, xmax, ymax)
            frame.GetXaxis().SetLabelSize(0.05)
            frame.GetYaxis().SetLabelSize(0.08)
            frame.GetXaxis().SetTitleSize(0.05)
            frame.GetYaxis().SetTitleSize(0.01)
            frame.GetXaxis().SetLabelOffset(0.00005)
            frame.GetYaxis().SetMoreLogLabels(True)
            frame.GetYaxis().SetNdivisions(303, False)
            frame.GetYaxis().SetRangeUser(ymin, ymax)




            h1.GetXaxis().SetRangeUser(xmin, xmax)
            h1.GetXaxis().SetTitle(plot_xlabel)
            h1.GetXaxis().SetLabelSize(0.03)
            h1.GetYaxis().SetLabelSize(0.06)
            h1.GetYaxis().SetRangeUser(ymin, ymax)
            h1.GetYaxis().SetTitle("DY/MinBias")
            
            h1MC.GetXaxis().SetRangeUser(xmin, xmax)
            h1MC.GetXaxis().SetTitle(plot_xlabel)
            h1MC.GetXaxis().SetLabelSize(0.03)
            h1MC.GetYaxis().SetLabelSize(0.06)
            h1MC.GetYaxis().SetRangeUser(ymin, ymax)
            h1MC.GetYaxis().SetTitle("DY/MinBias")

            inset_histos.append((h1, h1MC))

            if index == 0:
                # h1.Draw("hist e")
                h1MC.Draw("hist e")

            else:
                # h1.Draw("hist e same")
                h1MC.Draw("hist e same")

        inset.cd()
        ymin = []
        ymax = []

        for h in inset_histos:
            ymin.append(min(h[1].GetBinContent(1), h[1].GetBinContent(2), h[1].GetBinContent(3), h[1].GetBinContent(4)))
            ymax.append(max(h[1].GetBinContent(1), h[1].GetBinContent(2), h[1].GetBinContent(3), h[1].GetBinContent(4)))

        frame.GetYaxis().SetRangeUser(min(ymin) * 0.9, max(ymax) * 1.05)

        for h in inset_histos:
            h[1].Draw("hist e same")

        canvas.cd()
        # pad1.cd()

        legend_ptcuts.Draw()
        legend_col0.Draw()
        legend_var.Draw()


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

        df_SingleMuon_var = df_SingleMuon_var.Filter("DiMuon_Mass > 86 && DiMuon_Mass < 96")
        df_MCDYJets_var = df_MCDYJets_var.Filter("DiMuon_Mass > 86 && DiMuon_Mass < 96")

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

def parse_args():
    parser = argparse.ArgumentParser(
        description="Combined plotting driver for NanoAOD PF-candidate studies"
    )
    parser.add_argument(
        "--mode",
        choices=["compare", "compare-quantilebinning", "ptscan", "ptscan-quantilebinning", "quantile", "quantile-ptscan", "quantile-all", "DYMinBias", "quantile-all-ptscan", "quantiles", "momentumfractions", "mllyll", "all"],
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

    # if args.slurm == True:
    #     totalEvents = TotalEvents()
    #     selectedEvents = SelectedEvents(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias)
    # else:
    #     totalEvents = TotalEvents_local()
    #     selectedEvents = SelectedEvents_local(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias)

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
        QuantilePerObservable(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias, args.vars, args.output_suffix, args.quantile_bins, args.pt_cuts, args.binweight)

    if args.mode in ["DYMinBias", "quantiles", "all"]:    
        DYMinBiasPerObservableRatio(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias, args.vars, args.output_suffix, args.quantile_bins, args.pt_cuts, args.binweight)

    if args.mode in ["quantile-ptscan", "quantiles", "all"]:
        Quantile_DiMuonPtCut(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias, args.vars, args.pt_cuts, args.output_suffix, args.quantile_bins)

    if args.mode in ["quantile-all", "quantiles", "all"]:
        Quantile_AllTogether(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias, args.vars, args.output_suffix, args.quantile_bins)

    if args.mode in ["quantile-all-ptscan", "quantiles", "all"]:
        Quantile_AllTogether_DiMuonPtCut(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias, args.vars, args.pt_cuts, args.output_suffix, args.quantile_bins)

    if args.mode in ["momentumfractions", "all"]:
        MomentumFractions(df_SingleMuon, df_MCDYJets, args.pt_cuts, args.output_suffix)

    if args.mode in ["mllyll", "all"]:
        MassRapidity(df_SingleMuon, df_MCDYJets, args.pt_cuts, args.output_suffix)

    end = time.time()
    elapsed_time = end - start
    print(f"\nTotal execution time: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main()
