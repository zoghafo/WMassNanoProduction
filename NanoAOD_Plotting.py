import argparse
import array
import ROOT
import glob
import pandas as pd
import os
import pprint
import time



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
    df = df.Filter(f"diMuon_pT < {pt_cut}")
    return df

def MakeHist(df, var, label, y_title, bins, hist_name):
    title = f"; {label}; {y_title}"
    if len(bins) == 3:
        return df.Histo1D((hist_name, title, bins[0], bins[1], bins[2]), f"PFSelection_{var}")

    edges = array.array("d", bins)
    return df.Histo1D((hist_name, title, len(edges) - 1, edges), f"PFSelection_{var}")


def NormaliseHist(hist, width=False):
    integral = hist.Integral()
    if integral > 0:
        if width:
            hist.Scale(1.0 / integral, "width")
        else:
            hist.Scale(1.0 / integral)
    else:
        print(f"Warning: histogram '{hist.GetName()}' has zero integral; skipping normalization")
    hist.SetStats(0)


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

# ---------------------- PLOTS ----------------------

def Plot_CompareTriggers(df_SingleMuon_var, df_MinBias_var, df_MCDYJets_var, df_MCMinBias_var, variables, out_suffix, totalEvents, selectedEvents):

    for var in variables:

        label = VARIABLES[var]
        bins = BINNING[var]
        y_title = "Number of Events (normalised)"

        h_SingleMuon_ptr = MakeHist(df_SingleMuon_var, var, label, y_title, bins, f"h_SingleMuon_{var}")
        h_MinBias_ptr = MakeHist(df_MinBias_var, var, label, y_title, bins, f"h_MinBias_{var}")
        h_MCDYJets_ptr = MakeHist(df_MCDYJets_var, var, label, y_title, bins, f"h_MCDYJets_{var}")
        h_MCMinBias_ptr = MakeHist(df_MCMinBias_var, var, label, y_title, bins, f"h_MCMinBias_{var}")

        h_SingleMuon= h_SingleMuon_ptr.GetValue()
        h_MinBias = h_MinBias_ptr.GetValue()
        h_MCDYJets = h_MCDYJets_ptr.GetValue()
        h_MCMinBias = h_MCMinBias_ptr.GetValue()
        NormaliseHist(h_SingleMuon)
        NormaliseHist(h_MinBias)
        NormaliseHist(h_MCDYJets)
        NormaliseHist(h_MCMinBias)

        canvas = ROOT.TCanvas(f"c_{var}")

        pad1 = ROOT.TPad("pad1", "pad1", 0, 0.32, 1, 1)
        pad1.Draw()
        pad1.cd()
        pad1.SetBottomMargin(0.05)
        pad1.SetRightMargin(0.26)
        pad1.SetLogy()
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

        h_MCDYJets.SetLineColor(ROOT.kViolet - 6)
        h_MCDYJets.SetLineWidth(2)
        h_MCDYJets.SetLineStyle(2)
        h_MCDYJets.Draw("hist e same")

        h_MCMinBias.SetLineColor(ROOT.kOrange + 5)
        h_MCMinBias.SetLineWidth(2)
        h_MCMinBias.SetLineStyle(2)
        h_MCMinBias.Draw("hist e same")

        h_SingleMuon.SetMaximum(max(h_SingleMuon.GetMaximum(), h_MinBias.GetMaximum(), h_MCDYJets.GetMaximum(), h_MCMinBias.GetMaximum()) * 1.3)

        legend = ROOT.TLegend(0.75, 0.3, 0.96, 0.87)
        dummy = ROOT.TObject()
        legend.SetBorderSize(0)
        legend.SetFillStyle(0)
        legend.SetTextSize(0.04)
        legend.SetMargin(0.2)
        legend.AddEntry(dummy, "#bf{Data}", "")

        legend.AddEntry(h_SingleMuon, "DY", "l")
        legend.AddEntry(dummy, f"{(selectedEvents['SingleMuon'][0]/totalEvents['SingleMuon'][0])*100:.2f}% selected Events", "")
        legend.AddEntry(dummy, f"{(selectedEvents['SingleMuon'][1]/totalEvents['SingleMuon'][1])*100:.2f}% selected PFCands", "")

        legend.AddEntry(h_MinBias, "ZeroBias", "l")
        legend.AddEntry(dummy, f"{(selectedEvents['MinBias'][0]/totalEvents['MinBias'][0])*100:.2f}% selected Events", "")
        legend.AddEntry(dummy, f"{(selectedEvents['MinBias'][1]/totalEvents['MinBias'][1])*100:.2f}% selected PFCands", "")

        legend.AddEntry(dummy, "#bf{MC}", "")

        legend.AddEntry(h_MCDYJets, "DY", "l")
        legend.AddEntry(dummy, f"{(selectedEvents['MCDY'][0]/totalEvents['MCDY'][0])*100:.2f}% selected Events", "")
        legend.AddEntry(dummy, f"{(selectedEvents['MCDY'][1]/totalEvents['MCDY'][1])*100:.2f}% selected PFCands", "")

        legend.AddEntry(h_MCMinBias, "ZeroBias", "l")
        legend.AddEntry(dummy, f"{(selectedEvents['MCMinBias'][0]/totalEvents['MCMinBias'][0])*100:.2f}% selected Events", "")
        legend.AddEntry(dummy, f"{(selectedEvents['MCMinBias'][1]/totalEvents['MCMinBias'][1])*100:.2f}% selected PFCands", "")
        legend.Draw()

        canvas.cd()
        pad2 = ROOT.TPad("pad2", "pad2", 0, 0, 1, 0.35)
        pad2.Draw()
        pad2.cd()
        pad2.SetTopMargin(0.05)
        pad2.SetBottomMargin(0.35)
        pad2.SetRightMargin(0.26)
        if var not in ["PFCands_eta", "PFCands_phi", "PFCands_pvAssocQuality"]:
            pad2.SetLogy()

        ratio_SingleMuon = h_SingleMuon.Clone(f"ratio_{var}")
        ratio_SingleMuon.Divide(h_MinBias)
        ratio_SingleMuon.SetLineColor(ROOT.kBlack)
        ratio_SingleMuon.SetMarkerStyle(20)
        ratio_SingleMuon.SetMarkerSize(0.8)
        ratio_SingleMuon.GetYaxis().SetTitle("Ratio")
        ratio_SingleMuon.GetXaxis().SetTitle(label)
        ratio_SingleMuon.GetXaxis().SetTitleSize(0.1)
        ratio_SingleMuon.GetXaxis().SetTitleOffset(1.3)
        ratio_SingleMuon.GetXaxis().SetLabelSize(0.09)
        ratio_SingleMuon.GetXaxis().SetTickLength(0.07)
        ratio_SingleMuon.GetYaxis().SetTitleSize(0.09)
        ratio_SingleMuon.GetYaxis().SetLabelSize(0.08)
        ratio_SingleMuon.GetYaxis().SetTitleOffset(0.5)

        ratio_MCDYJets = h_MCDYJets.Clone(f"ratio_{var}")
        ratio_MCDYJets.Divide(h_MCMinBias)
        ratio_MCDYJets.SetLineColor(ROOT.kGray + 2)
        ratio_MCDYJets.SetMarkerColor(ROOT.kGray + 2)
        ratio_MCDYJets.SetMarkerStyle(20)
        ratio_MCDYJets.SetMarkerSize(0.8)
        pad2.SetGridy()

        if var not in ["PFCands_eta", "PFCands_phi", "PFCands_pvAssocQuality"]:

            min_val = ratio_SingleMuon.GetBinContent(ratio_SingleMuon.GetMinimumBin())
            if min_val <= 0:
                min_val = 1e-3
            max_val = ratio_SingleMuon.GetBinContent(ratio_SingleMuon.GetMaximumBin())
            if max_val <= 0:
                max_val = 10

            min_val = min_val * 0.2
            max_val = max_val * 10

        else:
            min_val = 0.5
            max_val = 1.5

        ratio_SingleMuon.SetMinimum(min_val)
        ratio_SingleMuon.SetMaximum(max_val)
        ratio_SingleMuon.Draw("pe")
        ratio_MCDYJets.Draw("pe same")

        ratio_DY = h_SingleMuon.Clone(f"ratio_{var}")
        ratio_DY.Divide(h_MCDYJets)
        ratio_DY.SetLineColor(ROOT.kViolet - 6)
        ratio_DY.SetMarkerColor(ROOT.kViolet - 6)
        ratio_DY.SetMarkerStyle(20)
        ratio_DY.SetMarkerSize(0.8)
        ratio_DY.GetYaxis().SetTitle("Ratio")
        ratio_DY.GetXaxis().SetTitle(label)
        ratio_DY.GetXaxis().SetTitleSize(0.1)
        ratio_DY.GetXaxis().SetTitleOffset(1.3)
        ratio_DY.GetXaxis().SetLabelSize(0.09)
        ratio_DY.GetXaxis().SetTickLength(0.07)
        ratio_DY.GetYaxis().SetTitleSize(0.09)
        ratio_DY.GetYaxis().SetLabelSize(0.08)
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

        legend_ratio = ROOT.TLegend(0.75, 0.4, 0.99, 0.68)
        legend_ratio.SetBorderSize(0)
        legend_ratio.SetMargin(0.08)
        # legend_ratio.SetFillStyle(0)
        legend_ratio.SetTextSize(0.08)
        legend_ratio.AddEntry(ratio_SingleMuon, "Data DY / Data ZeroBias", "pe")
        legend_ratio.AddEntry(ratio_MCDYJets, "MC DY / MC ZeroBias", "pe")
        legend_ratio.AddEntry(ratio_DY, "Data DY / MC DY", "pe")
        legend_ratio.AddEntry(ratio_MinBias, "Data ZeroBias / MC ZeroBias", "pe")
        legend_ratio.Draw()

        output_name = f"new_plots/{var}{out_suffix}.pdf"
        canvas.SaveAs(output_name)
        canvas.Close()

def Plot_CompareTriggers_QuantileBinning(df_SingleMuon_var, df_MinBias_var, df_MCDYJets_var, df_MCMinBias_var, variables, out_suffix, totalEvents, selectedEvents, quantile_bins=None, quantile_reference="both", zoom_xmax=140):

    for var in variables:
        if var in ["PFCands_pt", "PFCands_eta", "PFCands_phi", "PFCands_pvAssocQuality"]:
            continue

        label = VARIABLES[var]
        bins = BINNING[var]
        y_title = "Event Count Density (normalised)"

        plot_bins = bins

        if quantile_reference == "Data":
            h_reference_ptr = MakeHist(
                df_MinBias_var, var, label, y_title, bins,
                f"h_SingleMuon_{var}_quantile_ref"
            )

        elif quantile_reference == "MC":
            h_reference_ptr = MakeHist(
                df_MCMinBias_var, var, label, y_title, bins,
                f"h_MCDYJets_{var}_quantile_ref"
            )

        elif quantile_reference == "both":
            # For "both", derive quantile bin edges from Data.
            h_reference_ptr = MakeHist(
                df_MinBias_var, var, label, y_title, bins,
                f"h_SingleMuon_{var}_quantile_ref"
            )

        else:
            raise ValueError(
                "quantile_reference must be 'Data', 'MC', or 'both'"
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

        if quantile_reference == "Data" or quantile_reference == "both":
            h_SingleMuon_ptr = MakeHist(df_SingleMuon_var, var, label, y_title, plot_bins, f"h_SingleMuon_{var}")
            h_MinBias_ptr = MakeHist(df_MinBias_var, var, label, y_title, plot_bins, f"h_MinBias_{var}")
        if quantile_reference == "MC" or quantile_reference == "both":
            h_MCDY_ptr = MakeHist(df_MCDYJets_var, var, label, y_title, plot_bins, f"h_MCDY_{var}")
            h_MCMinBias_ptr = MakeHist(df_MCMinBias_var, var, label, y_title, plot_bins, f"h_MCMinBias_{var}")

        if quantile_reference == "Data" or quantile_reference == "both":
            h_SingleMuon = h_SingleMuon_ptr.GetValue()
            h_MinBias = h_MinBias_ptr.GetValue()
            NormaliseHist(h_SingleMuon, True)
            NormaliseHist(h_MinBias, True)
        if quantile_reference == "MC" or quantile_reference == "both":
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

                if quantile_reference == "Data" or quantile_reference == "both":
                    SingleMuon_low = inverse_cdf_from_hist(h_SingleMuon, 1.0 - q_high)
                    SingleMuon_high = inverse_cdf_from_hist(h_SingleMuon, 1.0 - q_low)
                    MinBias_low = inverse_cdf_from_hist(h_MinBias, 1.0 - q_high)
                    MinBias_high = inverse_cdf_from_hist(h_MinBias, 1.0 - q_low)

                if quantile_reference == "MC" or quantile_reference == "both":
                    MCDY_low = inverse_cdf_from_hist(h_MCDY, 1.0 - q_high)
                    MCDY_high = inverse_cdf_from_hist(h_MCDY, 1.0 - q_low)
                    MCMinBias_low = inverse_cdf_from_hist(h_MCMinBias, 1.0 - q_high)
                    MCMinBias_high = inverse_cdf_from_hist(h_MCMinBias, 1.0 - q_low)

                if quantile_reference == "Data":
                    if SingleMuon_low is None or SingleMuon_high is None or MinBias_low is None or MinBias_high is None:
                        print(f"  [{q_low:.3f}, {q_high:.3f}] -> undefined")
                    else:
                        print(
                            f"  [{q_low:.3f}, {q_high:.3f}] -> "
                            f"Data SingleMuon {SingleMuon_low:.6g} - {SingleMuon_high:.6g}, "
                            f"Data MinBias {MinBias_low:.6g} - {MinBias_high:.6g}"
                        )
                elif quantile_reference == "MC":
                    if MCDY_low is None or MCDY_high is None or MCMinBias_low is None or MCMinBias_high is None:
                        print(f"  [{q_low:.3f}, {q_high:.3f}] -> undefined")
                    else:
                        print(
                            f"  [{q_low:.3f}, {q_high:.3f}] -> "
                            f"MCDY {MCDY_low:.6g} - {MCDY_high:.6g}, "
                            f"MCMinBias {MCMinBias_low:.6g} - {MCMinBias_high:.6g}"
                        )
                elif quantile_reference == "both":
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
        pad1.SetBottomMargin(0.05)
        pad1.SetRightMargin(0.26)
        pad1.SetLogy()
        pad1.SetGridy(1)
        pad1.SetTicky(0)

        if quantile_reference == "Data" or quantile_reference == "both":
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

        if quantile_reference == "MC" or quantile_reference == "both":
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
        

        legend = ROOT.TLegend(0.75, 0.28, 0.96, 0.87)
        dummy = ROOT.TObject()
        legend.SetBorderSize(0)
        legend.SetFillStyle(0)
        legend.SetTextSize(0.04)
        legend.SetMargin(0.2)

        if quantile_reference == "Data" or quantile_reference == "both":
            legend.AddEntry(dummy, "#bf{Data}", "")
            legend.AddEntry(h_SingleMuon, "DY", "l")
            legend.AddEntry(dummy, f"{(selectedEvents['SingleMuon'][0]/totalEvents['SingleMuon'][0])*100:.2f}% selected Events", "")
            legend.AddEntry(dummy, f"{(selectedEvents['SingleMuon'][1]/totalEvents['SingleMuon'][1])*100:.2f}% selected PFCands", "")

            legend.AddEntry(h_MinBias, "ZeroBias", "l")
            legend.AddEntry(dummy, f"{(selectedEvents['MinBias'][0]/totalEvents['MinBias'][0])*100:.2f}% selected Events", "")
            legend.AddEntry(dummy, f"{(selectedEvents['MinBias'][1]/totalEvents['MinBias'][1])*100:.2f}% selected PFCands", "")
        
        if quantile_reference == "MC" or quantile_reference == "both":
            legend.AddEntry(dummy, "#bf{MC}", "")
            legend.AddEntry(h_MCDY, "DY", "l")
            legend.AddEntry(dummy, f"{(selectedEvents['MCDY'][0]/totalEvents['MCDY'][0])*100:.2f}% selected Events", "")
            legend.AddEntry(dummy, f"{(selectedEvents['MCDY'][1]/totalEvents['MCDY'][1])*100:.2f}% selected PFCands", "")

            legend.AddEntry(h_MCMinBias, "ZeroBias", "l")
            legend.AddEntry(dummy, f"{(selectedEvents['MCMinBias'][0]/totalEvents['MCMinBias'][0])*100:.2f}% selected Events", "")
            legend.AddEntry(dummy, f"{(selectedEvents['MCMinBias'][1]/totalEvents['MCMinBias'][1])*100:.2f}% selected PFCands", "")

        legend.Draw()

        canvas.cd()
        pad2 = ROOT.TPad("pad2", "pad2", 0, 0, 1, 0.35)
        pad2.Draw()
        pad2.cd()
        pad2.SetTopMargin(0.05)
        pad2.SetBottomMargin(0.35)
        pad2.SetRightMargin(0.26)

        pad2.SetGridy(1)
        pad2.SetTicky(0)

        if var not in ["PFCands_eta", "PFCands_phi", "PFCands_pvAssocQuality"]:
            pad2.SetLogy()

        if quantile_reference == "Data" or quantile_reference == "both":
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

        if quantile_reference == "MC" or quantile_reference == "both":
            ratio_MCDYJets = h_MCDY.Clone(f"ratio_{var}")
            ratio_MCDYJets.Divide(h_MCMinBias)
            ratio_MCDYJets.SetLineColor(ROOT.kGray + 2)
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


        if quantile_reference == "Data" or quantile_reference == "both":

            min_val = ratio_SingleMuon.GetBinContent(ratio_SingleMuon.GetMinimumBin())
            if min_val <= 0:
                min_val = 1e-3
            max_val = ratio_SingleMuon.GetBinContent(ratio_SingleMuon.GetMaximumBin())
            if max_val <= 0:
                max_val = 10

            min_val = min_val * 0.2
            max_val = max_val * 10

            ratio_SingleMuon.SetMinimum(min_val)
            ratio_SingleMuon.SetMaximum(max_val)

        if quantile_reference == "MC" or quantile_reference == "both":

            min_val = ratio_MCDYJets.GetBinContent(ratio_MCDYJets.GetMinimumBin())
            if min_val <= 0:
                min_val = 1e-3
            max_val = ratio_MCDYJets.GetBinContent(ratio_MCDYJets.GetMaximumBin())
            if max_val <= 0:
                max_val = 10

            min_val = min_val * 0.2
            max_val = max_val * 10

            ratio_MCDYJets.SetMinimum(min_val)
            ratio_MCDYJets.SetMaximum(max_val)


        # add small inset zoom (bottom-right) for HT variable
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

        inset.DrawFrame(0, 10**(-3), zoom_xmax, 1)
        frame = inset.DrawFrame(
                                0,
                                min(h_SingleMuon.GetMinimum(), h_MinBias.GetMinimum(), h_MCDY.GetMinimum(), h_MCMinBias.GetMinimum()) if quantile_reference == "both" else min(h_SingleMuon.GetMinimum(), h_MinBias.GetMinimum()) if quantile_reference == "Data" else min(h_MCDY.GetMinimum(), h_MCMinBias.GetMinimum()),
                                zoom_xmax,
                                max(h_SingleMuon.GetMaximum(), h_MinBias.GetMaximum(), h_MCDY.GetMaximum(), h_MCMinBias.GetMaximum()) * 1.3 if quantile_reference == "both" else max(h_SingleMuon.GetMaximum(), h_MinBias.GetMaximum()) * 1.3 if quantile_reference == "Data" else max(h_MCDY.GetMaximum(), h_MCMinBias.GetMaximum()) * 1.3
                                )
        frame.GetXaxis().SetLabelSize(0.05)
        frame.GetYaxis().SetLabelSize(0.05)
        frame.GetXaxis().SetTitleSize(0.05)
        frame.GetYaxis().SetTitleSize(0.05)
        frame.GetYaxis().SetNdivisions(10, False)
        inset.SetGridy(1)
        inset.SetTicky(0)
        
        # clone histograms so axis/range changes don't affect main pads
        if quantile_reference == "Data" or quantile_reference == "both":
            h1 = h_SingleMuon.Clone(h_SingleMuon.GetName() + "_inset")
            h2 = h_MinBias.Clone(h_MinBias.GetName() + "_inset")
        if quantile_reference == "MC" or quantile_reference == "both":
            h1MC = h_MCDY.Clone(h_MCDY.GetName() + "_inset")
            h2MC = h_MCMinBias.Clone(h_MCMinBias.GetName() + "_inset")

        for hh in (h1, h2, h1MC, h2MC) if quantile_reference == "both" else (h1, h2) if quantile_reference == "Data" else (h1MC, h2MC):
            hh.SetStats(0)
        if quantile_reference == "Data" or quantile_reference == "both":
            h1.SetLineColor(ROOT.kViolet - 6)
            h1.SetLineWidth(2)
            h1.GetYaxis().SetTitle("")
            h2.SetLineColor(ROOT.kOrange + 5)
            h2.SetLineWidth(2)
            h1.Draw("hist e same")
            h2.Draw("hist e same")
        if quantile_reference == "MC" or quantile_reference == "both":
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

        inset_ratio = ROOT.TPad(f"inset_ratio_{var}", f"inset_ratio_{var}", 0.74, 0.115, 1, 0.34)
        inset_ratio.SetLogy()
        inset_ratio.SetGridy()
        inset_ratio.SetFillStyle(0)
        inset_ratio.SetBorderSize(1)

        inset_ratio.Draw()
        inset_ratio.cd()
        inset_ratio.DrawFrame(0, 10**(-1), zoom_xmax, 100)
        # print(f"Ratio plot y-axis range for {var} inset: {min(ratio_SingleMuon.GetMinimum(), ratio_MCDYJets.GetMinimum())} - {max(ratio_SingleMuon.GetMaximum(), ratio_MCDYJets.GetMaximum())}")
        ymin = (
            min(ratio_SingleMuon.GetMinimum(), ratio_MCDYJets.GetMinimum())
            if quantile_reference == "both"
            else ratio_SingleMuon.GetMinimum()
            if quantile_reference == "Data"
            else ratio_MCDYJets.GetMinimum()
        )
        ymax = (
            max(ratio_SingleMuon.GetMaximum(), ratio_MCDYJets.GetMaximum())
            if quantile_reference == "both"
            else ratio_SingleMuon.GetMaximum()
            if quantile_reference == "Data"
            else ratio_MCDYJets.GetMaximum()
        )
        frame_ratio = inset_ratio.DrawFrame(
                                0,
                                ymin * 0.2,
                                zoom_xmax,
                                ymax * 1.3
                                )
        frame_ratio.GetXaxis().SetLabelSize(0.07)
        frame_ratio.GetYaxis().SetLabelSize(0.07)
        frame_ratio.GetXaxis().SetTitleSize(0.07)
        frame_ratio.GetYaxis().SetTitleSize(0.07)
        frame_ratio.GetXaxis().SetTitle("")
        frame_ratio.GetYaxis().SetTitle("")
        frame_ratio.GetXaxis().SetRangeUser(0, zoom_xmax)
        frame_ratio.GetYaxis().SetNdivisions(10, False)
        inset_ratio.SetGridy(1)
        inset_ratio.SetTicky(0)


        if quantile_reference in ["Data", "both"]:
            hdata_ratio = ratio_SingleMuon.Clone(ratio_SingleMuon.GetName() + "_insetratio")
            hdata_ratio.SetStats(0)
            hdata_ratio.SetLineWidth(2)
            hdata_ratio.Draw("pe same")

        if quantile_reference in ["MC", "both"]:
            hMC_ratio = ratio_MCDYJets.Clone(ratio_MCDYJets.GetName() + "_insetratio")
            hMC_ratio.SetStats(0)
            hMC_ratio.SetLineWidth(2)
            hMC_ratio.Draw("pe same")

        pad2.cd()
        legend_ratio = ROOT.TLegend(0.67, 0.4, 0.725, 0.58)
        legend_ratio.SetBorderSize(0)
        # legend_ratio.SetFillStyle(0)
        legend_ratio.SetTextSize(0.08)
        if quantile_reference == "Data" or quantile_reference == "both":
            legend_ratio.AddEntry(ratio_SingleMuon, "Data", "pe")
        if quantile_reference == "MC" or quantile_reference == "both":
            legend_ratio.AddEntry(ratio_MCDYJets, "MC", "pe")
        legend_ratio.Draw()

        if quantile_reference == "Data" or quantile_reference == "MC":
            output_name = f"new_plots/{var}_QuantileBinning{quantile_reference}{out_suffix}.pdf"
        else:
            output_name = f"new_plots/{var}_QuantileBinning{out_suffix}.pdf"
        canvas.SaveAs(output_name)
        canvas.Close()

def Plot_DiMuonPtCut(df_SingleMuon_var, df_MinBias_var, df_MCDYJets_var, df_MCMinBias_var, variables, pt_cuts, out_suffix, totalEvents, selectedEvents):

    colours = [ROOT.kViolet - 6, ROOT.kBlue - 4, ROOT.kGreen + 3, ROOT.kOrange + 5, ROOT.kRed + 1]

    for var in variables:
        label = VARIABLES[var]
        bins = BINNING[var]
        y_title = "Number of Events (normalised)"

        h_MinBias_ptr = MakeHist(df_MinBias_var, var, label, y_title, bins, f"h_MinBias_{var}_ptscan")
        h_MinBias = h_MinBias_ptr.GetValue()
        NormaliseHist(h_MinBias)

        h_MCMinBias_ptr = MakeHist(df_MCMinBias_var, var, label, y_title, bins, f"h_MCMinBias_{var}_ptscan")
        h_MCMinBias = h_MCMinBias_ptr.GetValue()
        NormaliseHist(h_MCMinBias)

        canvas = ROOT.TCanvas(f"c_ptscan_{var}", "", 800, 700)
        canvas.cd()
        canvas.SetRightMargin(0.19)
        canvas.SetLogy()

        legend_col0 = ROOT.TLegend(0.73, 0.84, 0.85, 0.89)
        legend_col1 = ROOT.TLegend(0.82, 0.01, 0.98, 0.98)
        dummy = ROOT.TObject()
        for legend in (legend_col0, legend_col1):
            legend.SetBorderSize(0)
            legend.SetFillStyle(0)
            legend.SetTextSize(0.015)
            legend.SetMargin(0.2)

        legend_DataStyle = ROOT.TLine(0.0, 0.0, 0.5, 0.0)
        legend_DataStyle.SetLineColor(ROOT.kBlack)
        legend_DataStyle.SetLineWidth(2)
        legend_DataStyle.SetLineStyle(1)

        legend_MCStyle = ROOT.TLine(0.0, 0.0, 0.5, 0.0)
        legend_MCStyle.SetLineColor(ROOT.kBlack)
        legend_MCStyle.SetLineWidth(2)
        legend_MCStyle.SetLineStyle(2)


        histos = []
        plot_max = 0

        for index, pt_cut in enumerate(pt_cuts):
            print(f"Applying diMuon pT cut: {pt_cut} GeV...")

            colour = colours[index % len(colours)]

            df_SingleMuon_cut = DiMuonPtCut(df_SingleMuon_var, pt_cut)
            df_MCDYJets_cut = DiMuonPtCut(df_MCDYJets_var, pt_cut)

            # Redefining the selected events and PFCands after the diMuon pT cut for Data_DY and MC_DY
            selectedEvents['SingleMuon'][0] = df_SingleMuon_cut.Count().GetValue()
            selectedEvents['SingleMuon'][1] = df_SingleMuon_cut.Sum("PFSelection_nPFCands").GetValue()

            selectedEvents['MCDY'][0] = df_MCDYJets_cut.Count().GetValue()
            selectedEvents['MCDY'][1] = df_MCDYJets_cut.Sum("PFSelection_nPFCands").GetValue()


            h_SingleMuon_ptr = MakeHist(df_SingleMuon_cut, var, label, y_title, bins, f"h_SingleMuon_{var}_{pt_cut}GeV")
            h_MCDYJets_ptr = MakeHist(df_MCDYJets_cut, var, label, y_title, bins, f"h_MCDYJets_{var}_{pt_cut}GeV")

            h_SingleMuon= h_SingleMuon_ptr.GetValue()
            NormaliseHist(h_SingleMuon)

            h_MCDYJets= h_MCDYJets_ptr.GetValue()
            NormaliseHist(h_MCDYJets)

            ratio_SingleMuon = h_SingleMuon.Clone(f"ratio_SingleMuon_{var}_{pt_cut}GeV")
            ratio_SingleMuon.Divide(h_MinBias)
            ratio_SingleMuon.SetStats(0)
            ratio_SingleMuon.SetLineColor(colour)
            ratio_SingleMuon.SetLineWidth(2)
            ratio_SingleMuon.GetXaxis().SetTitle(label)
            ratio_SingleMuon.GetXaxis().SetTitleSize(0.025)
            ratio_SingleMuon.GetXaxis().SetLabelSize(0.025)
            ratio_SingleMuon.GetXaxis().SetTitleOffset(1.6)
            ratio_SingleMuon.GetYaxis().SetTitle("DY/MinBias")
            ratio_SingleMuon.GetYaxis().SetLabelSize(0.025)
            ratio_SingleMuon.GetYaxis().SetTitleSize(0.025)

            ratio_MCDYJets = h_MCDYJets.Clone(f"ratio_MCDYJets_{var}_{pt_cut}GeV")
            ratio_MCDYJets.Divide(h_MCMinBias)
            ratio_MCDYJets.SetStats(0)
            ratio_MCDYJets.SetLineColor(colour)
            ratio_MCDYJets.SetLineWidth(2)
            ratio_MCDYJets.SetLineStyle(2)
            ratio_MCDYJets.GetXaxis().SetTitle(label)
            ratio_MCDYJets.GetXaxis().SetTitleSize(0.025)
            ratio_MCDYJets.GetXaxis().SetLabelSize(0.025)
            ratio_MCDYJets.GetXaxis().SetTitleOffset(1.6)
            ratio_MCDYJets.GetYaxis().SetTitle("DY/MinBias")
            ratio_MCDYJets.GetYaxis().SetLabelSize(0.025)
            ratio_MCDYJets.GetYaxis().SetTitleSize(0.025)

            canvas.SetLogy()
            if index == 0:
                ratio_SingleMuon.Draw("hist same")
                ratio_MCDYJets.Draw("hist same")
            else:
                ratio_SingleMuon.Draw("hist same")
                ratio_MCDYJets.Draw("hist same")

            max_val = ratio_SingleMuon.GetBinContent(ratio_SingleMuon.GetMaximumBin())
            if plot_max < max_val:
                plot_max = max_val

            histos.append(ratio_SingleMuon)
            histos.append(ratio_MCDYJets)

            legend_col1.AddEntry(ratio_SingleMuon, f"p^{{#mu#mu}}_{{T}} < {pt_cut} GeV", "l")
            legend_col1.AddEntry(dummy, "#bf{Data}", "")

            legend_col1.AddEntry(dummy, "DY", "")
            legend_col1.AddEntry(dummy, f"{(selectedEvents['SingleMuon'][0]/totalEvents['SingleMuon'][0]) * 100:.2f}% selected Events", "")
            legend_col1.AddEntry(dummy, f"{(selectedEvents['SingleMuon'][1]/totalEvents['SingleMuon'][1]) * 100:.2f}% selected PFCands", "")

            legend_col1.AddEntry(dummy, "ZeroBias", "")
            legend_col1.AddEntry(dummy, f"{(selectedEvents['MinBias'][0]/totalEvents['MinBias'][0]) * 100:.2f}% selected Events", "")
            legend_col1.AddEntry(dummy, f"{(selectedEvents['MinBias'][1]/totalEvents['MinBias'][1]) * 100:.2f}% selected PFCands", "")

            legend_col1.AddEntry(dummy, "#bf{MC}", "")

            legend_col1.AddEntry(dummy, "DY", "")
            legend_col1.AddEntry(dummy, f"{(selectedEvents['MCDY'][0]/totalEvents['MCDY'][0]) * 100:.2f}% selected Events", "")
            legend_col1.AddEntry(dummy, f"{(selectedEvents['MCDY'][1]/totalEvents['MCDY'][1]) * 100:.2f}% selected PFCands", "")

            legend_col1.AddEntry(dummy, "ZeroBias", "")
            legend_col1.AddEntry(dummy, f"{(selectedEvents['MCMinBias'][0]/totalEvents['MCMinBias'][0]) * 100:.2f}% selected Events", "")
            legend_col1.AddEntry(dummy, f"{(selectedEvents['MCMinBias'][1]/totalEvents['MCMinBias'][1]) * 100:.2f}% selected PFCands", "")
            print(f"Finished processing diMuon pT cut: {pt_cut} GeV!\n")

        if histos and plot_max > 0:
            histos[0].SetMaximum(plot_max * 20)

    
        legend_col0.AddEntry(legend_DataStyle, "Data", "l")
        legend_col0.AddEntry(legend_MCStyle, "MC", "l")
        legend_col1.Draw()
        legend_col0.SetTextSize(0.02)
        legend_col0.Draw()


        output_name = f"new_plots/{var}_pTscan{out_suffix}.pdf"
        canvas.SaveAs(output_name)
        canvas.Close()

def Plot_DiMuonPtCut_QuantileBinning(df_SingleMuon_var, df_MinBias_var, df_MCDYJets_var, df_MCMinBias_var, variables, pt_cuts, out_suffix, totalEvents, selectedEvents, quantile_bins=None, quantile_reference="both", zoom_xmax=140):

    colours = [
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
                ROOT.kBlack
                ]

    for var in variables:
        if var in ["PFCands_pt", "PFCands_eta", "PFCands_phi", "PFCands_pvAssocQuality"]:
            continue

        label = VARIABLES[var]
        bins = BINNING[var]
        y_title = "Number of Events (normalised)"

        plot_bins = bins

        # h_MinBias_ptr = MakeHist(df_MinBias_var, var, label, y_title, bins, f"h_MinBias_{var}_ptscan")
        # h_MinBias = h_MinBias_ptr.GetValue()
        # NormaliseHist(h_MinBias)

        # h_MCMinBias_ptr = MakeHist(df_MCMinBias_var, var, label, y_title, bins, f"h_MCMinBias_{var}_ptscan")
        # h_MCMinBias = h_MCMinBias_ptr.GetValue()
        # NormaliseHist(h_MCMinBias)

        if quantile_reference == "Data":
            h_reference_ptr = MakeHist(
                df_MinBias_var, var, label, y_title, bins,
                f"h_SingleMuon_{var}_quantile_ref"
            )

        elif quantile_reference == "MC":
            h_reference_ptr = MakeHist(
                df_MCMinBias_var, var, label, y_title, bins,
                f"h_MCDYJets_{var}_quantile_ref"
            )

        elif quantile_reference == "both":
            # For "both", derive quantile bin edges from Data.
            h_reference_ptr = MakeHist(
                df_MinBias_var, var, label, y_title, bins,
                f"h_SingleMuon_{var}_quantile_ref"
            )

        else:
            raise ValueError(
                "quantile_reference must be 'Data', 'MC', or 'both'"
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

        if quantile_reference == "Data" or quantile_reference == "both":
            h_SingleMuon_ptr = MakeHist(df_SingleMuon_var, var, label, y_title, plot_bins, f"h_SingleMuon_{var}")
            h_MinBias_ptr = MakeHist(df_MinBias_var, var, label, y_title, plot_bins, f"h_MinBias_{var}")
        if quantile_reference == "MC" or quantile_reference == "both":
            h_MCDY_ptr = MakeHist(df_MCDYJets_var, var, label, y_title, plot_bins, f"h_MCDY_{var}")
            h_MCMinBias_ptr = MakeHist(df_MCMinBias_var, var, label, y_title, plot_bins, f"h_MCMinBias_{var}")

        if quantile_reference == "Data" or quantile_reference == "both":
            h_SingleMuon = h_SingleMuon_ptr.GetValue()
            h_MinBias = h_MinBias_ptr.GetValue()
            NormaliseHist(h_SingleMuon, True)
            NormaliseHist(h_MinBias, True)
        if quantile_reference == "MC" or quantile_reference == "both":
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

                if quantile_reference == "Data" or quantile_reference == "both":
                    SingleMuon_low = inverse_cdf_from_hist(h_SingleMuon, 1.0 - q_high)
                    SingleMuon_high = inverse_cdf_from_hist(h_SingleMuon, 1.0 - q_low)
                    MinBias_low = inverse_cdf_from_hist(h_MinBias, 1.0 - q_high)
                    MinBias_high = inverse_cdf_from_hist(h_MinBias, 1.0 - q_low)

                if quantile_reference == "MC" or quantile_reference == "both":
                    MCDY_low = inverse_cdf_from_hist(h_MCDY, 1.0 - q_high)
                    MCDY_high = inverse_cdf_from_hist(h_MCDY, 1.0 - q_low)
                    MCMinBias_low = inverse_cdf_from_hist(h_MCMinBias, 1.0 - q_high)
                    MCMinBias_high = inverse_cdf_from_hist(h_MCMinBias, 1.0 - q_low)

                if quantile_reference == "Data":
                    if SingleMuon_low is None or SingleMuon_high is None or MinBias_low is None or MinBias_high is None:
                        print(f"  [{q_low:.3f}, {q_high:.3f}] -> undefined")
                    else:
                        print(
                            f"  [{q_low:.3f}, {q_high:.3f}] -> "
                            f"Data SingleMuon {SingleMuon_low:.6g} - {SingleMuon_high:.6g}, "
                            f"Data MinBias {MinBias_low:.6g} - {MinBias_high:.6g}"
                        )
                elif quantile_reference == "MC":
                    if MCDY_low is None or MCDY_high is None or MCMinBias_low is None or MCMinBias_high is None:
                        print(f"  [{q_low:.3f}, {q_high:.3f}] -> undefined")
                    else:
                        print(
                            f"  [{q_low:.3f}, {q_high:.3f}] -> "
                            f"MCDY {MCDY_low:.6g} - {MCDY_high:.6g}, "
                            f"MCMinBias {MCMinBias_low:.6g} - {MCMinBias_high:.6g}"
                        )
                elif quantile_reference == "both":
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
        canvas.SetRightMargin(0.19)
        canvas.SetLogy()
        canvas.SetGridy(1)

        
        if quantile_reference == "both":
            pad1 = ROOT.TPad(f"pad1_{var}", "", 0, 0.32, 1, 1)
            pad1.Draw()
            pad1.cd()
            pad1.SetBottomMargin(0.05)
            pad1.SetRightMargin(0.19)
            pad1.SetLogy()
            pad1.SetGridy(1)
            # pad1.SetTicky(0)

            canvas.cd()

            pad2 = ROOT.TPad(f"pad2_{var}", "", 0, 0, 1, 0.35)
            pad2.Draw()
            pad2.cd()
            pad2.SetTopMargin(0.05)
            pad2.SetBottomMargin(0.35)
            pad2.SetRightMargin(0.19)
            pad2.SetGridy(1)
            # pad2.SetTicky(0)

            

        if quantile_reference == "both":
            legend_col0 = ROOT.TLegend(0.73, 0.87, 0.85, 0.92)
        else:
            legend_col0 = ROOT.TLegend(0.73, 0.85, 0.85, 0.9)
        
        legend_col1 = ROOT.TLegend(0.82, 0.01, 0.98, 0.98)
        dummy = ROOT.TObject()

        for legend in (legend_col0, legend_col1):
            legend.SetBorderSize(0)
            legend.SetFillStyle(0)
            legend.SetTextSize(0.015)
            legend.SetMargin(0.2)

        legend_DataStyle = ROOT.TLine(0.0, 0.0, 0.5, 0.0)
        legend_DataStyle.SetLineColor(ROOT.kBlack)
        legend_DataStyle.SetLineWidth(2)
        legend_DataStyle.SetLineStyle(1)

        legend_MCStyle = ROOT.TLine(0.0, 0.0, 0.5, 0.0)
        legend_MCStyle.SetLineColor(ROOT.kBlack)
        legend_MCStyle.SetLineWidth(2)
        legend_MCStyle.SetLineStyle(2)
        
        histos = []
        insent_histos = []
        ratios_pad2 = []
        plot_max = 0

        for index, pt_cut in enumerate(pt_cuts):

            print(f"Applying diMuon pT cut: {pt_cut} GeV...")

            colour = colours[index % len(colours)]
            

            df_SingleMuon_cut = DiMuonPtCut(df_SingleMuon_var, pt_cut)
            df_MCDYJets_cut = DiMuonPtCut(df_MCDYJets_var, pt_cut)

            # Redefining the selected events and PFCands after the diMuon pT cut for Data_DY and MC_DY
            selectedEvents['SingleMuon'][0] = df_SingleMuon_cut.Count().GetValue()
            selectedEvents['SingleMuon'][1] = df_SingleMuon_cut.Sum("PFSelection_nPFCands").GetValue()

            selectedEvents['MCDY'][0] = df_MCDYJets_cut.Count().GetValue()
            selectedEvents['MCDY'][1] = df_MCDYJets_cut.Sum("PFSelection_nPFCands").GetValue()


            if quantile_reference == "Data" or quantile_reference == "both":
                h_SingleMuon_ptr = MakeHist(df_SingleMuon_cut, var, label, y_title, plot_bins, f"h_SingleMuon_{var}_ptcut{pt_cut}GeV")
                h_SingleMuon = h_SingleMuon_ptr.GetValue()
                h_SingleMuon.SetDirectory(0)
                NormaliseHist(h_SingleMuon, True)

                ratio_SingleMuon = h_SingleMuon.Clone(f"ratio_SingleMuon_{var}_{pt_cut}GeV_{index}")
                ratio_SingleMuon.Divide(h_MinBias)
                ratio_SingleMuon.SetStats(0)
                ratio_SingleMuon.SetLineColor(colour)
                ratio_SingleMuon.SetLineWidth(2)
                ratio_SingleMuon.GetXaxis().SetTitle(label)
                ratio_SingleMuon.GetXaxis().SetTitleSize(0.03)
                ratio_SingleMuon.GetXaxis().SetLabelSize(0.03)
                ratio_SingleMuon.GetXaxis().SetTitleOffset(1.4)
                ratio_SingleMuon.GetYaxis().SetTitle("DY/MinBias")
                if quantile_reference == "both":
                    ratio_SingleMuon.GetYaxis().SetLabelSize(0.04)
                    ratio_SingleMuon.GetYaxis().SetTitleSize(0.04)
                    ratio_SingleMuon.GetYaxis().SetTitleOffset(1)
                else:
                    ratio_SingleMuon.GetYaxis().SetLabelSize(0.03)
                    ratio_SingleMuon.GetYaxis().SetTitleSize(0.03)
                ratio_SingleMuon.GetYaxis().SetNdivisions(10, False)

                insent_histos.append(ratio_SingleMuon)


            if quantile_reference == "MC" or quantile_reference == "both":
                h_MCDY_ptr = MakeHist(df_MCDYJets_cut, var, label, y_title, plot_bins, f"h_MCDY_{var}_ptcut{pt_cut}GeV")
                h_MCDY = h_MCDY_ptr.GetValue()
                h_MCDY.SetDirectory(0)
                NormaliseHist(h_MCDY, True)

                ratio_MCDY = h_MCDY.Clone(f"ratio_MCDY_{var}_{pt_cut}GeV_{index}")
                ratio_MCDY.Divide(h_MCMinBias)
                ratio_MCDY.SetStats(0)
                ratio_MCDY.SetLineColor(colour)
                ratio_MCDY.SetLineWidth(2)
                ratio_MCDY.SetLineStyle(2)
                ratio_MCDY.GetXaxis().SetTitle(label)
                ratio_MCDY.GetXaxis().SetTitleSize(0.03)
                ratio_MCDY.GetXaxis().SetLabelSize(0.03)
                ratio_MCDY.GetXaxis().SetTitleOffset(1.4)
                ratio_MCDY.GetYaxis().SetTitle("DY/MinBias")
                if quantile_reference == "both":
                    ratio_MCDY.GetYaxis().SetLabelSize(0.04)
                    ratio_MCDY.GetYaxis().SetTitleSize(0.04)
                else:
                    ratio_MCDY.GetYaxis().SetLabelSize(0.03)
                    ratio_MCDY.GetYaxis().SetTitleSize(0.03)   
                ratio_MCDY.GetYaxis().SetNdivisions(10, False)

                insent_histos.append(ratio_MCDY)         

            if quantile_reference == "both":
                pad1.cd()
            else:
                canvas.cd()
                
            if index == 0:
                if quantile_reference == "Data" or quantile_reference == "both":
                    ratio_SingleMuon.Draw("hist e same")
                    histos.append(ratio_SingleMuon)
                if quantile_reference == "MC" or quantile_reference == "both":
                    ratio_MCDY.Draw("hist e same")
                    histos.append(ratio_MCDY)
            else:
                if quantile_reference == "Data" or quantile_reference == "both":
                    ratio_SingleMuon.Draw("hist e same")
                    histos.append(ratio_SingleMuon)
                if quantile_reference == "MC" or quantile_reference == "both":
                    ratio_MCDY.Draw("hist e same")
                    histos.append(ratio_MCDY)



            legend_col1.AddEntry(dummy, f"#color[{colour}]{{#bf{{p^{{#mu#mu}}_{{T}} < {pt_cut} GeV}}}}", "")

            if quantile_reference == "Data" or quantile_reference == "both":

                max_val = ratio_SingleMuon.GetBinContent(ratio_SingleMuon.GetMaximumBin())
                if plot_max < max_val:
                    plot_max = max_val

                legend_col1.AddEntry(dummy, "#bf{Data}", "")

                legend_col1.AddEntry(dummy, "DY", "")
                legend_col1.AddEntry(dummy, f"{(selectedEvents['SingleMuon'][0]/totalEvents['SingleMuon'][0]) * 100:.2f}% selected Events", "")
                legend_col1.AddEntry(dummy, f"{(selectedEvents['SingleMuon'][1]/totalEvents['SingleMuon'][1]) * 100:.2f}% selected PFCands", "")

                legend_col1.AddEntry(dummy, "ZeroBias", "")
                legend_col1.AddEntry(dummy, f"{(selectedEvents['MinBias'][0]/totalEvents['MinBias'][0]) * 100:.2f}% selected Events", "")
                legend_col1.AddEntry(dummy, f"{(selectedEvents['MinBias'][1]/totalEvents['MinBias'][1]) * 100:.2f}% selected PFCands", "")
            
            if quantile_reference == "MC" or quantile_reference == "both":

                max_val = ratio_MCDY.GetBinContent(ratio_MCDY.GetMaximumBin())
                if plot_max < max_val:
                    plot_max = max_val

                legend_col1.AddEntry(dummy, "#bf{MC}", "")

                legend_col1.AddEntry(dummy, "DY", "")
                legend_col1.AddEntry(dummy, f"{(selectedEvents['MCDY'][0]/totalEvents['MCDY'][0]) * 100:.2f}% selected Events", "")
                legend_col1.AddEntry(dummy, f"{(selectedEvents['MCDY'][1]/totalEvents['MCDY'][1]) * 100:.2f}% selected PFCands", "")

                legend_col1.AddEntry(dummy, "ZeroBias", "")
                legend_col1.AddEntry(dummy, f"{(selectedEvents['MCMinBias'][0]/totalEvents['MCMinBias'][0]) * 100:.2f}% selected Events", "")
                legend_col1.AddEntry(dummy, f"{(selectedEvents['MCMinBias'][1]/totalEvents['MCMinBias'][1]) * 100:.2f}% selected PFCands", "")


            
            if quantile_reference == "both":

                ratio = ratio_SingleMuon.Clone(f"ratio_{var}_{pt_cut}GeV_{index}")
                ratio.Divide(ratio_MCDY)
                ratio.SetDirectory(0)
                ratio.SetStats(0)
                ratio.SetLineColor(colour)
                ratio.SetMarkerColor(colour)
                ratio.SetMarkerStyle(20)
                ratio.SetMarkerSize(0.6)
                ratio.GetYaxis().SetTitle("Data/MC")
                ratio.GetXaxis().SetTitle(label)
                ratio.GetXaxis().SetTitleSize(0.08)
                ratio.GetXaxis().SetTitleOffset(1.3)
                ratio.GetXaxis().SetLabelSize(0.075)
                ratio.GetXaxis().SetTickLength(0.07)
                ratio.GetYaxis().SetTitleSize(0.08)
                ratio.GetYaxis().SetLabelSize(0.075)
                ratio.GetYaxis().SetTitleOffset(0.55)
                pad2.cd()
                ratio.Draw("pe")

            print(f"Finished processing diMuon pT cut: {pt_cut} GeV!\n")
  

        canvas.cd()
        if histos and plot_max > 0:
            histos[0].SetMaximum(plot_max * 2)
        if quantile_reference == "Data" or quantile_reference == "both":
            legend_col0.AddEntry(legend_DataStyle, "Data", "l")
        if quantile_reference == "MC" or quantile_reference == "both":
            legend_col0.AddEntry(legend_MCStyle, "MC", "l")
        canvas.cd()
        legend_col1.Draw()
        legend_col0.SetTextSize(0.02)
        legend_col0.Draw()

        if quantile_reference == "both":
            inset = ROOT.TPad(f"inset_{var}", f"inset_{var}", 0.4, 0.35, 0.8, 0.8)
        else:
            inset = ROOT.TPad(f"inset_{var}", f"inset_{var}", 0.4, 0.1, 0.8, 0.55)
        inset.SetLogy()
        inset.SetFillStyle(0)
        inset.SetBorderSize(1)
        inset.SetRightMargin(0.05)
        inset.SetTopMargin(0.08)
        inset.SetBottomMargin(0.12)
        inset.Draw()
        inset.cd()
        # inset.DrawFrame(0, 10**(-1), zoom_xmax, 10)

        inset.cd()

        ymin = min(hist.GetMinimum() for hist in histos) if histos else 0.1
        if ymin <= 0:
            ymin = 1e-2
        ymax = max(hist.GetMaximum() for hist in histos) if histos else 1
        if ymax <= 0:
            ymax = 10
        frame = inset.DrawFrame(
                                0,
                                ymin,
                                zoom_xmax,
                                ymax
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
        
        
           
        # canvas.cd()

        # inset_ratio = ROOT.TPad(f"inset_ratio_{var}", f"inset_ratio_{var}", 0.74, 0.115, 1, 0.34)
        # inset_ratio.SetLogy()
        # inset_ratio.SetGridy()
        # inset_ratio.SetFillStyle(0)
        # inset_ratio.SetBorderSize(1)

        # inset_ratio.Draw()
        # inset_ratio.cd()
        # inset_ratio.DrawFrame(0, 10**(-1), zoom_xmax, 100)
        # # print(f"Ratio plot y-axis range for {var} inset: {min(ratio_SingleMuon.GetMinimum(), ratio_MCDYJets.GetMinimum())} - {max(ratio_SingleMuon.GetMaximum(), ratio_MCDYJets.GetMaximum())}")
        # ymin = (
        #     min(ratio_SingleMuon.GetMinimum(), ratio_MCDYJets.GetMinimum())
        #     if quantile_reference == "both"
        #     else ratio_SingleMuon.GetMinimum()
        #     if quantile_reference == "Data"
        #     else ratio_MCDYJets.GetMinimum()
        # )
        # ymax = (
        #     max(ratio_SingleMuon.GetMaximum(), ratio_MCDYJets.GetMaximum())
        #     if quantile_reference == "both"
        #     else ratio_SingleMuon.GetMaximum()
        #     if quantile_reference == "Data"
        #     else ratio_MCDYJets.GetMaximum()
        # )
        # frame_ratio = inset_ratio.DrawFrame(
        #                         0,
        #                         ymin * 0.2,
        #                         zoom_xmax,
        #                         ymax * 1.3
        #                         )
        # frame_ratio.GetXaxis().SetLabelSize(0.07)
        # frame_ratio.GetYaxis().SetLabelSize(0.07)
        # frame_ratio.GetXaxis().SetTitleSize(0.07)
        # frame_ratio.GetYaxis().SetTitleSize(0.07)
        # frame_ratio.GetXaxis().SetTitle("")
        # frame_ratio.GetYaxis().SetTitle("")
        # frame_ratio.GetXaxis().SetRangeUser(0, zoom_xmax)
        # frame_ratio.GetYaxis().SetNdivisions(10, False)
        # inset_ratio.SetGridy(1)
        # inset_ratio.SetTicky(0)


        # if quantile_reference in ["Data", "both"]:
        #     hdata_ratio = ratio_SingleMuon.Clone(ratio_SingleMuon.GetName() + "_insetratio")
        #     hdata_ratio.SetStats(0)
        #     hdata_ratio.SetLineWidth(2)
        #     hdata_ratio.Draw("pe same")

        # if quantile_reference in ["MC", "both"]:
        #     hMC_ratio = ratio_MCDYJets.Clone(ratio_MCDYJets.GetName() + "_insetratio")
        #     hMC_ratio.SetStats(0)
        #     hMC_ratio.SetLineWidth(2)
        #     hMC_ratio.Draw("pe same")







        if quantile_reference == "Data":
            output_name = f"new_plots/{var}_pTscan_QuantileBinningData{out_suffix}.pdf"
        elif quantile_reference == "MC":
            output_name = f"new_plots/{var}_pTscan_QuantileBinningMC{out_suffix}.pdf"
        else:
            output_name = f"new_plots/{var}_pTscan_QuantileBinning{out_suffix}.pdf"
            
        canvas.SaveAs(output_name)
        canvas.Close()

def QuantilePerObservable(df_SingleMuon_var, df_MinBias_var, df_MCDYJets_var, df_MCMinBias_var, variables, out_suffix, totalEvents, selectedEvents, bins):

    for var in variables:
        if var in ["PFCands_pt", "PFCands_eta", "PFCands_phi", "PFCands_pvAssocQuality"]:
            continue

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
        df_SingleMuon_q = df_SingleMuon_var.Define(f"{var}_invQ", f"1.0 - {var}InvQMap::eval(PFSelection_{var})")
        df_MCDYJets_q = df_MCDYJets_var.Define(f"{var}_invQ", f"1.0 - {var}InvQMapMC::eval(PFSelection_{var})")
        df_MCMinBias_q = df_MCMinBias_var.Define(f"{var}_invQ", f"1.0 - {var}InvQMapMC::eval(PFSelection_{var})")
        plot_column = f"{var}_invQ"
        plot_xlabel = f"1 - F_{{MB}}({label})"

        edges = array.array("d", bins)

        h_MinBias_ptr = df_MinBias_q.Histo1D(
            (f"h_MinBias_{var}_quantile", f"; {plot_xlabel}; {y_title}", len(edges) - 1, edges),
            plot_column,
        )
        h_SingleMuon_ptr = df_SingleMuon_q.Histo1D(
            (f"h_SingleMuon_{var}_quantile", f"; {plot_xlabel}; {y_title}", len(edges) - 1, edges),
            plot_column,
        )
        h_MCDYJets_ptr = df_MCDYJets_q.Histo1D(
            (f"h_MCDYJets_{var}_quantile", f"; {plot_xlabel}; {y_title}", len(edges) - 1, edges),
            plot_column,
        )
        h_MCMinBias_ptr = df_MCMinBias_q.Histo1D(
            (f"h_MCMinBias_{var}_quantile", f"; {plot_xlabel}; {y_title}", len(edges) - 1, edges),
            plot_column,
        )

        h_MinBias = h_MinBias_ptr.GetValue()
        h_SingleMuon = h_SingleMuon_ptr.GetValue()
        h_MCDYJets = h_MCDYJets_ptr.GetValue()
        h_MCMinBias = h_MCMinBias_ptr.GetValue()

        NormaliseHist(h_MinBias)
        NormaliseHist(h_SingleMuon)
        NormaliseHist(h_MCDYJets)
        NormaliseHist(h_MCMinBias)

        canvas = ROOT.TCanvas(f"c_quantile_{var}")
        canvas.cd()
        canvas.SetBottomMargin(0.13)
        canvas.SetLogy()

        pad1 = ROOT.TPad("pad1", "pad1", 0, 0.32, 1, 1)
        pad1.Draw()
        pad1.cd()
        pad1.SetBottomMargin(0.05)
        # pad1.SetRightMargin(0.26)
        pad1.SetLogy()

        ratio_SingleMuon = h_SingleMuon.Clone(f"ratio_quantile_{var}")
        ratio_SingleMuon.Divide(h_MinBias)
        ratio_SingleMuon.SetLineColor(ROOT.kViolet - 6)
        ratio_SingleMuon.SetLineWidth(2)
        ratio_SingleMuon.GetXaxis().SetTitle("")
        ratio_SingleMuon.GetXaxis().SetTitle(plot_xlabel)
        ratio_SingleMuon.GetYaxis().SetTitle("DY/ZeroBias")
        ratio_SingleMuon.GetXaxis().SetTitleSize(0.035)
        ratio_SingleMuon.GetXaxis().SetTitleOffset(1.3)
        ratio_SingleMuon.GetXaxis().SetLabelSize(0.035)
        ratio_SingleMuon.GetXaxis().SetTickLength(0.03)
        ratio_SingleMuon.GetYaxis().SetTitleSize(0.04)
        ratio_SingleMuon.GetYaxis().SetLabelSize(0.04)
        ratio_SingleMuon.Draw("hist e")

        ratio_MCDYJets = h_MCDYJets.Clone(f"ratio_quantile_mc_{var}")
        ratio_MCDYJets.Divide(h_MCMinBias)
        ratio_MCDYJets.SetLineColor(ROOT.kViolet - 6)
        ratio_MCDYJets.SetLineWidth(2)
        ratio_MCDYJets.SetLineStyle(2)
        ratio_MCDYJets.Draw("hist e same")

        ratio_SingleMuon.SetMaximum(max(ratio_SingleMuon.GetMaximum(), ratio_MCDYJets.GetMaximum()) * 10)

        canvas.cd()

        pad2 = ROOT.TPad("pad2", "pad2", 0, 0, 1, 0.35)
        pad2.Draw()
        pad2.cd()
        pad2.SetTopMargin(0.05)
        pad2.SetBottomMargin(0.35)
        pad2.SetGridy()

        ratio = ratio_SingleMuon.Clone(f"ratio")
        ratio.Divide(ratio_MCDYJets)
        ratio.SetLineColor(ROOT.kBlack)
        ratio.SetMarkerColor(ROOT.kBlack)
        ratio.SetMarkerStyle(20)
        ratio.SetMarkerSize(0.8)
        ratio.GetXaxis().SetTitle(plot_xlabel)
        ratio.GetXaxis().SetTitleSize(0.1)
        ratio.GetXaxis().SetTitleOffset(1.3)
        ratio.GetXaxis().SetLabelSize(0.09)
        ratio.GetXaxis().SetTickLength(0.07)
        ratio.GetYaxis().SetTitle("Ratio")
        ratio.GetYaxis().SetTitleSize(0.09)
        ratio.GetYaxis().SetLabelSize(0.08)
        ratio.GetYaxis().SetTitleOffset(0.5)
        ratio.SetMinimum(0)
        ratio.SetMaximum(2)
        ratio.Draw("pe")


        canvas.cd()
        legend = ROOT.TLegend(0.7, 0.5, 0.84, 0.89)
        dummy = ROOT.TObject()
        legend.SetBorderSize(0)
        legend.SetFillStyle(0)
        legend.SetTextSize(0.02)
        legend.SetMargin(0.2)
        legend.AddEntry(ratio_SingleMuon, "#bf{Data}", "l")

        legend.AddEntry(dummy, "DY", "")
        legend.AddEntry(dummy, f"{(selectedEvents['SingleMuon'][0]/totalEvents['SingleMuon'][0])*100:.2f}% selected Events", "")
        legend.AddEntry(dummy, f"{(selectedEvents['SingleMuon'][1]/totalEvents['SingleMuon'][1])*100:.2f}% selected PFCands", "")

        legend.AddEntry(dummy, "ZeroBias", "")
        legend.AddEntry(dummy, f"{(selectedEvents['MinBias'][0]/totalEvents['MinBias'][0])*100:.2f}% selected Events", "")
        legend.AddEntry(dummy, f"{(selectedEvents['MinBias'][1]/totalEvents['MinBias'][1])*100:.2f}% selected PFCands", "")

        legend.AddEntry(ratio_MCDYJets, "#bf{MC}", "l")

        legend.AddEntry(dummy, "DY", "")
        legend.AddEntry(dummy, f"{(selectedEvents['MCDY'][0]/totalEvents['MCDY'][0])*100:.2f}% selected Events", "")
        legend.AddEntry(dummy, f"{(selectedEvents['MCDY'][1]/totalEvents['MCDY'][1])*100:.2f}% selected PFCands", "")

        legend.AddEntry(dummy, "ZeroBias", "")
        legend.AddEntry(dummy, f"{(selectedEvents['MCMinBias'][0]/totalEvents['MCMinBias'][0])*100:.2f}% selected Events", "")
        legend.AddEntry(dummy, f"{(selectedEvents['MCMinBias'][1]/totalEvents['MCMinBias'][1])*100:.2f}% selected PFCands", "")

        legend.Draw()

        output_dir = f"new_plots/quantile_binning/{bins}"
        os.makedirs(output_dir, exist_ok=True)

        output_name = f"{output_dir}/{var}_Quantile{out_suffix}.pdf"
        canvas.SaveAs(output_name)

        canvas.Close()


def Quantile_DiMuonPtCut(df_SingleMuon_var, df_MinBias_var, df_MCDYJets_var, df_MCMinBias_var, variables, pt_cuts, out_suffix, totalEvents, selectedEvents, bins):


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

        df_MinBias_q = df_MinBias_var.Define(f"{var}_invQ", f"1.0 - {var}InvQMapPtScan::eval(PFSelection_{var})")
        df_SingleMuon_q = df_SingleMuon_var.Define(f"{var}_invQ", f"1.0 - {var}InvQMapPtScan::eval(PFSelection_{var})")
        df_MCDYJets_q = df_MCDYJets_var.Define(f"{var}_invQ", f"1.0 - {var}InvQMapPtScanMC::eval(PFSelection_{var})")
        df_MCMinBias_q = df_MCMinBias_var.Define(f"{var}_invQ", f"1.0 - {var}InvQMapPtScanMC::eval(PFSelection_{var})")



        plot_column = f"{var}_invQ"
        plot_xlabel = f"1 - F_{{MB}}({label})"

        edges = array.array("d", bins)


        h_MinBias_ptr = df_MinBias_q.Histo1D(
            (f"h_MinBias_{var}_quantile_ptscan", f"; {plot_xlabel}; DY/ZeroBias", len(edges) - 1, edges),
            plot_column,
        )
        h_MCMinBias_ptr = df_MCMinBias_q.Histo1D(
            (f"h_MCMinBias_{var}_quantile_ptscan", f"; {plot_xlabel}; DY/ZeroBias", len(edges) - 1, edges),
            plot_column,
        )

        h_MinBias = h_MinBias_ptr.GetValue()
        NormaliseHist(h_MinBias)
        h_MCMinBias = h_MCMinBias_ptr.GetValue()
        NormaliseHist(h_MCMinBias)

        canvas = ROOT.TCanvas(f"c_quantile_ptscan_{var}", "", 800, 700)
        canvas.cd()
        canvas.SetBottomMargin(0.13)
        canvas.SetRightMargin(0.13)
        canvas.SetLogy()

        pad1 = ROOT.TPad(f"pad1_{var}GeV", "pad1", 0, 0.32, 1, 1)
        pad1.SetBottomMargin(0.05)
        pad1.SetRightMargin(0.13)
        pad1.SetLogy()
        pad1.Draw()


        pad2 = ROOT.TPad(f"pad2_{var}GeV", "pad2", 0, 0, 1, 0.35)
        pad2.SetTopMargin(0.05)
        pad2.SetBottomMargin(0.35)
        pad2.SetRightMargin(0.13)
        pad2.SetGridy()
        pad2.Draw()

        

        legend_col0 = ROOT.TLegend(0.79, 0.87, 0.92, 0.92)
        legend_col1 = ROOT.TLegend(0.89, 0.01, 0.95, 0.99)
        dummy = ROOT.TObject()
        for legend in (legend_col0, legend_col1):
            legend.SetBorderSize(0)
            legend.SetFillStyle(0)
            legend.SetTextSize(0.01)
            legend.SetMargin(0.2)

        legend_Data = ROOT.TLine(0.0, 0.0, 0.5, 0.0)
        legend_Data.SetLineColor(ROOT.kBlack)
        legend_Data.SetLineWidth(2)
        legend_Data.SetLineStyle(1)

        legend_MC = ROOT.TLine(0.0, 0.0, 0.5, 0.0)
        legend_MC.SetLineColor(ROOT.kBlack)
        legend_MC.SetLineWidth(2)
        legend_MC.SetLineStyle(2)

        histos = []
        plot_max = 0

        for index, pt_cut in enumerate(pt_cuts):
            
            canvas.cd()
            print(f"Applying diMuon pT cut: {pt_cut} GeV...")
            colour = colours[index]

            df_SingleMuon_cut = DiMuonPtCut(df_SingleMuon_q, pt_cut)
            df_MCDYJets_cut = DiMuonPtCut(df_MCDYJets_q, pt_cut)

            # Redefining the selected events and PFCands after the diMuon pT cut for Data_DY and MC_DY
            selectedEvents['SingleMuon'][0] = df_SingleMuon_cut.Count().GetValue()
            selectedEvents['SingleMuon'][1] = df_SingleMuon_cut.Sum("PFSelection_nPFCands").GetValue()

            selectedEvents['MCDY'][0] = df_MCDYJets_cut.Count().GetValue()
            selectedEvents['MCDY'][1] = df_MCDYJets_cut.Sum("PFSelection_nPFCands").GetValue()

            h_SingleMuon_ptr = df_SingleMuon_cut.Histo1D(
                (f"h_SingleMuon_{var}_quantile_{pt_cut}GeV", f"; {plot_xlabel}; DY/ZeroBias", len(edges) - 1, edges),
                plot_column,
            )
            h_MCDYJets_ptr = df_MCDYJets_cut.Histo1D(
                (f"h_MCDYJets_{var}_quantile_{pt_cut}GeV", f"; {plot_xlabel}; DY/ZeroBias", len(edges) - 1, edges),
                plot_column,
            )

            h_SingleMuon = h_SingleMuon_ptr.GetValue()
            h_MCDYJets = h_MCDYJets_ptr.GetValue()
            NormaliseHist(h_SingleMuon)
            NormaliseHist(h_MCDYJets)

            

            ratio_SingleMuon = h_SingleMuon.Clone(f"ratio_quantile_SingleMuon_{var}_{pt_cut}GeV")
            ratio_SingleMuon.Divide(h_MinBias)
            ratio_SingleMuon.SetStats(0)
            ratio_SingleMuon.SetLineColor(colour)
            ratio_SingleMuon.SetLineWidth(2)
            ratio_SingleMuon.GetXaxis().SetTitle(plot_xlabel)
            ratio_SingleMuon.GetYaxis().SetTitle("DY/MinBias")
            ratio_SingleMuon.GetXaxis().SetTitleSize(0.032)
            ratio_SingleMuon.GetXaxis().SetTitleOffset(0.5)
            ratio_SingleMuon.GetXaxis().SetLabelSize(0.032)
            ratio_SingleMuon.GetXaxis().SetTickLength(0.027)
            ratio_SingleMuon.GetYaxis().SetTitleSize(0.032)
            ratio_SingleMuon.GetYaxis().SetLabelSize(0.032)

            ratio_MCDYJets = h_MCDYJets.Clone(f"ratio_quantile_MCDYJets_{var}_{pt_cut}GeV")
            ratio_MCDYJets.Divide(h_MCMinBias)
            ratio_MCDYJets.SetStats(0)
            ratio_MCDYJets.SetLineColor(colour)
            ratio_MCDYJets.SetLineWidth(2)
            ratio_MCDYJets.SetLineStyle(2)
            ratio_MCDYJets.GetXaxis().SetTitleSize(0.032)
            ratio_MCDYJets.GetXaxis().SetTitleOffset(1.5)
            ratio_MCDYJets.GetXaxis().SetLabelSize(0.032)
            ratio_MCDYJets.GetXaxis().SetTickLength(0.027)
            ratio_MCDYJets.GetYaxis().SetTitleSize(0.032)
            ratio_MCDYJets.GetYaxis().SetLabelSize(0.032)

            pad1.cd()

            if index == 0:
                ratio_SingleMuon.Draw("hist e")
                ratio_MCDYJets.Draw("hist e")
            else:
                ratio_SingleMuon.Draw("hist e same")
                ratio_MCDYJets.Draw("hist e same")

            max_val = ratio_SingleMuon.GetBinContent(ratio_SingleMuon.GetMaximumBin())
            if plot_max < max_val:
                plot_max = max_val

            histos.append(ratio_SingleMuon)
            histos.append(ratio_MCDYJets)


            ratio = ratio_SingleMuon.Clone(f"ratio_final_{var}_{pt_cut}GeV")
            ratio.Divide(ratio_MCDYJets)
            ratio.SetLineColor(colour)
            ratio.SetMarkerColor(colour)
            ratio.SetMarkerStyle(20)
            ratio.SetMarkerSize(0.8)
            ratio.GetXaxis().SetTitle(plot_xlabel)
            ratio.GetXaxis().SetTitleSize(0.08)
            ratio.GetXaxis().SetTitleOffset(1.3)
            ratio.GetXaxis().SetLabelSize(0.07)
            ratio.GetXaxis().SetTickLength(0.07)
            ratio.GetYaxis().SetTitle("Ratio")
            ratio.GetYaxis().SetTitleSize(0.08)
            ratio.GetYaxis().SetLabelSize(0.07)
            ratio.GetYaxis().SetTitleOffset(0.5)
            ratio.SetMinimum(0)
            ratio.SetMaximum(2)

            pad2.cd()
            if index == 0:
                ratio.Draw("pe")
            else:
                ratio.Draw("pe same")

            histos.append(ratio)

            canvas.cd()

            legend_col1.AddEntry(ratio_SingleMuon, f"p^{{#mu#mu}}_{{T}} < {pt_cut} GeV", "l")
            legend_col1.AddEntry(dummy, "#bf{Data}", "")

            legend_col1.AddEntry(dummy, f"DY ({(selectedEvents['SingleMuon'][0]/totalEvents['SingleMuon'][0]) * 100:.2f}%, {(selectedEvents['SingleMuon'][1]/totalEvents['SingleMuon'][1]) * 100:.2f}%)", "")
            # legend_col1.AddEntry(dummy, f"{(selectedEvents['SingleMuon'][0]/totalEvents['SingleMuon'][0]) * 100:.2f}% selected Events", "")
            # legend_col1.AddEntry(dummy, f"{(selectedEvents['SingleMuon'][1]/totalEvents['SingleMuon'][1]) * 100:.2f}% selected PFCands", "")

            legend_col1.AddEntry(dummy, f"ZeroBias ({(selectedEvents['MinBias'][0]/totalEvents['MinBias'][0]) * 100:.2f}%, {(selectedEvents['MinBias'][1]/totalEvents['MinBias'][1]) * 100:.2f}%)", "")
            # legend_col1.AddEntry(dummy, f"{(selectedEvents['MinBias'][0]/totalEvents['MinBias'][0]) * 100:.2f}% selected Events", "")
            # legend_col1.AddEntry(dummy, f"{(selectedEvents['MinBias'][1]/totalEvents['MinBias'][1]) * 100:.2f}% selected PFCands", "")

            legend_col1.AddEntry(dummy, "#bf{MC}", "")

            legend_col1.AddEntry(dummy, f"DY ({(selectedEvents['MCDY'][0]/totalEvents['MCDY'][0]) * 100:.2f}%, {(selectedEvents['MCDY'][1]/totalEvents['MCDY'][1]) * 100:.2f}%)", "")
            # legend_col1.AddEntry(dummy, f"{(selectedEvents['MCDY'][0]/totalEvents['MCDY'][0]) * 100:.2f}% selected Events", "")
            # legend_col1.AddEntry(dummy, f"{(selectedEvents['MCDY'][1]/totalEvents['MCDY'][1]) * 100:.2f}% selected PFCands", "")

            legend_col1.AddEntry(dummy, f"ZeroBias ({(selectedEvents['MCMinBias'][0]/totalEvents['MCMinBias'][0]) * 100:.2f}%, {(selectedEvents['MCMinBias'][1]/totalEvents['MCMinBias'][1]) * 100:.2f}%)", "")
            # legend_col1.AddEntry(dummy, f"{(selectedEvents['MCMinBias'][0]/totalEvents['MCMinBias'][0]) * 100:.2f}% selected Events", "")
            # legend_col1.AddEntry(dummy, f"{(selectedEvents['MCMinBias'][1]/totalEvents['MCMinBias'][1]) * 100:.2f}% selected PFCands", "")

            n_entries = len(pt_cuts) * 7 # 7 entries per pt_cut
            entry_h = 0.009
            y1 = max(0.02, 0.99 - entry_h * n_entries - 0.01) # 0.01 is a small margin from the top of the legend
            print(f"Setting legend y1 to: {y1, n_entries, entry_h, entry_h * n_entries}")

            legend_col1.SetY1(y1)



            print(f"Finished processing diMuon pT cut: {pt_cut} GeV!\n")

        if histos and plot_max > 0:
            histos[0].SetMaximum(plot_max * 30)


        legend_col0.AddEntry(legend_Data, "Data", "l")
        legend_col0.AddEntry(legend_MC, "MC", "l")
        legend_col1.Draw()
        legend_col0.SetTextSize(0.02)
        legend_col0.Draw()

        output_dir = f"new_plots/quantile_binning/{bins}"
        os.makedirs(output_dir, exist_ok=True)

        output_name = f"{output_dir}/{var}_QuantilePtScan{out_suffix}.pdf"
        canvas.SaveAs(output_name)

        canvas.Close()


def Quantile_AllTogether(df_SingleMuon_var, df_MinBias_var, df_MCDYJets_var, df_MCMinBias_var, variables, out_suffix, totalEvents, selectedEvents, bins):

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

    first_ratio.GetXaxis().SetTitle("1 - F_{MB}(x)")
    first_ratio.GetYaxis().SetTitle("DY/ZeroBias")
    first_ratio.GetXaxis().SetTitleSize(0.035)
    first_ratio.GetXaxis().SetTitleOffset(1.3)
    first_ratio.GetXaxis().SetLabelSize(0.035)
    first_ratio.GetXaxis().SetTickLength(0.03)
    first_ratio.GetYaxis().SetTitleSize(0.035)
    first_ratio.GetYaxis().SetLabelSize(0.035)
    first_ratio.SetMaximum(max_val * 10)
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
        ratio.GetXaxis().SetTitle("1 - F_{MB}(x)")
        ratio.GetXaxis().SetTitleSize(0.08)
        ratio.GetXaxis().SetTitleOffset(1.3)
        ratio.GetXaxis().SetLabelSize(0.07)
        ratio.GetXaxis().SetTickLength(0.07)
        ratio.GetYaxis().SetTitle("Ratio")
        ratio.GetYaxis().SetTitleSize(0.08)
        ratio.GetYaxis().SetLabelSize(0.07)
        ratio.GetYaxis().SetTitleOffset(0.5)
        ratio.SetMinimum(0)
        ratio.SetMaximum(2)
        ratio_final_hists.append(ratio)
        

        if var == ratio_final_hists[0][0]:  # Only draw the first ratio to set axes and labels
            ratio.Draw("pe")
        else:
            ratio.Draw("pe same")


    canvas.cd()

    legendVars = ROOT.TLegend(0.76, 0.58, 0.96, 0.9)
    legendStats = ROOT.TLegend(0.76, 0.34, 0.96, 0.58)
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

    legendStats.AddEntry(dummy, f"DY ({(selectedEvents['SingleMuon'][0]/totalEvents['SingleMuon'][0]) * 100:.2f}%, {(selectedEvents['SingleMuon'][1]/totalEvents['SingleMuon'][1]) * 100:.2f}%)", "")
    # legendStats.AddEntry(dummy, f"{(selectedEvents['SingleMuon'][0]/totalEvents['SingleMuon'][0]) * 100:.2f}% selected Events", "")
    # legendStats.AddEntry(dummy, f"{(selectedEvents['SingleMuon'][1]/totalEvents['SingleMuon'][1]) * 100:.2f}% selected PFCands", "")

    legendStats.AddEntry(dummy, f"ZeroBias ({(selectedEvents['MinBias'][0]/totalEvents['MinBias'][0]) * 100:.2f}%, {(selectedEvents['MinBias'][1]/totalEvents['MinBias'][1]) * 100:.2f}%)", "")
    # legendStats.AddEntry(dummy, f"{(selectedEvents['MinBias'][0]/totalEvents['MinBias'][0]) * 100:.2f}% selected Events", "")
    # legendStats.AddEntry(dummy, f"{(selectedEvents['MinBias'][1]/totalEvents['MinBias'][1]) * 100:.2f}% selected PFCands", "")

    legendStats.AddEntry(legend_MC, "#bf{MC}", "l")

    legendStats.AddEntry(dummy, f"DY ({(selectedEvents['MCDY'][0]/totalEvents['MCDY'][0]) * 100:.2f}%, {(selectedEvents['MCDY'][1]/totalEvents['MCDY'][1]) * 100:.2f}%)", "")
    # legendStats.AddEntry(dummy, f"{(selectedEvents['MCDY'][0]/totalEvents['MCDY'][0]) * 100:.2f}% selected Events", "")
    # legendStats.AddEntry(dummy, f"{(selectedEvents['MCDY'][1]/totalEvents['MCDY'][1]) * 100:.2f}% selected PFCands", "")

    legendStats.AddEntry(dummy, f"ZeroBias ({(selectedEvents['MCMinBias'][0]/totalEvents['MCMinBias'][0]) * 100:.2f}%, {(selectedEvents['MCMinBias'][1]/totalEvents['MCMinBias'][1]) * 100:.2f}%)", "")
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


def Quantile_AllTogether_DiMuonPtCut(df_SingleMuon_var, df_MinBias_var, df_MCDYJets_var, df_MCMinBias_var, variables, pt_cuts, out_suffix, totalEvents, selectedEvents, bins):

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
            selectedEvents['SingleMuon'][0] = df_SingleMuon_q.Count().GetValue()
            selectedEvents['SingleMuon'][1] = df_SingleMuon_q.Sum("PFSelection_nPFCands").GetValue()

            selectedEvents['MCDY'][0] = df_MCDYJets_q.Count().GetValue()
            selectedEvents['MCDY'][1] = df_MCDYJets_q.Sum("PFSelection_nPFCands").GetValue()

            plot_column = f"{var}_invQ_all_pt"
            plot_xlabel = "1 - F_{MB}(x)"

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

        first_ratio.GetXaxis().SetTitle("1 - F_{MB}(x)")
        first_ratio.GetYaxis().SetTitle("DY/ZeroBias")
        first_ratio.GetXaxis().SetTitleSize(0.035)
        first_ratio.GetXaxis().SetTitleOffset(1.3)
        first_ratio.GetXaxis().SetLabelSize(0.035)
        first_ratio.GetXaxis().SetTickLength(0.03)
        first_ratio.GetYaxis().SetTitleSize(0.035)
        first_ratio.GetYaxis().SetLabelSize(0.035)
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
            ratio_final.GetXaxis().SetTitle("1 - F_{MB}(x)")
            ratio_final.GetXaxis().SetTitleSize(0.08)
            ratio_final.GetXaxis().SetTitleOffset(1.3)
            ratio_final.GetXaxis().SetLabelSize(0.07)
            ratio_final.GetXaxis().SetTickLength(0.07)
            ratio_final.GetYaxis().SetTitle("Ratio")
            ratio_final.GetYaxis().SetTitleSize(0.08)
            ratio_final.GetYaxis().SetLabelSize(0.07)
            ratio_final.GetYaxis().SetTitleOffset(0.5)
            ratio_final.SetMinimum(0)
            ratio_final.SetMaximum(2)

            if var == ratio_final_hists[0][0]:
                ratio_final.Draw("pe")
            else:
                ratio_final.Draw("pe same")



        pad1.cd()

        legendVars = ROOT.TLegend(0.785, 0.56, 0.935, 0.9)
        legendStats = ROOT.TLegend(0.785, 0.33, 0.935, 0.57)
        dummy = ROOT.TObject()
        for legend in (legendVars, legendStats):
            legend.SetBorderSize(0)
            legend.SetFillStyle(0)
            legend.SetTextSize(0.026)
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

        legendStats.AddEntry(dummy, f"#bf{{p^{{#mu#mu}}_{{T}} < {pt_cut} GeV}}", "")

        legendStats.AddEntry(legend_Data, "#bf{Data}", "l")

        legendStats.AddEntry(dummy, f"DY ({(selectedEvents['SingleMuon'][0]/totalEvents['SingleMuon'][0]) * 100:.2f}%, {(selectedEvents['SingleMuon'][1]/totalEvents['SingleMuon'][1]) * 100:.2f}%)", "")
        # legendStats.AddEntry(dummy, f"{(selectedEvents['SingleMuon'][0]/totalEvents['SingleMuon'][0]) * 100:.2f}% selected Events", "")
        # legendStats.AddEntry(dummy, f"{(selectedEvents['SingleMuon'][1]/totalEvents['SingleMuon'][1]) * 100:.2f}% selected PFCands", "")

        legendStats.AddEntry(dummy, f"ZeroBias ({(selectedEvents['MinBias'][0]/totalEvents['MinBias'][0]) * 100:.2f}%, {(selectedEvents['MinBias'][1]/totalEvents['MinBias'][1]) * 100:.2f}%)", "")
        # legendStats.AddEntry(dummy, f"{(selectedEvents['MinBias'][0]/totalEvents['MinBias'][0]) * 100:.2f}% selected Events", "")
        # legendStats.AddEntry(dummy, f"{(selectedEvents['MinBias'][1]/totalEvents['MinBias'][1]) * 100:.2f}% selected PFCands", "")

        legendStats.AddEntry(legend_MC, "#bf{MC}", "l")

        legendStats.AddEntry(dummy, f"DY ({(selectedEvents['MCDY'][0]/totalEvents['MCDY'][0]) * 100:.2f}%, {(selectedEvents['MCDY'][1]/totalEvents['MCDY'][1]) * 100:.2f}%)", "")
        # legendStats.AddEntry(dummy, f"{(selectedEvents['MCDY'][0]/totalEvents['MCDY'][0]) * 100:.2f}% selected Events", "")
        # legendStats.AddEntry(dummy, f"{(selectedEvents['MCDY'][1]/totalEvents['MCDY'][1]) * 100:.2f}% selected PFCands", "")

        legendStats.AddEntry(dummy, f"ZeroBias ({(selectedEvents['MCMinBias'][0]/totalEvents['MCMinBias'][0]) * 100:.2f}%, {(selectedEvents['MCMinBias'][1]/totalEvents['MCMinBias'][1]) * 100:.2f}%)", "")
        # legendStats.AddEntry(dummy, f"{(selectedEvents['MCMinBias'][0]/totalEvents['MCMinBias'][0]) * 100:.2f}% selected Events", "")
        # legendStats.AddEntry(dummy, f"{(selectedEvents['MCMinBias'][1]/totalEvents['MCMinBias'][1]) * 100:.2f}% selected PFCands", "")

        legendVars.Draw()
        legendStats.Draw()

        # output_name = f"new_plots/AllVariables_QuantileAllTogether_ZpT{pt_cut}GeV{out_suffix}.pdf"
        # canvas.SaveAs(output_name)

        output_dir = f"new_plots/quantile_binning/{bins}"
        os.makedirs(output_dir, exist_ok=True)

        output_name = f"{output_dir}/AllVariables_QuantileAllTogether_ZpT{pt_cut}GeV{out_suffix}.pdf"
        canvas.SaveAs(output_name)
        canvas.Close()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Combined plotting driver for NanoAOD PF-candidate studies"
    )
    parser.add_argument(
        "--mode",
        choices=["compare", "compare-quantilebinning", "ptscan", "ptscan-quantilebinning", "quantile", "quantile-ptscan", "quantile-all", "quantile-all-ptscan", "quantiles", "all"],
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
        type=float,
        nargs="+",
        default=[1, 4, 10, 20],
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
        type=bool,
        default=False,
        help="If True, adjust file paths for running on the CERN SLURM cluster (default: False)",
    )
    return parser.parse_args()
    

def main():

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

    if args.slurm == True:
        totalEvents = TotalEvents()
        selectedEvents = SelectedEvents(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias)
    else:
        totalEvents = TotalEvents_local()
        selectedEvents = SelectedEvents_local(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias)

    if args.no_plot:
        print("Selections finished. Plotting disabled by --no-plot.")
        return

    if args.mode in ["compare", "all"]:
        Plot_CompareTriggers(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias, args.vars, args.output_suffix, totalEvents, selectedEvents)

    if args.mode in ["compare-quantilebinning", "all"]:
        Plot_CompareTriggers_QuantileBinning(
            df_SingleMuon,
            df_MinBias,
            df_MCDYJets,
            df_MCMinBias,
            args.vars,
            args.output_suffix,
            totalEvents,
            selectedEvents,
            args.quantile_bins,
            args.quantile_reference,
            args.zoomxmax,
        )

    if args.mode in ["ptscan", "all"]:
        Plot_DiMuonPtCut(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias, args.vars, args.pt_cuts, args.output_suffix, totalEvents, selectedEvents)

    if args.mode in ["ptscan-quantilebinning", "all"]:
        Plot_DiMuonPtCut_QuantileBinning(
            df_SingleMuon,
            df_MinBias,
            df_MCDYJets,
            df_MCMinBias,
            args.vars,
            args.pt_cuts,
            args.output_suffix,
            totalEvents,
            selectedEvents,
            args.quantile_bins,
            args.quantile_reference,
            args.zoomxmax,
        )

    if args.mode in ["quantile-ptscan", "all"]:
        Quantile_DiMuonPtCut(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias, args.vars, args.pt_cuts, args.output_suffix, totalEvents, selectedEvents, args.quantile_bins)

    if args.mode in ["quantile", "quantiles", "all"]:
        QuantilePerObservable(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias, args.vars, args.output_suffix, totalEvents, selectedEvents, args.quantile_bins)

    if args.mode in ["quantile-ptscan", "quantiles", "all"]:
        Quantile_DiMuonPtCut(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias, args.vars, args.pt_cuts, args.output_suffix, totalEvents, selectedEvents, args.quantile_bins)

    if args.mode in ["quantile-all", "quantiles", "all"]:
        Quantile_AllTogether(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias, args.vars, args.output_suffix, totalEvents, selectedEvents, args.quantile_bins)

    if args.mode in ["quantile-all-ptscan", "quantiles", "all"]:
        Quantile_AllTogether_DiMuonPtCut(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias, args.vars, args.pt_cuts, args.output_suffix, totalEvents, selectedEvents, args.quantile_bins)

if __name__ == "__main__":
    main()
