import argparse
import array
import ROOT

ROOT.gStyle.SetOptStat(0)

FILE_NAMES_SINGLEMUON = [
    "/home/z/zoghafoo/CMSSW_10_6_26/src/Configuration/WMassNanoProduction/NanoV9DataPostVFP_PF_SingleMuon_100000Events_skip0.root",
    "/home/z/zoghafoo/CMSSW_10_6_26/src/Configuration/WMassNanoProduction/NanoV9DataPostVFP_PF_SingleMuon_100000Events_skip100000.root",
    "/home/z/zoghafoo/CMSSW_10_6_26/src/Configuration/WMassNanoProduction/NanoV9DataPostVFP_PF_SingleMuon_100000Events_skip200000.root",
    "/home/z/zoghafoo/CMSSW_10_6_26/src/Configuration/WMassNanoProduction/NanoV9DataPostVFP_PF_SingleMuon_100000Events_skip300000.root",
]

FILE_NAMES_ZEROBIAS = [
    "/home/z/zoghafoo/CMSSW_10_6_26/src/Configuration/WMassNanoProduction/NanoV9DataPostVFP_PF_ZeroBias_100000Events_skip0.root",
    "/home/z/zoghafoo/CMSSW_10_6_26/src/Configuration/WMassNanoProduction/NanoV9DataPostVFP_PF_ZeroBias_100000Events_skip100000.root",
    "/home/z/zoghafoo/CMSSW_10_6_26/src/Configuration/WMassNanoProduction/NanoV9DataPostVFP_PF_ZeroBias_100000Events_skip200000.root",
    "/home/z/zoghafoo/CMSSW_10_6_26/src/Configuration/WMassNanoProduction/NanoV9DataPostVFP_PF_ZeroBias_100000Events_skip300000.root",
    "/home/z/zoghafoo/CMSSW_10_6_26/src/Configuration/WMassNanoProduction/NanoV9DataPostVFP_PF_ZeroBias_100000Events_skip400000.root",
]

VARIABLES = {
    "PFCands_pt": "p_{T} [GeV]",
    "PFCands_eta": "\\eta",
    "PFCands_phi": "\\phi",
    "PFCands_mass": "m [GeV]",
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

DEFAULT_COMPARE_VARS = [
    "PFCands_pt",
    "PFCands_eta",
    "PFCands_phi",
    "PFCands_InvariantMass",
    "PFCands_pvAssocQuality",
    "nPFCands",
    "PFCands_Ht",
    "PFCands_Pt2sum",
    "PFCands_Psum",
    "PFCands_P2sum",
]

DEFAULT_PTSCAN_VARS = [
    "PFCands_InvariantMass",
]


def MakeDataframes(maxevents=None):
    df_SingleMuon = ROOT.RDataFrame("Events", set(FILE_NAMES_SINGLEMUON))
    df_MinBias = ROOT.RDataFrame("Events", set(FILE_NAMES_ZEROBIAS))

    if maxevents is not None:
        print(f"Processing only the first {maxevents} events from each file.")
        df_SingleMuon = df_SingleMuon.Range(maxevents)
        df_MinBias = df_MinBias.Range(maxevents)

    return df_SingleMuon, df_MinBias


def PrintDatasetCounts(df_SingleMuon, df_MinBias):
    total_events_single = df_SingleMuon.Count().GetValue()
    total_events_minbias = df_MinBias.Count().GetValue()
    print(f"Total number of events in SingleMuon file: {total_events_single}")
    print(f"Total number of events in MinBias file: {total_events_minbias}\n")

    total_pfcands_single = df_SingleMuon.Sum("nPFCands").GetValue()
    total_pfcands_minbias = df_MinBias.Sum("nPFCands").GetValue()
    print(f"Total number of PF Candidates in SingleMuon file: {total_pfcands_single}")
    print(f"Total number of PF Candidates in MinBias file: {total_pfcands_minbias}\n")

    return {
        "total_events_single": total_events_single,
        "total_events_minbias": total_events_minbias,
        "total_pfcands_single": total_pfcands_single,
        "total_pfcands_minbias": total_pfcands_minbias,
    }


def VetoMuons(df):
    df = df.Define("Muon_veto",
                   "Muon_standalonePt > 15 && Muon_highPurity && " "Muon_standaloneNumberOfValidHits >= 1 && Muon_looseId && "
                    "abs(Muon_dxybs) < 0.05"
                    )
    return df


def GoodMuons(df):
    df = df.Filter("ROOT::VecOps::Sum(Muon_veto) == 2")
    df = df.Define("Muon_good",
                   "Muon_pt > 26 && "
                   "abs(Muon_eta) < 2.4"
                   )
    df = df.Filter("ROOT::VecOps::Sum(Muon_good) == 2")
    return df


def DiMuonSelection(df):
    df = df.Define("Muon_sel", "Muon_veto && Muon_good")
    df = df.Filter("ROOT::VecOps::Sum(Muon_sel) == 2")
    df = df.Define("Muon_idx", "ROOT::VecOps::Nonzero(Muon_sel)")
    df = df.Filter("Muon_charge[Muon_idx[0]] * Muon_charge[Muon_idx[1]] < 0")
    df = df.Define("diMuon_pT", "pow(pow(Muon_pt[Muon_idx[0]] * cos(Muon_phi[Muon_idx[0]]) + Muon_pt[Muon_idx[1]] * cos(Muon_phi[Muon_idx[1]]), 2) + pow(Muon_pt[Muon_idx[0]] * sin(Muon_phi[Muon_idx[0]]) + Muon_pt[Muon_idx[1]] * sin(Muon_phi[Muon_idx[1]]), 2), 0.5)")
    return df


def PVSelection(df_SingleMuon, df_MinBias):
    df_SingleMuon = df_SingleMuon.Define(
        "PFCands_vertexRefUnique",
        """
        std::set<int> sorted_unique(PFCands_vertexRef.begin(), PFCands_vertexRef.end());
        return ROOT::VecOps::RVec<int>(sorted_unique.begin(), sorted_unique.end());
        """,
    )
    df_SingleMuon = df_SingleMuon.Define(
        "PFCands_vertexRefRandom",
        """
        if (PFCands_vertexRefUnique.size() == 0) return -1;
        return PFCands_vertexRefUnique[0];
        """,
    )

    df_MinBias = df_MinBias.Define(
        "PFCands_vertexRefUnique",
        """
        std::set<int> sorted_unique(PFCands_vertexRef.begin(), PFCands_vertexRef.end());
        return ROOT::VecOps::RVec<int>(sorted_unique.begin(), sorted_unique.end());
        """,
    )
    df_MinBias = df_MinBias.Define(
        "PFCands_vertexRefRandom",
        """
        if (PFCands_vertexRefUnique.size() == 0) return -1;
        return PFCands_vertexRefUnique[gRandom->Integer(PFCands_vertexRefUnique.size())];
        """,
    )

    return df_SingleMuon, df_MinBias


def PFCandidateSelection(df, elec_charge):
    df = df.Define(
        "PF",
        f"""
        (abs(PFCands_charge) == {elec_charge}) &&
        (PFCands_vertexRef == PFCands_vertexRefRandom) &&
        ((PFCands_pvAssocQuality == 6) || (PFCands_pvAssocQuality == 7)) &&
        (abs(PFCands_pdgId) != 13)
        """,
    )
    df = df.Filter("ROOT::VecOps::Sum(PF != 0.f) >= 2")
    df = df.Define("PFSelection_idx", "ROOT::VecOps::Nonzero(PF)")
    df = df.Define("nPFSelection", "PFSelection_idx.size()")
    return df


def addInvariantMass(df):
    df = df.Define(
        "PFCands_InvariantMass",
        """
        TLorentzVector sum;
        for (auto idx : PFSelection_idx) {
            TLorentzVector p4;
            p4.SetPtEtaPhiM(PFCands_pt[idx], PFCands_eta[idx], PFCands_phi[idx], PFCands_mass[idx]);
            sum += p4;
        }
        return sum.M();
        """
    )
    return df


def DiMuonPtCut(df, pt_cut):
    df = df.Filter(f"diMuon_pT < {pt_cut}")
    return df


def ObservablesCalculation(df_SingleMuon, df_MinBias, var):
    if var in ["PFCands_pt", "PFCands_eta", "PFCands_phi", "PFCands_pvAssocQuality"]:
        return (
            df_SingleMuon.Define(f"PFSelection_{var}", f"Take({var}, PFSelection_idx)"),
            df_MinBias.Define(f"PFSelection_{var}", f"Take({var}, PFSelection_idx)"),
            "Number of PF Candidates (normalised)",
        )

    if var == "PFCands_InvariantMass":
        return (
            df_SingleMuon.Define(f"PFSelection_{var}", "PFCands_InvariantMass"),
            df_MinBias.Define(f"PFSelection_{var}", "PFCands_InvariantMass"),
            "Number of Events (normalised)",
        )

    if var == "nPFCands":
        return (
            df_SingleMuon.Define(f"PFSelection_{var}", "PFSelection_idx.size()"),
            df_MinBias.Define(f"PFSelection_{var}", "PFSelection_idx.size()"),
            "Number of Events (normalised)",
        )

    if var == "PFCands_Ht":
        expr = "ROOT::VecOps::Sum(Take(PFCands_pt, PFSelection_idx))"
        return (
            df_SingleMuon.Define(f"PFSelection_{var}", expr),
            df_MinBias.Define(f"PFSelection_{var}", expr),
            "Number of Events (normalised)",
        )

    if var == "PFCands_Pt2sum":
        expr = "ROOT::VecOps::Sum(Take(PFCands_pt * PFCands_pt, PFSelection_idx))"
        return (
            df_SingleMuon.Define(f"PFSelection_{var}", expr),
            df_MinBias.Define(f"PFSelection_{var}", expr),
            "Number of Events (normalised)",
        )

    if var == "PFCands_Psum":
        expr = "ROOT::VecOps::Sum(Take(PFCands_p, PFSelection_idx))"
        return (
            df_SingleMuon.Define(f"PFSelection_{var}", expr),
            df_MinBias.Define(f"PFSelection_{var}", expr),
            "Number of Events (normalised)",
        )

    if var == "PFCands_P2sum":
        expr = "ROOT::VecOps::Sum(Take(PFCands_p * PFCands_p, PFSelection_idx))"
        return (
            df_SingleMuon.Define(f"PFSelection_{var}", expr),
            df_MinBias.Define(f"PFSelection_{var}", expr),
            "Number of Events (normalised)",
        )

    raise ValueError(f"Unsupported variable '{var}'")


def MakeHist(df, var, label, y_title, bins, hist_name):
    title = f"; {label}; {y_title}"
    if len(bins) == 3:
        return df.Histo1D((hist_name, title, bins[0], bins[1], bins[2]), f"PFSelection_{var}")

    edges = array.array("d", bins)
    return df.Histo1D((hist_name, title, len(edges) - 1, edges), f"PFSelection_{var}")


def NomaliseHist(hist):
    integral = hist.Integral()
    if integral > 0:
        hist.Scale(1.0 / integral)
    else:
        print(f"Warning: histogram '{hist.GetName()}' has zero integral; skipping normalization")
    hist.SetStats(0)


def Plot_CompareTriggers(df_SingleMuon, df_MinBias, variables, out_suffix):
    selected_events_single = df_SingleMuon.Count().GetValue()
    selected_events_minbias = df_MinBias.Count().GetValue()
    selected_pfcands_single = df_SingleMuon.Sum("nPFSelection").GetValue()
    selected_pfcands_minbias = df_MinBias.Sum("nPFSelection").GetValue()

    print(f"Number of selected events in SingleMuon file: {selected_events_single}")
    print(f"Number of selected events in MinBias file: {selected_events_minbias}\n")
    print(f"Number of selected PF candidates in SingleMuon file: {selected_pfcands_single}")
    print(f"Number of selected PF candidates in MinBias file: {selected_pfcands_minbias}")

    for var in variables:
        label = VARIABLES[var]
        bins = BINNING[var]

        df_SingleMuon_var, df_MinBias_var, y_title = ObservablesCalculation(df_SingleMuon, df_MinBias, var)
        h_single_ptr = MakeHist(df_SingleMuon_var, var, label, y_title, bins, f"h_SingleMuon_{var}")
        h_minbias_ptr = MakeHist(df_MinBias_var, var, label, y_title, bins, f"h_MinBias_{var}")

        h_single = h_single_ptr.GetValue()
        h_minbias = h_minbias_ptr.GetValue()
        NomaliseHist(h_single)
        NomaliseHist(h_minbias)

        canvas = ROOT.TCanvas(f"c_{var}")

        pad1 = ROOT.TPad("pad1", "pad1", 0, 0.32, 1, 1)
        pad1.Draw()
        pad1.cd()
        pad1.SetBottomMargin(0.05)
        pad1.SetRightMargin(0.32)
        pad1.SetLogy()
        h_single.GetXaxis().SetLabelSize(0)
        h_single.SetLineColor(ROOT.kViolet - 6)
        h_single.SetLineWidth(2)
        h_single.GetXaxis().SetTitle("")
        h_single.GetYaxis().SetTitle(y_title)
        h_single.GetYaxis().SetLabelSize(0.048)
        h_single.GetYaxis().SetTitleSize(0.045)
        h_single.GetYaxis().SetTitleOffset(1)
        h_single.Draw("hist")

        h_minbias.SetLineColor(ROOT.kOrange + 5)
        h_minbias.SetLineWidth(2)
        h_minbias.Draw("hist same")

        h_single.SetMaximum(max(h_single.GetMaximum(), h_minbias.GetMaximum()) * 1.3)

        legend = ROOT.TLegend(0.68, 0.58, 1, 0.87)
        dummy = ROOT.TObject()
        legend.SetBorderSize(0)
        legend.SetFillStyle(0)
        legend.SetTextSize(0.04)
        legend.SetMargin(0.2)
        legend.AddEntry(h_single, "SingleMuon Trigger", "l")
        legend.AddEntry(dummy, f"{selected_events_single/total} selected events", "")
        legend.AddEntry(dummy, f"{selected_pfcands_single} selected PF candidates", "")
        legend.AddEntry(h_minbias, "ZeroBias Trigger", "l")
        legend.AddEntry(dummy, f"{selected_events_minbias} selected events", "")
        legend.AddEntry(dummy, f"{selected_pfcands_minbias} selected PF candidates", "")
        legend.Draw()

        canvas.cd()
        pad2 = ROOT.TPad("pad2", "pad2", 0, 0, 1, 0.35)
        pad2.Draw()
        pad2.cd()
        pad2.SetTopMargin(0.05)
        pad2.SetBottomMargin(0.35)
        pad2.SetRightMargin(0.32)
        pad2.SetLogy()

        ratio = h_single.Clone(f"ratio_{var}")
        ratio.Divide(h_minbias)
        ratio.SetLineColor(ROOT.kBlack)
        ratio.SetMarkerStyle(20)
        ratio.SetMarkerSize(0.8)
        ratio.GetYaxis().SetTitle("SingleMuon / ZeroBias")
        ratio.GetXaxis().SetTitle(label)
        ratio.GetXaxis().SetTitleSize(0.1)
        ratio.GetXaxis().SetTitleOffset(1.3)
        ratio.GetXaxis().SetLabelSize(0.09)
        ratio.GetXaxis().SetTickLength(0.07)
        ratio.GetYaxis().SetTitleSize(0.09)
        ratio.GetYaxis().SetLabelSize(0.09)
        ratio.GetYaxis().SetTitleOffset(0.5)
        pad2.SetGridy()

        min_val = ratio.GetBinContent(ratio.GetMinimumBin())
        if min_val <= 0:
            min_val = 1e-3
        max_val = ratio.GetBinContent(ratio.GetMaximumBin())
        if max_val <= 0:
            max_val = 10

        ratio.SetMinimum(min_val * 0.2)
        ratio.SetMaximum(max_val * 10)
        ratio.Draw("pe")

        legend_ratio = ROOT.TLegend(0.62, 0.4, 0.675, 0.5)
        legend_ratio.SetBorderSize(0)
        # legend_ratio.SetFillStyle(0)
        legend_ratio.SetTextSize(0.08)
        legend_ratio.AddEntry(ratio, "Ratio", "pe")
        legend_ratio.Draw()

        output_name = f"new_plots/{var}{out_suffix}.pdf"
        canvas.SaveAs(output_name)
        canvas.Close()


def Plot_DiMuonPtCut(df_SingleMuon, df_MinBias, variables, pt_cuts, out_suffix):
    selected_events_single = df_SingleMuon.Count().GetValue()
    selected_pfcands_single = df_SingleMuon.Sum("nPFSelection").GetValue()
    print(f"Number of selected events in SingleMuon file (before pT cut): {selected_events_single}")
    print(f"Number of selected PF candidates in SingleMuon file (before pT cut): {selected_pfcands_single}")

    colours = [ROOT.kViolet - 6, ROOT.kBlue - 4, ROOT.kGreen + 3, ROOT.kOrange + 5, ROOT.kRed + 1]

    for var in variables:
        label = VARIABLES[var]
        bins = BINNING[var]

        df_SingleMuon_var, df_MinBias_var, y_title = ObservablesCalculation(df_SingleMuon, df_MinBias, var)
        h_minbias_ptr = MakeHist(df_MinBias_var, var, label, y_title, bins, f"h_MinBias_{var}_ptscan")
        h_minbias = h_minbias_ptr.GetValue()
        NomaliseHist(h_minbias)

        canvas = ROOT.TCanvas(f"c_ptscan_{var}", "", 800, 700)
        canvas.cd()

        legend = ROOT.TLegend(0.5, 0.5, 0.9, 0.87)
        dummy = ROOT.TObject()
        legend.SetBorderSize(0)
        legend.SetFillStyle(0)
        legend.SetTextSize(0.025)
        legend.SetMargin(0.2)

        histos = []
        plot_max = 0

        for index, pt_cut in enumerate(pt_cuts):
            colour = colours[index % len(colours)]
            df_single_cut = DiMuonPtCut(df_SingleMuon_var, pt_cut)

            selected_events_cut = df_single_cut.Count().GetValue()
            selected_pfcands_cut = df_single_cut.Sum("nPFSelection").GetValue()

            h_single_ptr = MakeHist(
                df_single_cut,
                var,
                label,
                y_title,
                bins,
                f"h_SingleMuon_{var}_{pt_cut}GeV",
            )
            h_single = h_single_ptr.GetValue()
            NomaliseHist(h_single)

            ratio = h_single.Clone(f"ratio_{var}_{pt_cut}GeV")
            ratio.Divide(h_minbias)
            ratio.SetStats(0)
            ratio.SetLineColor(colour)
            ratio.SetLineWidth(2)
            ratio.GetXaxis().SetTitle(label)
            ratio.GetYaxis().SetTitle("DY/MinBias")
            ratio.GetYaxis().SetLabelSize(0.03)
            ratio.GetYaxis().SetTitleSize(0.03)

            canvas.SetLogy()
            if index == 0:
                ratio.Draw("hist")
            else:
                ratio.Draw("hist same")

            max_val = ratio.GetBinContent(ratio.GetMaximumBin())
            if plot_max < max_val:
                plot_max = max_val

            histos.append(ratio)
            legend.AddEntry(ratio, f"p_{{T}} < {pt_cut} GeV", "l")
            legend.AddEntry(dummy, f"{selected_events_cut} selected events", "")
            legend.AddEntry(dummy, f"{selected_pfcands_cut} selected PF candidates", "")

        if histos and plot_max > 0:
            histos[0].SetMaximum(plot_max * 10)

        legend.Draw()
        output_name = f"new_plots/{var}_pTscan{out_suffix}.pdf"
        canvas.SaveAs(output_name)
        canvas.Close()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Combined plotting driver for NanoAOD PF-candidate studies"
    )
    parser.add_argument(
        "--mode",
        choices=["compare", "ptscan", "all"],
        default="all",
        help="Run SingleMuon-vs-ZeroBias compare plots, diMuon pT scan plots, or both",
    )
    parser.add_argument(
        "--maxevents",
        type=int,
        default=None,
        help="If set, process only the first N events from each dataframe",
    )
    parser.add_argument(
        "--no-plot",
        action="store_true",
        help="Run selections and print counts without producing plots",
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
        default=DEFAULT_COMPARE_VARS,
        choices=sorted(VARIABLES.keys()),
        help="Variables to plot in compare mode",
    )
    parser.add_argument(
        "--ptscan-vars",
        nargs="+",
        default=DEFAULT_PTSCAN_VARS,
        choices=sorted(VARIABLES.keys()),
        help="Variables to plot in ptscan mode",
    )
    parser.add_argument(
        "--output-suffix",
        default="",
        help="Optional suffix appended to output plot filenames",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    df_SingleMuon, df_MinBias = MakeDataframes(args.maxevents)
    PrintDatasetCounts(df_SingleMuon, df_MinBias)

    df_SingleMuon = VetoMuons(df_SingleMuon)
    df_SingleMuon = GoodMuons(df_SingleMuon)
    df_SingleMuon = DiMuonSelection(df_SingleMuon)

    df_SingleMuon, df_MinBias = PVSelection(df_SingleMuon, df_MinBias)
    df_SingleMuon = PFCandidateSelection(df_SingleMuon, args.charge)
    df_MinBias = PFCandidateSelection(df_MinBias, args.charge)

    df_SingleMuon = addInvariantMass(df_SingleMuon)
    df_MinBias = addInvariantMass(df_MinBias)

    if args.no_plot:
        print("Selections finished. Plotting disabled by --no-plot.")
        return

    if args.mode in ["compare", "all"]:
        Plot_CompareTriggers(df_SingleMuon, df_MinBias, args.compare_vars, args.output_suffix)

    if args.mode in ["ptscan", "all"]:
        Plot_DiMuonPtCut(df_SingleMuon, df_MinBias, args.ptscan_vars, args.pt_cuts, args.output_suffix)


if __name__ == "__main__":
    main()
