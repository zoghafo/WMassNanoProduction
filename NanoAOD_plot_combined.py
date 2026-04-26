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

FILE_NAMES_MCDYJETS = [
    "/home/z/zoghafoo/CMSSW_10_6_26/src/Configuration/WMassNanoProduction/NanoV9MCPostVFP_PF_DYJetsToMuMu.root",
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
    df_SingleMuon = ROOT.RDataFrame("Events", set(FILE_NAMES_SINGLEMUON))
    df_MinBias = ROOT.RDataFrame("Events", set(FILE_NAMES_ZEROBIAS))
    df_MCDYJets = ROOT.RDataFrame("Events", set(FILE_NAMES_MCDYJETS))

    if maxevents is not None:
        print(f"Processing only the first {maxevents} Events from each file.")
        df_SingleMuon = df_SingleMuon.Range(maxevents)
        df_MinBias = df_MinBias.Range(maxevents)
        df_MCDYJets = df_MCDYJets.Range(maxevents)

    return df_SingleMuon, df_MinBias, df_MCDYJets


def PrintDatasetCounts(df_SingleMuon, df_MinBias, df_MCDYJets):
    total_events_SingleMuon= df_SingleMuon.Count().GetValue()
    total_events_MinBias = df_MinBias.Count().GetValue()
    total_events_MCDYJets = df_MCDYJets.Count().GetValue()
    # print(f"Total number of Events in SingleMuon file: {total_events_SingleMuon}")
    # print(f"Total number of Events in MinBias file: {total_events_MinBias}")
    # print(f"Total number of Events in MCDYJets file: {total_events_MCDYJets}\n")

    total_PFCands_SingleMuon= df_SingleMuon.Sum("nPFCands").GetValue()
    total_PFCands_MinBias = df_MinBias.Sum("nPFCands").GetValue()
    total_PFCands_MCDYJets = df_MCDYJets.Sum("nPFCands").GetValue()
    # print(f"Total number of PFCands in SingleMuon file: {total_PFCands_SingleMuon}")
    # print(f"Total number of PFCands in MinBias file: {total_PFCands_MinBias}")
    # print(f"Total number of PFCands in MCDYJets file: {total_PFCands_MCDYJets}\n")

    return {
        "total_events_SingleMuon": total_events_SingleMuon,
        "total_events_MinBias": total_events_MinBias,
        "total_events_MCDYJets": total_events_MCDYJets,
        "total_PFCands_SingleMuon": total_PFCands_SingleMuon,
        "total_PFCands_MinBias": total_PFCands_MinBias,
        "total_PFCands_MCDYJets": total_PFCands_MCDYJets,
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


def PVSelection(df_SingleMuon, df_MinBias, df_MCDYJets):
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

    df_MCDYJets = df_MCDYJets.Define(
        "PFCands_vertexRefUnique",
        """
        std::set<int> sorted_unique(PFCands_vertexRef.begin(), PFCands_vertexRef.end());
        return ROOT::VecOps::RVec<int>(sorted_unique.begin(), sorted_unique.end());
        """,
    )
    df_MCDYJets = df_MCDYJets.Define(
        "PFCands_vertexRefRandom",
        """
        if (PFCands_vertexRefUnique.size() == 0) return -1;
        return PFCands_vertexRefUnique[0];
        """,
    )

    return df_SingleMuon, df_MinBias, df_MCDYJets


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


def ObservablesCalculation(df_SingleMuon, df_MinBias, df_MCDYJets, var):
    if var in ["PFCands_pt", "PFCands_eta", "PFCands_phi", "PFCands_pvAssocQuality"]:
        return (
            df_SingleMuon.Define(f"PFSelection_{var}", f"Take({var}, PFSelection_idx)"),
            df_MinBias.Define(f"PFSelection_{var}", f"Take({var}, PFSelection_idx)"),
            df_MCDYJets.Define(f"PFSelection_{var}", f"Take({var}, PFSelection_idx)"),
            "Number of PF Candidates (normalised)",
        )

    if var == "PFCands_InvariantMass":
        return (
            df_SingleMuon.Define(f"PFSelection_{var}", "PFCands_InvariantMass"),
            df_MinBias.Define(f"PFSelection_{var}", "PFCands_InvariantMass"),
            df_MCDYJets.Define(f"PFSelection_{var}", "PFCands_InvariantMass"),
            "Number of Events (normalised)",
        )

    if var == "nPFCands":
        return (
            df_SingleMuon.Define(f"PFSelection_{var}", "PFSelection_idx.size()"),
            df_MinBias.Define(f"PFSelection_{var}", "PFSelection_idx.size()"),
            df_MCDYJets.Define(f"PFSelection_{var}", "PFSelection_idx.size()"),
            "Number of Events (normalised)",

        )

    if var == "PFCands_Ht":
        expr = "ROOT::VecOps::Sum(Take(PFCands_pt, PFSelection_idx))"
        return (
            df_SingleMuon.Define(f"PFSelection_{var}", expr),
            df_MinBias.Define(f"PFSelection_{var}", expr),
            df_MCDYJets.Define(f"PFSelection_{var}", expr),
            "Number of Events (normalised)",
        )

    if var == "PFCands_Pt2sum":
        expr = "ROOT::VecOps::Sum(Take(PFCands_pt * PFCands_pt, PFSelection_idx))"
        return (
            df_SingleMuon.Define(f"PFSelection_{var}", expr),
            df_MinBias.Define(f"PFSelection_{var}", expr),
            df_MCDYJets.Define(f"PFSelection_{var}", expr),
            "Number of Events (normalised)",
        )

    if var == "PFCands_Psum":
        expr = "ROOT::VecOps::Sum(Take(PFCands_p, PFSelection_idx))"
        return (
            df_SingleMuon.Define(f"PFSelection_{var}", expr),
            df_MinBias.Define(f"PFSelection_{var}", expr),
            df_MCDYJets.Define(f"PFSelection_{var}", expr),
            "Number of Events (normalised)",
        )

    if var == "PFCands_P2sum":
        expr = "ROOT::VecOps::Sum(Take(PFCands_p * PFCands_p, PFSelection_idx))"
        return (
            df_SingleMuon.Define(f"PFSelection_{var}", expr),
            df_MinBias.Define(f"PFSelection_{var}", expr),
            df_MCDYJets.Define(f"PFSelection_{var}", expr),
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


# ---------------------- PLOTS ----------------------

def Plot_CompareTriggers(df_SingleMuon, df_MinBias, df_MCDYJets, variables, total_events, out_suffix):

    total_events_SingleMuon = total_events["total_events_SingleMuon"]
    total_events_MinBias = total_events["total_events_MinBias"]
    total_events_MCDYJets = total_events["total_events_MCDYJets"]
    total_PFCands_SingleMuon = total_events["total_PFCands_SingleMuon"]
    total_PFCands_MinBias = total_events["total_PFCands_MinBias"]
    total_PFCands_MCDYJets = total_events["total_PFCands_MCDYJets"]

    selected_events_SingleMuon= df_SingleMuon.Count().GetValue()
    selected_events_MinBias = df_MinBias.Count().GetValue()
    selected_events_MCDYJets = df_MCDYJets.Count().GetValue()
    selected_PFCands_SingleMuon= df_SingleMuon.Sum("nPFSelection").GetValue()
    selected_PFCands_MinBias = df_MinBias.Sum("nPFSelection").GetValue()
    selected_PFCands_MCDYJets = df_MCDYJets.Sum("nPFSelection").GetValue()

    print(f"Number of selected Events in SingleMuon file: {selected_events_SingleMuon}")
    print(f"Number of selected Events in MinBias file: {selected_events_MinBias}")
    print(f"Number of selected Events in MCDYJets file: {selected_events_MCDYJets}\n")
    print(f"Number of selected PFCands in SingleMuon file: {selected_PFCands_SingleMuon}")
    print(f"Number of selected PFCands in MinBias file: {selected_PFCands_MinBias}")
    print(f"Number of selected PFCands in MCDYJets file: {selected_PFCands_MCDYJets}\n")

    for var in variables:
        label = VARIABLES[var]
        bins = BINNING[var]

        df_SingleMuon_var, df_MinBias_var, df_MCDYJets_var, y_title = ObservablesCalculation(df_SingleMuon, df_MinBias, df_MCDYJets, var)
        h_SingleMuon_ptr = MakeHist(df_SingleMuon_var, var, label, y_title, bins, f"h_SingleMuon_{var}")
        h_MinBias_ptr = MakeHist(df_MinBias_var, var, label, y_title, bins, f"h_MinBias_{var}")
        h_MCDYJets_ptr = MakeHist(df_MCDYJets_var, var, label, y_title, bins, f"h_MCDYJets_{var}")

        h_SingleMuon= h_SingleMuon_ptr.GetValue()
        h_MinBias = h_MinBias_ptr.GetValue()
        h_MCDYJets = h_MCDYJets_ptr.GetValue()
        NomaliseHist(h_SingleMuon)
        NomaliseHist(h_MinBias)
        NomaliseHist(h_MCDYJets)

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

        h_MCDYJets.SetLineColor(ROOT.kGray + 2)
        h_MCDYJets.SetLineWidth(2)
        h_MCDYJets.SetLineStyle(2)
        h_MCDYJets.Draw("hist same")

        h_SingleMuon.SetMaximum(max(h_SingleMuon.GetMaximum(), h_MinBias.GetMaximum(), h_MCDYJets.GetMaximum()) * 1.3)

        legend = ROOT.TLegend(0.75, 0.4, 0.98, 0.87)
        dummy = ROOT.TObject()
        legend.SetBorderSize(0)
        legend.SetFillStyle(0)
        legend.SetTextSize(0.04)
        legend.SetMargin(0.2)
        legend.AddEntry(dummy, "#bf{Data}", "")
        legend.AddEntry(h_SingleMuon, "DY", "l")
        legend.AddEntry(dummy, f"{(selected_events_SingleMuon/total_events_SingleMuon)*100:.2f}% selected Events", "")
        legend.AddEntry(dummy, f"{(selected_PFCands_SingleMuon/total_PFCands_SingleMuon)*100:.2f}% selected PFCands", "")
        legend.AddEntry(h_MinBias, "ZeroBias", "l")
        legend.AddEntry(dummy, f"{(selected_events_MinBias/total_events_MinBias)*100:.2f}% selected Events", "")
        legend.AddEntry(dummy, f"{(selected_PFCands_MinBias/total_PFCands_MinBias)*100:.2f}% selected PFCands", "")
        legend.AddEntry(dummy, "#bf{MC}", "")
        legend.AddEntry(h_MCDYJets, "DY", "l")
        legend.AddEntry(dummy, f"{(selected_events_MCDYJets/total_events_MCDYJets)*100:.2f}% selected Events", "")
        legend.AddEntry(dummy, f"{(selected_PFCands_MCDYJets/total_PFCands_MCDYJets)*100:.2f}% selected PFCands", "")
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
        ratio_MCDYJets.Divide(h_MinBias)
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

        legend_ratio = ROOT.TLegend(0.62, 0.4, 0.675, 0.55)
        legend_ratio.SetBorderSize(0)
        # legend_ratio.SetFillStyle(0)
        legend_ratio.SetTextSize(0.08)
        legend_ratio.AddEntry(ratio_SingleMuon, "Data", "pe")
        legend_ratio.AddEntry(ratio_MCDYJets, "MC", "pe")
        legend_ratio.Draw()

        output_name = f"new_plots/{var}{out_suffix}.pdf"
        canvas.SaveAs(output_name)
        canvas.Close()


def Plot_DiMuonPtCut(df_SingleMuon, df_MinBias, df_MCDYJets, variables, pt_cuts, total_events, out_suffix):
    total_events_SingleMuon = total_events["total_events_SingleMuon"]
    total_events_MinBias = total_events["total_events_MinBias"]
    total_events_MCDYJets = total_events["total_events_MCDYJets"]
    total_PFCands_SingleMuon = total_events["total_PFCands_SingleMuon"]
    total_PFCands_MinBias = total_events["total_PFCands_MinBias"]
    total_PFCands_MCDYJets = total_events["total_PFCands_MCDYJets"]

    selected_events_MinBias = df_MinBias.Count().GetValue()
    selected_PFCands_MinBias = df_MinBias.Sum("nPFSelection").GetValue()

    # print(f"Number of selected Events in MinBias file: {selected_events_MinBias}")
    # print(f"Number of selected PFCands in MinBias file: {selected_PFCands_MinBias}")

    colours = [ROOT.kViolet - 6, ROOT.kBlue - 4, ROOT.kGreen + 3, ROOT.kOrange + 5, ROOT.kRed + 1]

    for var in variables:
        label = VARIABLES[var]
        bins = BINNING[var]

        df_SingleMuon_var, df_MinBias_var, df_MCDYJets_var, y_title = ObservablesCalculation(df_SingleMuon, df_MinBias, df_MCDYJets, var)
        h_MinBias_ptr = MakeHist(df_MinBias_var, var, label, y_title, bins, f"h_MinBias_{var}_ptscan")
        h_MinBias = h_MinBias_ptr.GetValue()
        NomaliseHist(h_MinBias)

        canvas = ROOT.TCanvas(f"c_ptscan_{var}", "", 800, 700)
        canvas.cd()
        canvas.SetRightMargin(0.25)
        canvas.SetLogy()

        legend_col0 = ROOT.TLegend(0.68, 0.84, 0.8, 0.89)
        legend_col1 = ROOT.TLegend(0.75, 0.04, 0.98, 0.96)
        dummy = ROOT.TObject()
        for legend in (legend_col0, legend_col1):
            legend.SetBorderSize(0)
            legend.SetFillStyle(0)
            legend.SetTextSize(0.02)
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

            colour = colours[index % len(colours)]

            df_SingleMuon_cut = DiMuonPtCut(df_SingleMuon_var, pt_cut)
            df_MCDYJets_cut = DiMuonPtCut(df_MCDYJets_var, pt_cut)

            selected_events_SingleMuon= df_SingleMuon_cut.Count().GetValue()
            selected_events_MCDYJets= df_MCDYJets_cut.Count().GetValue()
            selected_PFCands_SingleMuon= df_SingleMuon_cut.Sum("nPFSelection").GetValue()
            selected_PFCands_MCDYJets= df_MCDYJets_cut.Sum("nPFSelection").GetValue()

            # print(f"Number of selected Events in SingleMuon file: {selected_events_SingleMuon}")
            # print(f"Number of selected Events in MCDYJets file: {selected_events_MCDYJets}")
            # print(f"Number of selected PFCands in SingleMuon file: {selected_PFCands_SingleMuon}")
            # print(f"Number of selected PFCands in MCDYJets file: {selected_PFCands_MCDYJets}")

            h_SingleMuon_ptr = MakeHist(df_SingleMuon_cut, var, label, y_title, bins, f"h_SingleMuon_{var}_{pt_cut}GeV")
            h_MCDYJets_ptr = MakeHist(df_MCDYJets_cut, var, label, y_title, bins, f"h_MCDYJets_{var}_{pt_cut}GeV")

            h_SingleMuon= h_SingleMuon_ptr.GetValue()
            NomaliseHist(h_SingleMuon)

            h_MCDYJets= h_MCDYJets_ptr.GetValue()
            NomaliseHist(h_MCDYJets)

            ratio_SingleMuon = h_SingleMuon.Clone(f"ratio_SingleMuon_{var}_{pt_cut}GeV")
            ratio_SingleMuon.Divide(h_MinBias)
            ratio_SingleMuon.SetStats(0)
            ratio_SingleMuon.SetLineColor(colour)
            ratio_SingleMuon.SetLineWidth(2)
            ratio_SingleMuon.GetXaxis().SetTitle(label)
            ratio_SingleMuon.GetYaxis().SetTitle("DY/MinBias")
            ratio_SingleMuon.GetYaxis().SetLabelSize(0.03)
            ratio_SingleMuon.GetYaxis().SetTitleSize(0.03)

            ratio_MCDYJets = h_MCDYJets.Clone(f"ratio_MCDYJets_{var}_{pt_cut}GeV")
            ratio_MCDYJets.Divide(h_MinBias)
            ratio_MCDYJets.SetStats(0)
            ratio_MCDYJets.SetLineColor(colour)
            ratio_MCDYJets.SetLineWidth(2)
            ratio_MCDYJets.SetLineStyle(2)
            ratio_MCDYJets.GetXaxis().SetTitle(label)
            ratio_MCDYJets.GetYaxis().SetTitle("DY/MinBias")
            ratio_MCDYJets.GetYaxis().SetLabelSize(0.03)
            ratio_MCDYJets.GetYaxis().SetTitleSize(0.03)

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
            legend_col1.AddEntry(dummy, f"{(selected_events_SingleMuon/total_events_SingleMuon) * 100:.2f}% selected Events", "")
            legend_col1.AddEntry(dummy, f"{(selected_PFCands_SingleMuon/total_PFCands_SingleMuon) * 100:.2f}% selected PFCands", "")
            legend_col1.AddEntry(dummy, "#bf{MC}", "")
            legend_col1.AddEntry(dummy, f"{(selected_events_MCDYJets/total_events_MCDYJets) * 100:.2f}% selected Events", "")
            legend_col1.AddEntry(dummy, f"{(selected_PFCands_MCDYJets/total_PFCands_MCDYJets) * 100:.2f}% selected PFCands", "")
            legend_col1.AddEntry(dummy, "#bf{ZeroBias}", "")
            legend_col1.AddEntry(dummy, f"{(selected_events_MinBias/total_events_MinBias) * 100:.2f}% selected Events", "")
            legend_col1.AddEntry(dummy, f"{(selected_PFCands_MinBias/total_PFCands_MinBias) * 100:.2f}% selected PFCands", "")

        if histos and plot_max > 0:
            histos[0].SetMaximum(plot_max * 10)

    
        legend_col0.AddEntry(legend_DataStyle, "Data", "l")
        legend_col0.AddEntry(legend_MCStyle, "MC", "l")
        legend_col0.Draw()
        legend_col1.Draw()

        output_name = f"new_plots/{var}_pTscan{out_suffix}.pdf"
        canvas.SaveAs(output_name)
        canvas.Close()

def QuantilePerObservable(df_SingleMuon, df_MinBias, df_MCDYJets, variables, total_events, out_suffix):
    total_events_SingleMuon = total_events["total_events_SingleMuon"]
    total_events_MinBias = total_events["total_events_MinBias"]
    total_events_MCDYJets = total_events["total_events_MCDYJets"]
    total_PFCands_SingleMuon = total_events["total_PFCands_SingleMuon"]
    total_PFCands_MinBias = total_events["total_PFCands_MinBias"]
    total_PFCands_MCDYJets = total_events["total_PFCands_MCDYJets"]

    selected_events_SingleMuon = df_SingleMuon.Count().GetValue()
    selected_events_MinBias = df_MinBias.Count().GetValue()
    selected_events_MCDYJets = df_MCDYJets.Count().GetValue()

    selected_PFCands_SingleMuon = df_SingleMuon.Sum("nPFSelection").GetValue()
    selected_PFCands_MinBias = df_MinBias.Sum("nPFSelection").GetValue()
    selected_PFCands_MCDYJets = df_MCDYJets.Sum("nPFSelection").GetValue()

    for var in variables:
        if var in ["PFCands_pt", "PFCands_eta", "PFCands_phi", "PFCands_pvAssocQuality"]:
            continue

        label = VARIABLES[var]
        bins = BINNING[var]

        df_SingleMuon_var, df_MinBias_var, df_MCDYJets_var, y_title = ObservablesCalculation(df_SingleMuon, df_MinBias, df_MCDYJets, var)

        h_tmp_ptr = MakeHist(df_MinBias_var, var, label, y_title, bins, f"h_MinBias_{var}_quantile_tmp")
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


        df_MinBias_q = df_MinBias_var.Define(f"{var}_invQ", f"1.0 - {var}InvQMap::eval(PFSelection_{var})")
        df_SingleMuon_q = df_SingleMuon_var.Define(f"{var}_invQ", f"1.0 - {var}InvQMap::eval(PFSelection_{var})")
        df_MCDYJets_q = df_MCDYJets_var.Define(f"{var}_invQ", f"1.0 - {var}InvQMap::eval(PFSelection_{var})")

        plot_column = f"{var}_invQ"
        plot_xlabel = f"1 - F_{{MB}}({label})"

        h_MinBias_ptr = df_MinBias_q.Histo1D(
            (f"h_MinBias_{var}_quantile", f"; {plot_xlabel}; {y_title}", 10, 0, 1),
            plot_column,
        )
        h_SingleMuon_ptr = df_SingleMuon_q.Histo1D(
            (f"h_SingleMuon_{var}_quantile", f"; {plot_xlabel}; {y_title}", 10, 0, 1),
            plot_column,
        )
        h_MCDYJets_ptr = df_MCDYJets_q.Histo1D(
            (f"h_MCDYJets_{var}_quantile", f"; {plot_xlabel}; {y_title}", 10, 0, 1),
            plot_column,
        )

        h_MinBias = h_MinBias_ptr.GetValue()
        h_SingleMuon = h_SingleMuon_ptr.GetValue()
        h_MCDYJets = h_MCDYJets_ptr.GetValue()

        NomaliseHist(h_MinBias)
        NomaliseHist(h_SingleMuon)
        NomaliseHist(h_MCDYJets)

        canvas = ROOT.TCanvas(f"c_quantile_{var}")
        canvas.cd()
        canvas.SetBottomMargin(0.13)
        canvas.SetLogy()


        ratio_SingleMuon = h_SingleMuon.Clone(f"ratio_quantile_{var}")
        ratio_SingleMuon.Divide(h_MinBias)
        ratio_SingleMuon.SetLineColor(ROOT.kViolet - 6)
        ratio_SingleMuon.SetLineWidth(2)
        ratio_SingleMuon.GetXaxis().SetTitle("")
        ratio_SingleMuon.GetXaxis().SetTitle(plot_xlabel)
        ratio_SingleMuon.GetYaxis().SetTitle("DY/ZeroBias")
        ratio_SingleMuon.GetYaxis().SetTitle("Number of Events (normalised)")
        ratio_SingleMuon.GetXaxis().SetTitleSize(0.035)
        ratio_SingleMuon.GetXaxis().SetTitleOffset(1.3)
        ratio_SingleMuon.GetXaxis().SetLabelSize(0.035)
        ratio_SingleMuon.GetXaxis().SetTickLength(0.03)
        ratio_SingleMuon.GetYaxis().SetTitleSize(0.035)
        ratio_SingleMuon.GetYaxis().SetLabelSize(0.035)
        ratio_SingleMuon.Draw("hist")

        ratio_MCDYJets = h_MCDYJets.Clone(f"ratio_quantile_mc_{var}")
        ratio_MCDYJets.Divide(h_MinBias)
        ratio_MCDYJets.SetLineColor(ROOT.kViolet - 6)
        ratio_MCDYJets.SetLineWidth(2)
        ratio_MCDYJets.SetLineStyle(2)
        ratio_MCDYJets.Draw("hist same")

        ratio_SingleMuon.SetMaximum(max(ratio_SingleMuon.GetMaximum(), ratio_MCDYJets.GetMaximum()) * 10)

        # legend = ROOT.TLegend(0.68, 0.65, 1, 0.89)
        # dummy = ROOT.TObject()
        # legend.SetBorderSize(0)
        # legend.SetFillStyle(0)
        # legend.SetTextSize(0.02)
        # legend.SetMargin(0.2)

        # legend.AddEntry(dummy, "ZeroBias", "")
        # legend.AddEntry(dummy, f"{(selected_events_MinBias/total_events_MinBias)*100:.2f}% selected Events", "")
        # legend.AddEntry(dummy, f"{(selected_PFCands_MinBias/total_PFCands_MinBias)*100:.2f}% selected PFCands", "")

        # legend.AddEntry(ratio_SingleMuon, "DY", "l")
        # legend.AddEntry(dummy, f"{(selected_events_SingleMuon/total_events_SingleMuon)*100:.2f}% selected Events", "")
        # legend.AddEntry(dummy, f"{(selected_PFCands_SingleMuon/total_PFCands_SingleMuon)*100:.2f}% selected PFCands", "")

        # legend.AddEntry(ratio_MCDYJets, "MC", "l")
        # legend.AddEntry(dummy, f"{(selected_events_MCDYJets/total_events_MCDYJets)*100:.2f}% selected Events", "")
        # legend.AddEntry(dummy, f"{(selected_PFCands_MCDYJets/total_PFCands_MCDYJets)*100:.2f}% selected PFCands", "")
        # legend.Draw()

        legend = ROOT.TLegend(0.7, 0.55, 0.84, 0.89)
        dummy = ROOT.TObject()
        legend.SetBorderSize(0)
        legend.SetFillStyle(0)
        legend.SetTextSize(0.02)
        legend.SetMargin(0.2)
        legend.AddEntry(ratio_SingleMuon, "#bf{Data}", "l")
        legend.AddEntry(dummy, "DY", "")
        legend.AddEntry(dummy, f"{(selected_events_SingleMuon/total_events_SingleMuon)*100:.2f}% selected Events", "")
        legend.AddEntry(dummy, f"{(selected_PFCands_SingleMuon/total_PFCands_SingleMuon)*100:.2f}% selected PFCands", "")
        legend.AddEntry(dummy, "ZeroBias", "")
        legend.AddEntry(dummy, f"{(selected_events_MinBias/total_events_MinBias)*100:.2f}% selected Events", "")
        legend.AddEntry(dummy, f"{(selected_PFCands_MinBias/total_PFCands_MinBias)*100:.2f}% selected PFCands", "")
        legend.AddEntry(ratio_MCDYJets, "#bf{MC}", "l")
        legend.AddEntry(dummy, "DY", "")
        legend.AddEntry(dummy, f"{(selected_events_MCDYJets/total_events_MCDYJets)*100:.2f}% selected Events", "")
        legend.AddEntry(dummy, f"{(selected_PFCands_MCDYJets/total_PFCands_MCDYJets)*100:.2f}% selected PFCands", "")
        legend.Draw()

        output_name = f"new_plots/{var}_Quantile{out_suffix}.pdf"
        canvas.SaveAs(output_name)
        canvas.Close()


def Quantile_DiMuonPtCut(df_SingleMuon, df_MinBias, df_MCDYJets, variables, pt_cuts, total_events, out_suffix):
    total_events_SingleMuon = total_events["total_events_SingleMuon"]
    total_events_MinBias = total_events["total_events_MinBias"]
    total_events_MCDYJets = total_events["total_events_MCDYJets"]
    total_PFCands_SingleMuon = total_events["total_PFCands_SingleMuon"]
    total_PFCands_MinBias = total_events["total_PFCands_MinBias"]
    total_PFCands_MCDYJets = total_events["total_PFCands_MCDYJets"]

    selected_events_MinBias = df_MinBias.Count().GetValue()
    selected_PFCands_MinBias = df_MinBias.Sum("nPFSelection").GetValue()

    colours = [ROOT.kViolet - 6, ROOT.kBlue - 4, ROOT.kGreen + 3, ROOT.kOrange + 5, ROOT.kRed + 1]

    for var in variables:
        if var in ["PFCands_pt", "PFCands_eta", "PFCands_phi", "PFCands_pvAssocQuality"]:
            continue

        label = VARIABLES[var]
        bins = BINNING[var]

        df_SingleMuon_var, df_MinBias_var, df_MCDYJets_var, y_title = ObservablesCalculation(df_SingleMuon, df_MinBias, df_MCDYJets, var)

        h_tmp_ptr = MakeHist(df_MinBias_var, var, label, y_title, bins, f"h_MinBias_{var}_quantile_ptscan_tmp")
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

        df_MinBias_q = df_MinBias_var.Define(f"{var}_invQ", f"1.0 - {var}InvQMapPtScan::eval(PFSelection_{var})")
        df_SingleMuon_q = df_SingleMuon_var.Define(f"{var}_invQ", f"1.0 - {var}InvQMapPtScan::eval(PFSelection_{var})")
        df_MCDYJets_q = df_MCDYJets_var.Define(f"{var}_invQ", f"1.0 - {var}InvQMapPtScan::eval(PFSelection_{var})")

        plot_column = f"{var}_invQ"
        plot_xlabel = f"1 - F_{{MB}}({label})"

        h_MinBias_ptr = df_MinBias_q.Histo1D(
            (f"h_MinBias_{var}_quantile_ptscan", f"; {plot_xlabel}; Number of Events (normalised)", 10, 0, 1),
            plot_column,
        )
        h_MinBias = h_MinBias_ptr.GetValue()
        NomaliseHist(h_MinBias)

        canvas = ROOT.TCanvas(f"c_quantile_ptscan_{var}", "", 800, 700)
        canvas.cd()
        canvas.SetBottomMargin(0.13)
        canvas.SetRightMargin(0.25)
        canvas.SetLogy()

        legend_col0 = ROOT.TLegend(0.68, 0.84, 0.8, 0.89)
        legend_col1 = ROOT.TLegend(0.75, 0.04, 0.98, 0.96)
        dummy = ROOT.TObject()
        for legend in (legend_col0, legend_col1):
            legend.SetBorderSize(0)
            legend.SetFillStyle(0)
            legend.SetTextSize(0.02)
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
            colour = colours[index % len(colours)]

            df_SingleMuon_cut = DiMuonPtCut(df_SingleMuon_q, pt_cut)
            df_MCDYJets_cut = DiMuonPtCut(df_MCDYJets_q, pt_cut)

            selected_events_SingleMuon = df_SingleMuon_cut.Count().GetValue()
            selected_events_MCDYJets = df_MCDYJets_cut.Count().GetValue()
            selected_PFCands_SingleMuon = df_SingleMuon_cut.Sum("nPFSelection").GetValue()
            selected_PFCands_MCDYJets = df_MCDYJets_cut.Sum("nPFSelection").GetValue()

            h_SingleMuon_ptr = df_SingleMuon_cut.Histo1D(
                (f"h_SingleMuon_{var}_quantile_{pt_cut}GeV", f"; {plot_xlabel}; Number of Events (normalised)", 10, 0, 1),
                plot_column,
            )
            h_MCDYJets_ptr = df_MCDYJets_cut.Histo1D(
                (f"h_MCDYJets_{var}_quantile_{pt_cut}GeV", f"; {plot_xlabel}; Number of Events (normalised)", 10, 0, 1),
                plot_column,
            )

            h_SingleMuon = h_SingleMuon_ptr.GetValue()
            h_MCDYJets = h_MCDYJets_ptr.GetValue()
            NomaliseHist(h_SingleMuon)
            NomaliseHist(h_MCDYJets)

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
            ratio_MCDYJets.Divide(h_MinBias)
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
            legend_col1.AddEntry(dummy, f"{(selected_events_SingleMuon/total_events_SingleMuon) * 100:.2f}% selected Events", "")
            legend_col1.AddEntry(dummy, f"{(selected_PFCands_SingleMuon/total_PFCands_SingleMuon) * 100:.2f}% selected PFCands", "")
            legend_col1.AddEntry(dummy, "#bf{MC}", "")
            legend_col1.AddEntry(dummy, f"{(selected_events_MCDYJets/total_events_MCDYJets) * 100:.2f}% selected Events", "")
            legend_col1.AddEntry(dummy, f"{(selected_PFCands_MCDYJets/total_PFCands_MCDYJets) * 100:.2f}% selected PFCands", "")
            legend_col1.AddEntry(dummy, "#bf{ZeroBias}", "")
            legend_col1.AddEntry(dummy, f"{(selected_events_MinBias/total_events_MinBias) * 100:.2f}% selected Events", "")
            legend_col1.AddEntry(dummy, f"{(selected_PFCands_MinBias/total_PFCands_MinBias) * 100:.2f}% selected PFCands", "")

        if histos and plot_max > 0:
            histos[0].SetMaximum(plot_max * 30)

        legend_col0.AddEntry(legend_Data, "Data", "l")
        legend_col0.AddEntry(legend_MC, "MC", "l")
        legend_col0.Draw()
        legend_col1.Draw()

        output_name = f"new_plots/{var}_QuantilePtScan{out_suffix}.pdf"
        canvas.SaveAs(output_name)
        canvas.Close()


def Quantile_AllTogether(df_SingleMuon, df_MinBias, df_MCDYJets, variables, total_events, out_suffix):
    total_events_SingleMuon = total_events["total_events_SingleMuon"]
    total_events_MinBias = total_events["total_events_MinBias"]
    total_events_MCDYJets = total_events["total_events_MCDYJets"]
    total_PFCands_SingleMuon = total_events["total_PFCands_SingleMuon"]
    total_PFCands_MinBias = total_events["total_PFCands_MinBias"]
    total_PFCands_MCDYJets = total_events["total_PFCands_MCDYJets"]

    selected_events_SingleMuon = df_SingleMuon.Count().GetValue()
    selected_events_MinBias = df_MinBias.Count().GetValue()
    selected_events_MCDYJets = df_MCDYJets.Count().GetValue()

    selected_PFCands_SingleMuon = df_SingleMuon.Sum("nPFSelection").GetValue()
    selected_PFCands_MinBias = df_MinBias.Sum("nPFSelection").GetValue()
    selected_PFCands_MCDYJets = df_MCDYJets.Sum("nPFSelection").GetValue()

    colours = [ROOT.kViolet - 6, ROOT.kBlue - 4, ROOT.kGreen + 3, ROOT.kOrange + 5, ROOT.kRed + 1, ROOT.kCyan + 2]
    ratio_data_hists = []
    ratio_mc_hists = []

    for var in variables:
        if var in ["PFCands_pt", "PFCands_eta", "PFCands_phi", "PFCands_pvAssocQuality"]:
            continue

        label = VARIABLES[var]
        bins = BINNING[var]

        df_SingleMuon_var, df_MinBias_var, df_MCDYJets_var, y_title = ObservablesCalculation(df_SingleMuon, df_MinBias, df_MCDYJets, var)

        h_tmp_ptr = MakeHist(df_MinBias_var, var, label, y_title, bins, f"h_MinBias_{var}_quantile_all_tmp")
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

        df_MinBias_q = df_MinBias_var.Define(f"{var}_invQ_all", f"1.0 - {var}InvQMapAllTogether::eval(PFSelection_{var})")
        df_SingleMuon_q = df_SingleMuon_var.Define(f"{var}_invQ_all", f"1.0 - {var}InvQMapAllTogether::eval(PFSelection_{var})")
        df_MCDYJets_q = df_MCDYJets_var.Define(f"{var}_invQ_all", f"1.0 - {var}InvQMapAllTogether::eval(PFSelection_{var})")

        plot_column = f"{var}_invQ_all"
        plot_xlabel = "1 - F_{MB}(x)"

        h_MinBias_ptr = df_MinBias_q.Histo1D(
            (f"h_MinBias_{var}_quantile_all", f"; {plot_xlabel}; {y_title}", 10, 0, 1),
            plot_column,
        )
        h_SingleMuon_ptr = df_SingleMuon_q.Histo1D(
            (f"h_SingleMuon_{var}_quantile_all", f"; {plot_xlabel}; {y_title}", 10, 0, 1),
            plot_column,
        )
        h_MCDYJets_ptr = df_MCDYJets_q.Histo1D(
            (f"h_MCDYJets_{var}_quantile_all", f"; {plot_xlabel}; {y_title}", 10, 0, 1),
            plot_column,
        )

        h_MinBias = h_MinBias_ptr.GetValue()
        h_SingleMuon = h_SingleMuon_ptr.GetValue()
        h_MCDYJets = h_MCDYJets_ptr.GetValue()

        NomaliseHist(h_MinBias)
        NomaliseHist(h_SingleMuon)
        NomaliseHist(h_MCDYJets)

        colour = colours[len(ratio_data_hists) % len(colours)]

        ratio_SingleMuon = h_SingleMuon.Clone(f"ratio_quantile_all_data_{var}")
        ratio_SingleMuon.Divide(h_MinBias)
        ratio_SingleMuon.SetLineColor(colour)
        ratio_SingleMuon.SetLineWidth(2)

        ratio_MCDYJets = h_MCDYJets.Clone(f"ratio_quantile_all_mc_{var}")
        ratio_MCDYJets.Divide(h_MinBias)
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
    # canvas.SetRightMargin(0.25)
    canvas.SetLogy()

    first_ratio = ratio_data_hists[0][2]
    max_val = max(max(r.GetMaximum(), m.GetMaximum()) for (_, _, r), (_, _, m) in zip(ratio_data_hists, ratio_mc_hists))

    first_ratio.GetXaxis().SetTitle("1 - F_{MB}(x)")
    first_ratio.GetYaxis().SetTitle("Number of Events (normalised)")
    first_ratio.GetXaxis().SetTitleSize(0.035)
    first_ratio.GetXaxis().SetTitleOffset(1.3)
    first_ratio.GetXaxis().SetLabelSize(0.035)
    first_ratio.GetXaxis().SetTickLength(0.03)
    first_ratio.GetYaxis().SetTitleSize(0.035)
    first_ratio.GetYaxis().SetLabelSize(0.035)
    first_ratio.SetMaximum(max_val * 2)
    first_ratio.Draw("hist")

    ratio_mc_hists[0][2].Draw("hist same")

    for _, _, ratio in ratio_data_hists[1:]:
        ratio.Draw("hist same")
    for _, _, ratio in ratio_mc_hists[1:]:
        ratio.Draw("hist same")

    legend_col0 = ROOT.TLegend(0.5, 0.58, 0.7, 0.89)
    legend_col1 = ROOT.TLegend(0.74, 0.63, 0.96, 0.9)
    dummy = ROOT.TObject()
    for legend in (legend_col0, legend_col1):
        legend.SetBorderSize(0)
        legend.SetFillStyle(0)
        legend.SetTextSize(0.02)
        legend.SetMargin(0.2)
    
    legend_Data = ROOT.TLine(0.0, 0.0, 0.5, 0.0)
    legend_Data.SetLineColor(ROOT.kBlack)
    legend_Data.SetLineWidth(2)
    legend_Data.SetLineStyle(1)

    legend_MC = ROOT.TLine(0.0, 0.0, 0.5, 0.0)
    legend_MC.SetLineColor(ROOT.kBlack)
    legend_MC.SetLineWidth(2)
    legend_MC.SetLineStyle(2)

    legend_col0.AddEntry(legend_Data, "Data", "l")
    legend_col0.AddEntry(dummy, "#bf{DY}", "")
    legend_col0.AddEntry(dummy, f"{(selected_events_SingleMuon/total_events_SingleMuon) * 100:.2f}% selected Events", "")
    legend_col0.AddEntry(dummy, f"{(selected_PFCands_SingleMuon/total_PFCands_SingleMuon) * 100:.2f}% selected PFCands", "")

    legend_col0.AddEntry(dummy, "#bf{ZeroBias}", "")
    legend_col0.AddEntry(dummy, f"{(selected_events_MinBias/total_events_MinBias) * 100:.2f}% selected Events", "")
    legend_col0.AddEntry(dummy, f"{(selected_PFCands_MinBias/total_PFCands_MinBias) * 100:.2f}% selected PFCands", "")

    legend_col0.AddEntry(legend_MC, "MC", "l")
    legend_col0.AddEntry(dummy, "#bf{DY}", "")
    legend_col0.AddEntry(dummy, f"{(selected_events_MCDYJets/total_events_MCDYJets) * 100:.2f}% selected Events", "")
    legend_col0.AddEntry(dummy, f"{(selected_PFCands_MCDYJets/total_PFCands_MCDYJets) * 100:.2f}% selected PFCands", "")
    

    for (var, label, ratio_data), (_, _, ratio_mc) in zip(ratio_data_hists, ratio_mc_hists):
        legend_col1.AddEntry(ratio_data, f"{label}", "lf")
        # legend_col1.AddEntry(ratio_mc, f"{label} (MC)", "l")

    legend_col0.Draw()
    legend_col1.Draw()

    output_name = f"new_plots/AllVariables_QuantileAllTogether{out_suffix}.pdf"
    canvas.SaveAs(output_name)
    canvas.Close()


def Quantile_AllTogether_DiMuonPtCut(df_SingleMuon, df_MinBias, df_MCDYJets, variables, pt_cuts, total_events, out_suffix):
    total_events_SingleMuon = total_events["total_events_SingleMuon"]
    total_events_MinBias = total_events["total_events_MinBias"]
    total_events_MCDYJets = total_events["total_events_MCDYJets"]
    total_PFCands_SingleMuon = total_events["total_PFCands_SingleMuon"]
    total_PFCands_MinBias = total_events["total_PFCands_MinBias"]
    total_PFCands_MCDYJets = total_events["total_PFCands_MCDYJets"]

    selected_events_MinBias = df_MinBias.Count().GetValue()
    selected_PFCands_MinBias = df_MinBias.Sum("nPFSelection").GetValue()

    colours = [ROOT.kViolet - 6, ROOT.kBlue - 4, ROOT.kGreen + 3, ROOT.kOrange + 5, ROOT.kRed + 1, ROOT.kCyan + 2]

    for pt_index, pt_cut in enumerate(pt_cuts):
        selected_events_SingleMuon = DiMuonPtCut(df_SingleMuon, pt_cut).Count().GetValue()
        selected_events_MCDYJets = DiMuonPtCut(df_MCDYJets, pt_cut).Count().GetValue()
        selected_PFCands_SingleMuon = DiMuonPtCut(df_SingleMuon, pt_cut).Sum("nPFSelection").GetValue()
        selected_PFCands_MCDYJets = DiMuonPtCut(df_MCDYJets, pt_cut).Sum("nPFSelection").GetValue()

        ratio_data_hists = []
        ratio_mc_hists = []

        for var in variables:
            if var in ["PFCands_pt", "PFCands_eta", "PFCands_phi", "PFCands_pvAssocQuality"]:
                continue

            label = VARIABLES[var]
            bins = BINNING[var]

            df_SingleMuon_var, df_MinBias_var, df_MCDYJets_var, y_title = ObservablesCalculation(df_SingleMuon, df_MinBias, df_MCDYJets, var)

            h_tmp_ptr = MakeHist(df_MinBias_var, var, label, y_title, bins, f"h_MinBias_{var}_quantile_all_ptscan_tmp")
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

            df_MinBias_q = df_MinBias_var.Define(f"{var}_invQ_all_pt", f"1.0 - {var}InvQMapAllTogetherPtCut{pt_index}::eval(PFSelection_{var})")
            df_SingleMuon_q = df_SingleMuon_var.Define(f"{var}_invQ_all_pt", f"1.0 - {var}InvQMapAllTogetherPtCut{pt_index}::eval(PFSelection_{var})")
            df_MCDYJets_q = df_MCDYJets_var.Define(f"{var}_invQ_all_pt", f"1.0 - {var}InvQMapAllTogetherPtCut{pt_index}::eval(PFSelection_{var})")

            df_SingleMuon_q = DiMuonPtCut(df_SingleMuon_q, pt_cut)
            df_MCDYJets_q = DiMuonPtCut(df_MCDYJets_q, pt_cut)

            plot_column = f"{var}_invQ_all_pt"
            plot_xlabel = "1 - F_{MB}(x)"

            h_MinBias_ptr = df_MinBias_q.Histo1D(
                (f"h_MinBias_{var}_quantile_all_ptscan", f"; {plot_xlabel}; {y_title}", 10, 0, 1),
                plot_column,
            )
            h_SingleMuon_ptr = df_SingleMuon_q.Histo1D(
                (f"h_SingleMuon_{var}_quantile_all_ptscan_{pt_index}", f"; {plot_xlabel}; {y_title}", 10, 0, 1),
                plot_column,
            )
            h_MCDYJets_ptr = df_MCDYJets_q.Histo1D(
                (f"h_MCDYJets_{var}_quantile_all_ptscan_{pt_index}", f"; {plot_xlabel}; {y_title}", 10, 0, 1),
                plot_column,
            )

            h_MinBias = h_MinBias_ptr.GetValue()
            h_SingleMuon = h_SingleMuon_ptr.GetValue()
            h_MCDYJets = h_MCDYJets_ptr.GetValue()

            NomaliseHist(h_MinBias)
            NomaliseHist(h_SingleMuon)
            NomaliseHist(h_MCDYJets)

            colour = colours[len(ratio_data_hists) % len(colours)]

            ratio_SingleMuon = h_SingleMuon.Clone(f"ratio_quantile_all_data_{var}_pt{pt_index}")
            ratio_SingleMuon.Divide(h_MinBias)
            ratio_SingleMuon.SetLineColor(colour)
            ratio_SingleMuon.SetLineWidth(2)

            ratio_MCDYJets = h_MCDYJets.Clone(f"ratio_quantile_all_mc_{var}_pt{pt_index}")
            ratio_MCDYJets.Divide(h_MinBias)
            ratio_MCDYJets.SetLineColor(colour)
            ratio_MCDYJets.SetLineWidth(2)
            ratio_MCDYJets.SetLineStyle(2)

            ratio_data_hists.append((var, label, ratio_SingleMuon))
            ratio_mc_hists.append((var, label, ratio_MCDYJets))

        if not ratio_data_hists:
            print(f"Warning: no valid histograms were produced for all-together quantile pT-cut plot (pT < {pt_cut} GeV)")
            continue

        canvas = ROOT.TCanvas(f"c_quantile_all_together_pt_{pt_index}", "", 800, 700)
        canvas.cd()
        canvas.SetBottomMargin(0.13)
        canvas.SetLogy()

        first_ratio = ratio_data_hists[0][2]
        max_val = max(max(r.GetMaximum(), m.GetMaximum()) for (_, _, r), (_, _, m) in zip(ratio_data_hists, ratio_mc_hists))

        first_ratio.GetXaxis().SetTitle("1 - F_{MB}(x)")
        first_ratio.GetYaxis().SetTitle("Number of Events (normalised)")
        first_ratio.GetXaxis().SetTitleSize(0.035)
        first_ratio.GetXaxis().SetTitleOffset(1.3)
        first_ratio.GetXaxis().SetLabelSize(0.035)
        first_ratio.GetXaxis().SetTickLength(0.03)
        first_ratio.GetYaxis().SetTitleSize(0.035)
        first_ratio.GetYaxis().SetLabelSize(0.035)
        first_ratio.SetMaximum(max_val * 2)
        first_ratio.Draw("hist")

        ratio_mc_hists[0][2].Draw("hist same")

        for _, _, ratio in ratio_data_hists[1:]:
            ratio.Draw("hist same")
        for _, _, ratio in ratio_mc_hists[1:]:
            ratio.Draw("hist same")

        legend_col0 = ROOT.TLegend(0.5, 0.58, 0.7, 0.89)
        legend_col1 = ROOT.TLegend(0.74, 0.63, 0.96, 0.9)
        dummy = ROOT.TObject()
        for legend in (legend_col0, legend_col1):
            legend.SetBorderSize(0)
            legend.SetFillStyle(0)
            legend.SetTextSize(0.02)
            legend.SetMargin(0.2)

        legend_Data = ROOT.TLine(0.0, 0.0, 0.5, 0.0)
        legend_Data.SetLineColor(ROOT.kBlack)
        legend_Data.SetLineWidth(2)
        legend_Data.SetLineStyle(1)

        legend_MC = ROOT.TLine(0.0, 0.0, 0.5, 0.0)
        legend_MC.SetLineColor(ROOT.kBlack)
        legend_MC.SetLineWidth(2)
        legend_MC.SetLineStyle(2)

        legend_col0.AddEntry(dummy, f"#bf{{p^{{#mu#mu}}_{{T}} < {pt_cut} GeV}}", "")
        legend_col0.AddEntry(legend_Data, "Data", "l")
        legend_col0.AddEntry(dummy, "#bf{DY}", "")
        legend_col0.AddEntry(dummy, f"{(selected_events_SingleMuon/total_events_SingleMuon) * 100:.2f}% selected Events", "")
        legend_col0.AddEntry(dummy, f"{(selected_PFCands_SingleMuon/total_PFCands_SingleMuon) * 100:.2f}% selected PFCands", "")

        legend_col0.AddEntry(dummy, "#bf{ZeroBias}", "")
        legend_col0.AddEntry(dummy, f"{(selected_events_MinBias/total_events_MinBias) * 100:.2f}% selected Events", "")
        legend_col0.AddEntry(dummy, f"{(selected_PFCands_MinBias/total_PFCands_MinBias) * 100:.2f}% selected PFCands", "")

        legend_col0.AddEntry(legend_MC, "MC", "l")
        legend_col0.AddEntry(dummy, "#bf{DY}", "")
        legend_col0.AddEntry(dummy, f"{(selected_events_MCDYJets/total_events_MCDYJets) * 100:.2f}% selected Events", "")
        legend_col0.AddEntry(dummy, f"{(selected_PFCands_MCDYJets/total_PFCands_MCDYJets) * 100:.2f}% selected PFCands", "")

        for (var, label, ratio_data), (_, _, ratio_mc) in zip(ratio_data_hists, ratio_mc_hists):
            legend_col1.AddEntry(ratio_data, f"{label}", "lf")

        legend_col0.Draw()
        legend_col1.Draw()

        output_name = f"new_plots/AllVariables_QuantileAllTogether_ZpT{pt_cut}GeV{out_suffix}.pdf"
        canvas.SaveAs(output_name)
        canvas.Close()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Combined plotting driver for NanoAOD PF-candidate studies"
    )
    parser.add_argument(
        "--mode",
        choices=["compare", "ptscan", "quantile", "quantile-ptscan", "quantile-all", "quantile-all-ptscan", "all"],
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
    return parser.parse_args()


def main():
    args = parse_args()

    df_SingleMuon, df_MinBias, df_MCDYJets = MakeDataframes(args.maxevents)
    total_events = PrintDatasetCounts(df_SingleMuon, df_MinBias, df_MCDYJets)

    df_SingleMuon = VetoMuons(df_SingleMuon)
    df_SingleMuon = GoodMuons(df_SingleMuon)
    df_SingleMuon = DiMuonSelection(df_SingleMuon)

    df_MCDYJets = VetoMuons(df_MCDYJets)
    df_MCDYJets = GoodMuons(df_MCDYJets)
    df_MCDYJets = DiMuonSelection(df_MCDYJets)

    df_SingleMuon, df_MinBias, df_MCDYJets = PVSelection(df_SingleMuon, df_MinBias, df_MCDYJets)
    df_SingleMuon = PFCandidateSelection(df_SingleMuon, args.charge)
    df_MinBias = PFCandidateSelection(df_MinBias, args.charge)
    df_MCDYJets = PFCandidateSelection(df_MCDYJets, args.charge)

    df_SingleMuon = addInvariantMass(df_SingleMuon)
    df_MinBias = addInvariantMass(df_MinBias)
    df_MCDYJets = addInvariantMass(df_MCDYJets)

    if args.no_plot:
        print("Selections finished. Plotting disabled by --no-plot.")
        return

    if args.mode in ["compare", "all"]:
        Plot_CompareTriggers(df_SingleMuon, df_MinBias, df_MCDYJets, args.compare_vars, total_events, args.output_suffix)

    if args.mode in ["ptscan", "all"]:
        Plot_DiMuonPtCut(df_SingleMuon, df_MinBias, df_MCDYJets, args.ptscan_vars, args.pt_cuts, total_events, args.output_suffix)

    if args.mode in ["quantile", "all"]:
        QuantilePerObservable(df_SingleMuon, df_MinBias, df_MCDYJets, args.quantile_vars, total_events, args.output_suffix)
    if args.mode in ["quantile-ptscan", "all"]:
        Quantile_DiMuonPtCut(df_SingleMuon, df_MinBias, df_MCDYJets, args.quantile_ptscan_vars, args.pt_cuts, total_events, args.output_suffix)

    if args.mode in ["quantile-all", "all"]:
        Quantile_AllTogether(df_SingleMuon, df_MinBias, df_MCDYJets, args.quantile_vars, total_events, args.output_suffix)

    if args.mode in ["quantile-all-ptscan", "all"]:
        Quantile_AllTogether_DiMuonPtCut(df_SingleMuon, df_MinBias, df_MCDYJets, args.quantile_ptscan_vars, args.pt_cuts, total_events, args.output_suffix)

if __name__ == "__main__":
    main()
