import argparse
import array
import ROOT
import glob
import pandas as pd
import os
import pprint

path = "/pnfs/psi.ch/cms/trivcat/store/user/zoghafoo/crabsubmission_files/selEvents"

DATASETS = [
            "SingleMuon",
            "MinBias",
            "MCDY",
            "MCMinBias"
           ]

FILES = [
         f"{path}/SingleMuon_SelectedEvents.root",
         f"{path}/MinBias_SelectedEvents.root",
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


def NormaliseHist(hist):
    integral = hist.Integral()
    if integral > 0:
        hist.Scale(1.0 / integral)
    else:
        print(f"Warning: histogram '{hist.GetName()}' has zero integral; skipping normalization")
    hist.SetStats(0)


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
        h_SingleMuon.Draw("hist")

        h_MinBias.SetLineColor(ROOT.kOrange + 5)
        h_MinBias.SetLineWidth(2)
        h_MinBias.Draw("hist same")

        h_MCDYJets.SetLineColor(ROOT.kViolet - 6)
        h_MCDYJets.SetLineWidth(2)
        h_MCDYJets.SetLineStyle(2)
        h_MCDYJets.Draw("hist same")

        h_MCMinBias.SetLineColor(ROOT.kOrange + 5)
        h_MCMinBias.SetLineWidth(2)
        h_MCMinBias.SetLineStyle(2)
        h_MCMinBias.Draw("hist same")

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
        ratio_SingleMuon.GetYaxis().SetTitle("DY/ZeroBias")
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

        legend_ratio = ROOT.TLegend(0.67, 0.4, 0.725, 0.58)
        legend_ratio.SetBorderSize(0)
        # legend_ratio.SetFillStyle(0)
        legend_ratio.SetTextSize(0.08)
        legend_ratio.AddEntry(ratio_SingleMuon, "Data", "pe")
        legend_ratio.AddEntry(ratio_MCDYJets, "MC", "pe")
        legend_ratio.Draw()

        output_name = f"new_plots/{var}{out_suffix}.pdf"
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
                ratio_SingleMuon.Draw("hist")
                ratio_MCDYJets.Draw("hist")
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
            histos[0].SetMaximum(plot_max * 10)

    
        legend_col0.AddEntry(legend_DataStyle, "Data", "l")
        legend_col0.AddEntry(legend_MCStyle, "MC", "l")
        legend_col1.Draw()
        legend_col0.SetTextSize(0.02)
        legend_col0.Draw()


        output_name = f"new_plots/{var}_pTscan{out_suffix}.pdf"
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
        choices=["compare", "ptscan", "quantile", "quantile-ptscan", "quantile-all", "quantile-all-ptscan", "quantiles", "all"],
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
        "--compare-vars",
        nargs="+",
        default=VARIABLES.keys(),
        choices=sorted(VARIABLES.keys()),
        help="Variables to plot in compare mode",
    )
    parser.add_argument(
        "--ptscan-vars",
        nargs="+",
        default=VARIABLES.keys(),
        choices=sorted(VARIABLES.keys()),
        help="Variables to plot in ptscan mode",
    )
    parser.add_argument(
        "--quantile-vars",
        nargs="+",
        default=VARIABLES.keys(),
        choices=sorted(VARIABLES.keys()),
        help="Variables to plot in quantile mode",
    )
    parser.add_argument(
        "--quantile-ptscan-vars",
        nargs="+",
        default=VARIABLES.keys(),
        choices=sorted(VARIABLES.keys()),
        help="Variables to plot in quantile pT-scan mode",
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
    return parser.parse_args()


def main():
    args = parse_args()

    pprint.pprint(vars(args))

    df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias = MakeDataframes(args.maxevents)

    if args.save_event_counts:
        totalEvents = TotalEvents()
        selectedEvents = SelectedEvents(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias)

    if args.no_plot:
        print("Selections finished. Plotting disabled by --no-plot.")
        return

    if args.mode in ["compare", "all"]:
        Plot_CompareTriggers(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias, args.compare_vars, args.output_suffix, totalEvents, selectedEvents)

    if args.mode in ["ptscan", "all"]:
        Plot_DiMuonPtCut(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias, args.ptscan_vars, args.pt_cuts, args.output_suffix, totalEvents, selectedEvents)

    if args.mode in ["quantile", "quantiles", "all"]:
        QuantilePerObservable(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias, args.quantile_vars, args.output_suffix, totalEvents, selectedEvents, args.quantile_bins)

    if args.mode in ["quantile-ptscan", "quantiles", "all"]:
        Quantile_DiMuonPtCut(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias, args.quantile_ptscan_vars, args.pt_cuts, args.output_suffix, totalEvents, selectedEvents, args.quantile_bins)

    if args.mode in ["quantile-all", "quantiles", "all"]:
        Quantile_AllTogether(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias, args.quantile_vars, args.output_suffix, totalEvents, selectedEvents, args.quantile_bins)

    if args.mode in ["quantile-all-ptscan", "quantiles", "all"]:
        Quantile_AllTogether_DiMuonPtCut(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias, args.quantile_ptscan_vars, args.pt_cuts, args.output_suffix, totalEvents, selectedEvents, args.quantile_bins)

if __name__ == "__main__":
    main()
