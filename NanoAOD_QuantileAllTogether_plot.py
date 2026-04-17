from array import array

import ROOT
import sys

ROOT.gStyle.SetOptStat(0)

plot = sys.argv[1] if len(sys.argv) > 1 else "no"

# Set to None to use all events.
MAX_EVENTS = int(sys.argv[2]) if len(sys.argv) > 2 else None

fileName1_SingleMuon = '/home/z/zoghafoo/CMSSW_10_6_26/src/Configuration/WMassNanoProduction/NanoV9DataPostVFP_PF_SingleMuon_100000Events_skip0.root'
fileName2_SingleMuon = '/home/z/zoghafoo/CMSSW_10_6_26/src/Configuration/WMassNanoProduction/NanoV9DataPostVFP_PF_SingleMuon_100000Events_skip100000.root'
fileName3_SingleMuon = '/home/z/zoghafoo/CMSSW_10_6_26/src/Configuration/WMassNanoProduction/NanoV9DataPostVFP_PF_SingleMuon_100000Events_skip200000.root'
fileName4_SingleMuon = '/home/z/zoghafoo/CMSSW_10_6_26/src/Configuration/WMassNanoProduction/NanoV9DataPostVFP_PF_SingleMuon_100000Events_skip300000.root'


fileName1_ZeroBias = '/home/z/zoghafoo/CMSSW_10_6_26/src/Configuration/WMassNanoProduction/NanoV9DataPostVFP_PF_ZeroBias_100000Events_skip0.root'
fileName2_ZeroBias = '/home/z/zoghafoo/CMSSW_10_6_26/src/Configuration/WMassNanoProduction/NanoV9DataPostVFP_PF_ZeroBias_100000Events_skip100000.root'
fileName3_ZeroBias = '/home/z/zoghafoo/CMSSW_10_6_26/src/Configuration/WMassNanoProduction/NanoV9DataPostVFP_PF_ZeroBias_100000Events_skip200000.root'
fileName4_ZeroBias = '/home/z/zoghafoo/CMSSW_10_6_26/src/Configuration/WMassNanoProduction/NanoV9DataPostVFP_PF_ZeroBias_100000Events_skip300000.root'
fileName5_ZeroBias = '/home/z/zoghafoo/CMSSW_10_6_26/src/Configuration/WMassNanoProduction/NanoV9DataPostVFP_PF_ZeroBias_100000Events_skip400000.root'


df_SingleMuon = ROOT.RDataFrame("Events", {fileName1_SingleMuon, fileName2_SingleMuon, fileName3_SingleMuon, fileName4_SingleMuon})

df_MinBias = ROOT.RDataFrame("Events", {fileName1_ZeroBias, fileName2_ZeroBias, fileName3_ZeroBias, fileName4_ZeroBias, fileName5_ZeroBias})


if MAX_EVENTS is not None:
    print(f"Processing only the first {MAX_EVENTS} events from each file.")
    df_SingleMuon = df_SingleMuon.Range(MAX_EVENTS)
    df_MinBias = df_MinBias.Range(MAX_EVENTS)



totalNumberOfEvents_SingleMuon = df_SingleMuon.Count().GetValue()
print(f"Total number of events in SingleMuon file: {totalNumberOfEvents_SingleMuon}\n")
totalNumberOfEvents_MinBias = df_MinBias.Count().GetValue()
print(f"Total number of events in MinBias file: {totalNumberOfEvents_MinBias}\n\n")

totalNumberOfPFCands_SingleMuon = df_SingleMuon.Sum("nPFCands").GetValue()
print(f"Total number of PF Candidates in SingleMuon file: {totalNumberOfPFCands_SingleMuon}\n")
totalNumberOfPFCands_MinBias = df_MinBias.Sum("nPFCands").GetValue()
print(f"Total number of PF Candidates in MinBias file: {totalNumberOfPFCands_MinBias}\n\n")

# df_SingleMuon.Display(["PFCands_pt"], 10).Print()
# df_MinBias.Display(["PFCands_pt"], 10).Print()

# print(f"Number of events with at least one muon as PF candidates in SingleMuon file (before any selection): {df_SingleMuon.Filter('ROOT::VecOps::Sum(abs(PFCands_pdgId) == 13) > 0').Count().GetValue()}\n")
# print(f"Number of events with at least one muon as PF candidates in MinBias file (before any selection): {df_MinBias.Filter('ROOT::VecOps::Sum(abs(PFCands_pdgId) == 13) > 0').Count().GetValue()}\n\n")


variables = {
    # 'PFCands_pt': 'p_{T} [GeV]',
    # 'PFCands_eta': '\\eta',
    # 'PFCands_phi': '\\phi',
    'PFCands_InvariantMass': 'm_{inv} [GeV]',
    # 'PFCands_pvAssocQuality': 'PV association quality',
    'nPFCands': 'N^{PF}_{charged}',
    'PFCands_Ht': 'H_{T} [GeV]',
    'PFCands_Pt2sum': '\\sum_{PF cands} p^{2}_{T} [GeV^{2}]',
    'PFCands_Psum': '\\sum_{PF cands} p [GeV]',
    'PFCands_P2sum': '\\sum_{PF cands} p^{2} [GeV^{2}]',
}

binning = {
    'PFCands_pt': [20, 0, 100],
    'PFCands_eta': [20, -2.4, 2.4],
    'PFCands_phi': [20, -3.14, 3.14],
    'PFCands_InvariantMass': [0, 2, 5, 10, 15, 20, 25, 35, 45, 60, 80, 120, 160, 200, 300, 400],
    'PFCands_pvAssocQuality': [9, 0, 9],
    'nPFCands': [3.0, 5.0, 8.0, 11.0, 15.0, 20.0, 27.0, 34.0, 43.0, 54.0, 65.0, 90.0, 130., 160.],
    'PFCands_Ht': [0, 5, 10, 15, 20, 30, 50, 70, 90, 110, 130, 150, 170, 200, 230, 260, 300, 350, 370],
    'PFCands_Pt2sum': [0, 10, 20, 30, 40, 50, 70, 90, 120, 140, 160, 200, 250, 300, 350, 400],
    'PFCands_Psum': [0, 10, 20, 30, 40, 50, 60, 70, 100, 150, 200, 250, 300, 350, 400],
    'PFCands_P2sum': [0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 250, 300, 400, 500, 600, 800, 1000, 1500, 2000, 2500, 3000, 3500, 4000],
}

#---------- Muon Selection ----------

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

def diMuonSelection(df):
    df = df.Define("Muon_sel", "Muon_veto && Muon_good")
    df = df.Filter("ROOT::VecOps::Sum(Muon_sel) == 2")
    df = df.Define("Muon_idx", "ROOT::VecOps::Nonzero(Muon_sel)")
    df = df.Filter("Muon_charge[Muon_idx[0]] * Muon_charge[Muon_idx[1]] < 0")

    df = df.Define("diMuon_pT", "pow(pow(Muon_pt[Muon_idx[0]] * cos(Muon_phi[Muon_idx[0]]) + Muon_pt[Muon_idx[1]] * cos(Muon_phi[Muon_idx[1]]), 2) + pow(Muon_pt[Muon_idx[0]] * sin(Muon_phi[Muon_idx[0]]) + Muon_pt[Muon_idx[1]] * sin(Muon_phi[Muon_idx[1]]), 2), 0.5)")
    return df


df_SingleMuon = VetoMuons(df_SingleMuon)
df_SingleMuon = GoodMuons(df_SingleMuon)
df_SingleMuon = diMuonSelection(df_SingleMuon)

def diMuonPtCut(df, pT_diMuonCut):
    df = df.Filter(f"diMuon_pT < {pT_diMuonCut}")
    return df


df_SingleMuon = df_SingleMuon.Define("PFCands_vertexRefUnique",
                """
                std::set<int> sorted_unique(PFCands_vertexRef.begin(), PFCands_vertexRef.end());
                return ROOT::VecOps::RVec<int>(sorted_unique.begin(), sorted_unique.end());
                """
                )

df_SingleMuon = df_SingleMuon.Define("PFCands_vertexRefRandom",
                """
                if (PFCands_vertexRefUnique.size() == 0) return -1;
                return PFCands_vertexRefUnique[0];
                """
                )

df_MinBias = df_MinBias.Define("PFCands_vertexRefUnique",
                """
                std::set<int> sorted_unique(PFCands_vertexRef.begin(), PFCands_vertexRef.end());
                return ROOT::VecOps::RVec<int>(sorted_unique.begin(), sorted_unique.end());
                """
                )

df_MinBias = df_MinBias.Define("PFCands_vertexRefRandom",
                """
                if (PFCands_vertexRefUnique.size() == 0) return -1;
                return PFCands_vertexRefUnique[gRandom->Integer(PFCands_vertexRefUnique.size())];
                """
                )

def PFCandidateSelection(df, eleccharge):
    df = df.Define("PF",
                    f"""
                    (abs(PFCands_charge) == {eleccharge}) &&
                    (PFCands_vertexRef == PFCands_vertexRefRandom) &&
                    ((PFCands_pvAssocQuality == 6) || (PFCands_pvAssocQuality == 7)) &&
                    (abs(PFCands_pdgId) != 13)
                    """
                )
    df = df.Filter(f"ROOT::VecOps::Sum(PF != 0.f) >= 2")
    df = df.Define(f"PFSelection_idx", "ROOT::VecOps::Nonzero(PF)")

    # For the calculation of the PF candidates selection efficiency
    df = df.Define("nPFSelection", "PFSelection_idx.size()")

    return df


# Apply PF Candidates selection to both triggers
df_SingleMuon = PFCandidateSelection(df_SingleMuon, 1)
df_MinBias = PFCandidateSelection(df_MinBias, 1)

df_SingleMuon = df_SingleMuon.Define("PFCands_InvariantMass", """
    TLorentzVector sum;
    for (auto idx : PFSelection_idx) {
        TLorentzVector p4;
        p4.SetPtEtaPhiM(PFCands_pt[idx], PFCands_eta[idx], PFCands_phi[idx], PFCands_mass[idx]);
        sum += p4;
    }
    return sum.M();
""")

df_MinBias = df_MinBias.Define("PFCands_InvariantMass", """
    TLorentzVector sum;
    for (auto idx : PFSelection_idx) {
        TLorentzVector p4;
        p4.SetPtEtaPhiM(PFCands_pt[idx], PFCands_eta[idx], PFCands_phi[idx], PFCands_mass[idx]);
        sum += p4;
    }
    return sum.M();
""")


# df_SingleMuon.Display(["PF", "PFSelection_idx", "nPFSelection"], 10).Print()

selectedEvents_SingleMuon = df_SingleMuon.Count().GetValue()
selectedEvents_MinBias = df_MinBias.Count().GetValue()
# print(f"Number of selected events in SingleMuon file (before pT cut): {selectedEvents_SingleMuon}")
# print(f"Number of selected events in MinBias file (before pT cut): {selectedEvents_MinBias}")

selectedPFCands_SingleMuon = df_SingleMuon.Sum("nPFSelection").GetValue()
selectedPFCands_MinBias = df_MinBias.Sum("nPFSelection").GetValue()
# print(f"Number of selected PF candidates in SingleMuon file (before pT cut): {selectedPFCands_SingleMuon}")
# print(f"Number of selected PF candidates in MinBias file (before pT cut): {selectedPFCands_MinBias}")

# df_SingleMuon.Display(["PFCands_InvariantMass"], 50).Print()

#----------- Calculation of variables ----------
for var in ['PFCands_pt', 'PFCands_eta', 'PFCands_phi', 'PFCands_pvAssocQuality']:
    df_SingleMuon = df_SingleMuon.Define(f"PFSelection_{var}", f"Take({var}, PFSelection_idx)")
    df_MinBias = df_MinBias.Define(f"PFSelection_{var}", f"Take({var}, PFSelection_idx)")

df_SingleMuon = df_SingleMuon.Define(f"PFSelection_PFCands_InvariantMass", "PFCands_InvariantMass")
df_MinBias = df_MinBias.Define(f"PFSelection_PFCands_InvariantMass", "PFCands_InvariantMass")

df_SingleMuon = df_SingleMuon.Define(f"PFSelection_nPFCands", "PFSelection_idx.size()")
df_MinBias = df_MinBias.Define(f"PFSelection_nPFCands", "PFSelection_idx.size()")

df_SingleMuon = df_SingleMuon.Define(f"PFSelection_PFCands_Ht", "ROOT::VecOps::Sum(Take(PFCands_pt, PFSelection_idx))")
df_MinBias = df_MinBias.Define(f"PFSelection_PFCands_Ht", "ROOT::VecOps::Sum(Take(PFCands_pt, PFSelection_idx))")

df_SingleMuon = df_SingleMuon.Define(f"PFSelection_PFCands_Pt2sum", "ROOT::VecOps::Sum(Take(PFCands_pt * PFCands_pt, PFSelection_idx))")
df_MinBias = df_MinBias.Define(f"PFSelection_PFCands_Pt2sum", "ROOT::VecOps::Sum(Take(PFCands_pt * PFCands_pt, PFSelection_idx))")

df_SingleMuon = df_SingleMuon.Define(f"PFSelection_PFCands_Psum", "ROOT::VecOps::Sum(Take(PFCands_p, PFSelection_idx))")
df_MinBias = df_MinBias.Define(f"PFSelection_PFCands_Psum", "ROOT::VecOps::Sum(Take(PFCands_p, PFSelection_idx))")

df_SingleMuon = df_SingleMuon.Define(f"PFSelection_PFCands_P2sum", "ROOT::VecOps::Sum(Take(PFCands_p * PFCands_p, PFSelection_idx))")
df_MinBias = df_MinBias.Define(f"PFSelection_PFCands_P2sum", "ROOT::VecOps::Sum(Take(PFCands_p * PFCands_p, PFSelection_idx))")

if plot == "yes":
    pt_cuts = [20,
               10,
               4,
               1
               ]
    color_palette = [
        ROOT.kBlue + 1,
        ROOT.kRed + 1,
        ROOT.kGreen + 2,
        ROOT.kOrange + 7,
        ROOT.kMagenta + 1,
        ROOT.kCyan + 2,
        ROOT.kViolet + 1,
        ROOT.kTeal + 3,
        ROOT.kAzure + 7,
        ROOT.kPink + 7,
    ]

    for ptcut in pt_cuts:
        ratio_hists = []
        combined_xlabel = "1 - F_{MB}(x)"
        pt_tag = f"pt{str(ptcut).replace('.', 'p')}"
        df_SingleMuon_pTCut = diMuonPtCut(df_SingleMuon, pT_diMuonCut=ptcut)
        df_MinBias_cut = df_MinBias

        for var, label in variables.items():
            invq_column = f"{var}_invQ_{pt_tag}"
            ns_name = f"{var}_{pt_tag}InvQMap"

            bins = binning[var]

            if len(bins) == 3:
                h_tmp = df_MinBias_cut.Histo1D(
                    (f"h_MinBias_{var}_{pt_tag}_tmp", f"; {label}; Number of events (normalised)", bins[0], bins[1], bins[2]),
                    f"PFSelection_{var}"
                )
            else:
                edges = array('d', bins)
                h_tmp = df_MinBias_cut.Histo1D(
                    (f"h_MinBias_{var}_{pt_tag}_tmp", f"; {label}; Number of events (normalised)", len(edges) - 1, edges),
                    f"PFSelection_{var}"
                )

            hist_tmp = h_tmp.GetValue()
            total = hist_tmp.Integral()

            # Anchor the CDF at the histogram lower edge to avoid flattening the first bin.
            bin_edges = [hist_tmp.GetBinLowEdge(1)]
            cdf_values = [0.0]
            cumulative = 0.0

            for i in range(1, hist_tmp.GetNbinsX() + 1):
                cumulative += hist_tmp.GetBinContent(i)
                edge = hist_tmp.GetBinLowEdge(i + 1)
                F = cumulative / total if total > 0 else 0.0
                bin_edges.append(edge)
                cdf_values.append(F)

            edges_cpp = ", ".join(f"{x:.17g}" for x in bin_edges)
            cdf_cpp = ", ".join(f"{x:.17g}" for x in cdf_values)

            ROOT.gInterpreter.Declare(f"""
            namespace {ns_name} {{
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
            """)

            df_MinBias_cut = df_MinBias_cut.Define(invq_column, f"1.0 - {ns_name}::eval(PFSelection_{var})")
            df_SingleMuon_pTCut = df_SingleMuon_pTCut.Define(invq_column, f"1.0 - {ns_name}::eval(PFSelection_{var})")

            plot_column = invq_column
            plot_xlabel = f"1 - F_{{MB}}({var})"
            h_MinBias = df_MinBias_cut.Histo1D(
                (f"h_MinBias_{var}_{pt_tag}", f"; {plot_xlabel}; Number of events (normalised)", 10, 0, 1),
                plot_column
            )
            h_SingleMuon = df_SingleMuon_pTCut.Histo1D(
                (f"h_SingleMuon_{var}_{pt_tag}", f"; {plot_xlabel}; Number of events (normalised)", 10, 0, 1),
                plot_column
            )

            hist_MinBias = h_MinBias.GetValue()
            if hist_MinBias.Integral() != 0:
                hist_MinBias.Scale(1 / hist_MinBias.Integral())

            hist = h_SingleMuon.GetValue()
            if hist.Integral() != 0:
                hist.Scale(1 / hist.Integral())

            ratio = hist.Clone(f"ratio_{var}_{ptcut}")
            ratio.SetDirectory(0)
            ratio.SetTitle(f"p^{{#mu#mu}}_{{T}} < {ptcut} GeV")
            ratio.Divide(hist_MinBias)
            ratio.SetStats(0)
            ratio.SetLineColor(color_palette[len(ratio_hists) % len(color_palette)])
            ratio.SetLineWidth(2)
            ratio_hists.append((var, label, ratio))

        canvas = ROOT.TCanvas(f"c_{var}")
        canvas.cd()


        pad1 = ROOT.TPad("pad1", "pad1", 0, 0.32, 1, 1)
        pad1.Draw()
        pad1.cd()
        pad1.SetBottomMargin(0.05)
        # pad1.SetRightMargin(0.32)
        pad1.SetLogy()

        legend = ROOT.TLegend(0.73, 0.6, 0.9, 0.9)
        legend.SetBorderSize(0)
        legend.SetFillStyle(0)
        legend.SetTextSize(0.022)

        positive_minima = [h.GetMinimum(1e-12) for _, _, h in ratio_hists if h.GetMinimum(1e-12) > 0]
        y_min = min(positive_minima) if positive_minima else 1e-4
        y_max = max(h.GetMaximum() for _, _, h in ratio_hists) if ratio_hists else 1.0

        canvas.cd()
        pad2 = ROOT.TPad("pad2", "pad2", 0, 0, 1, 0.35)
        pad2.Draw()
        pad2.cd()
        pad2.SetTopMargin(0.05)
        pad2.SetBottomMargin(0.35)
        # pad2.SetRightMargin(0.32)
        # pad2.SetLogy()

        

        ht_ratio = next((h for v, _, h in ratio_hists if v == "PFCands_Ht"), None)
        ratio_ht_hists = []

        for idx, (var_name, label, ratio) in enumerate(ratio_hists):
            pad1.cd()
            ratio.GetXaxis().SetTitle("")
            ratio.GetYaxis().SetTitle("DY/MinBias")
            ratio.GetYaxis().SetLabelSize(0.04)
            ratio.GetYaxis().SetTitleSize(0.045)
            ratio.GetXaxis().SetLabelSize(0)
            ratio.GetXaxis().SetTitleSize(0.035)
            ratio.SetMinimum(0.05)
            ratio.SetMaximum(10)

            if var_name == "PFCands_Ht":
                # Draw histogram
                ratio.Draw("hist" if idx == 0 else "hist same")
                # Overlay error bars
                ratio.Draw("E1 same")
            else:
                ratio.Draw("hist" if idx == 0 else "hist same")
            legend.AddEntry(ratio, label, "l")

            pad2.cd()
            
            # Ratio with H_T
            ratio_HT = ratio.Clone(f"ratioOverHT_{var_name}_{pt_tag}")
            if ht_ratio is None:
                continue
            ratio_HT.Divide(ht_ratio)
            ratio_HT.SetLineColor(color_palette[idx % len(color_palette)])
            ratio_HT.SetMarkerColor(color_palette[idx % len(color_palette)])
            ratio_ht_hists.append(ratio_HT)

            ratio_HT.SetMarkerStyle(20)
            ratio_HT.SetMarkerSize(0.8)
            ratio_HT.GetYaxis().SetTitle(f"[1-F(x)] / [1-F(H_{{T}}]")
            ratio_HT.GetXaxis().SetTitle("1-F(x)")
            ratio_HT.GetXaxis().SetTitleSize(0.1)
            ratio_HT.GetXaxis().SetTitleOffset(1.2)
            ratio_HT.GetXaxis().SetLabelSize(0.09)
            ratio_HT.GetXaxis().SetTickLength(0.07)
            ratio_HT.GetYaxis().SetTitleSize(0.09)
            ratio_HT.GetYaxis().SetLabelSize(0.075)
            ratio_HT.GetYaxis().SetTitleOffset(0.5)
            ratio_HT.SetTitle("")
            ratio_HT.GetXaxis().SetTitle(combined_xlabel)

            pad2.SetGridy()

            # min_val = ratio_HT.GetBinContent(ratio_HT.GetMinimumBin())
            # if min_val <= 0:
            #     min_val = 1e-3
            # max_val = ratio_HT.GetBinContent(ratio_HT.GetMaximumBin())
            # if max_val <= 0:
            #     max_val = 10

            ratio_HT.SetMinimum(0)
            ratio_HT.SetMaximum(2)
            draw_opt = "pe" if idx == 0 else "pe same"
            ratio_HT.Draw(draw_opt)
        pad1.cd()
        legend.Draw()
        canvas.SaveAs(f"AllVariables_Quantiletest_pTcut_{ptcut}_ratioerrorbars.pdf")
        canvas.Close()