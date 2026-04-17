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
    'PFCands_pt': 'p_{T} [GeV]',
    'PFCands_eta': '\\eta',
    'PFCands_phi': '\\phi',
    'PFCands_InvariantMass': 'm [GeV]',
    'PFCands_pvAssocQuality': 'PV association quality',
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




# df_SingleMuon.Display(["diMuon_pT"], 50).Print()




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


# def PFCandidateSelection(df, eleccharge):

#     df = df.Define("PF",
#                     f"""
#                     (abs(PFCands_charge) == {eleccharge}) &&
#                     (PFCands_vertexRef == PFCands_vertexRefRandom) &&
#                     ((PFCands_pvAssocQuality == 6) || (PFCands_pvAssocQuality == 7)) &&
#                     (abs(PFCands_pdgId) != 13)
#                     """
#                 )
#     df = df.Filter(f"ROOT::VecOps::Sum(PF != 0.f) >= 2")
#     df = df.Define(f"PFSelection_idx", "ROOT::VecOps::Nonzero(PF)")

#     # For the calculation of the PF candidates selection efficiency
#     df = df.Define("nPFSelection", "PFSelection_idx.size()")

#     return df


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

# df_SingleMuon.Display(["PFCands_pt", "PF", "PFSelection_idx"], 50).Print()

if plot == "yes":
    for var, label in variables.items():

        #----------- Calculation of variables ----------
        if var in ['PFCands_pt', 'PFCands_eta', 'PFCands_phi', 'PFCands_pvAssocQuality']:
            df_SingleMuon = df_SingleMuon.Define(f"PFSelection_{var}", f"Take({var}, PFSelection_idx)")
            df_MinBias = df_MinBias.Define(f"PFSelection_{var}", f"Take({var}, PFSelection_idx)")
        elif var == 'PFCands_InvariantMass':
            df_SingleMuon = df_SingleMuon.Define(f"PFSelection_{var}", "PFCands_InvariantMass")
            df_MinBias = df_MinBias.Define(f"PFSelection_{var}", "PFCands_InvariantMass")
        elif var == 'nPFCands':
            df_SingleMuon = df_SingleMuon.Define(f"PFSelection_{var}", "PFSelection_idx.size()")
            df_MinBias = df_MinBias.Define(f"PFSelection_{var}", "PFSelection_idx.size()")
        elif var == 'PFCands_Ht':
            df_SingleMuon = df_SingleMuon.Define(f"PFSelection_{var}", "ROOT::VecOps::Sum(Take(PFCands_pt, PFSelection_idx))")
            df_MinBias = df_MinBias.Define(f"PFSelection_{var}", "ROOT::VecOps::Sum(Take(PFCands_pt, PFSelection_idx))")
        elif var == 'PFCands_Pt2sum':
            df_SingleMuon = df_SingleMuon.Define(f"PFSelection_{var}", "ROOT::VecOps::Sum(Take(PFCands_pt * PFCands_pt, PFSelection_idx))")
            df_MinBias = df_MinBias.Define(f"PFSelection_{var}", "ROOT::VecOps::Sum(Take(PFCands_pt * PFCands_pt, PFSelection_idx))")
        elif var == 'PFCands_Psum':
            df_SingleMuon = df_SingleMuon.Define(f"PFSelection_{var}", "ROOT::VecOps::Sum(Take(PFCands_p, PFSelection_idx))")
            df_MinBias = df_MinBias.Define(f"PFSelection_{var}", "ROOT::VecOps::Sum(Take(PFCands_p, PFSelection_idx))")
        elif var == 'PFCands_P2sum':
            df_SingleMuon = df_SingleMuon.Define(f"PFSelection_{var}", "ROOT::VecOps::Sum(Take(PFCands_p * PFCands_p, PFSelection_idx))")
            df_MinBias = df_MinBias.Define(f"PFSelection_{var}", "ROOT::VecOps::Sum(Take(PFCands_p * PFCands_p, PFSelection_idx))")

        bins = binning[var]

        if len(bins) == 3:
            h_tmp = df_MinBias.Histo1D(
                (f"h_MinBias_{var}", f"; {label}; Number of events (normalised)", bins[0], bins[1], bins[2]),
                f"PFSelection_{var}"
            )
        else:
            edges = array('d', bins)
            print(edges)

            h_tmp = df_MinBias.Histo1D(
                (f"h_MinBias_{var}", f"; {label}; Number of events (normalised)", len(edges) - 1, edges),
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
        """)

        if var in ['PFCands_pt', 'PFCands_eta', 'PFCands_phi', 'PFCands_pvAssocQuality']:
            df_MinBias = df_MinBias.Define(
                f"{var}_invQ",
                f"""
                ROOT::RVec<double> q;
                q.reserve(PFSelection_{var}.size());
                for (auto x : PFSelection_{var}) q.push_back(1.0 - {var}InvQMap::eval((double)x));
                return q;
                """
            )
            df_SingleMuon = df_SingleMuon.Define(
                f"{var}_invQ",
                f"""
                ROOT::RVec<double> q;
                q.reserve(PFSelection_{var}.size());
                for (auto x : PFSelection_{var}) q.push_back(1.0 - {var}InvQMap::eval((double)x));
                return q;
                """
            )
        else:
            df_MinBias = df_MinBias.Define(f"{var}_invQ", f"1.0 - {var}InvQMap::eval(PFSelection_{var})")
            df_SingleMuon = df_SingleMuon.Define(f"{var}_invQ", f"1.0 - {var}InvQMap::eval(PFSelection_{var})")

        plot_column = f"{var}_invQ"
        plot_xlabel = f"1 - F_{{MB}}({var})"
        h_MinBias = df_MinBias.Histo1D(
            (f"h_MinBias_{var}", f"; {plot_xlabel}; Number of events (normalised)", 10, 0, 1),
            plot_column
        )
        h_SingleMuon = df_SingleMuon.Histo1D(
            (f"h_SingleMuon_{var}_GeV", f"; {plot_xlabel}; Number of events (normalised)", 10, 0, 1),
            plot_column
        )
       
        canvas = ROOT.TCanvas(f"c_{var}", "", 800, 700)
        canvas.cd()


        legend = ROOT.TLegend(0.12, 0.5, 0.42, 0.87)
        dummy = ROOT.TObject()
        legend.SetBorderSize(0)
        legend.SetFillStyle(0)
        legend.SetTextSize(0.025)
        legend.SetMargin(0.2)

    

        hist_MinBias = h_MinBias.GetValue()

        if hist_MinBias.Integral() != 0:
            hist_MinBias.Scale(1 / hist_MinBias.Integral())
            print(f"Integral > 0")
        else:
            print(f"Integral of MinBias = 0, skipping scaling")
        hist_MinBias.SetStats(0)
        hist_MinBias.GetXaxis().SetTitle(plot_xlabel)


        plot_maximum = 0

        canvas.cd()


        hist = h_SingleMuon.GetValue()

        if hist.Integral() != 0:
            hist.Scale(1 / hist.Integral())
            print(f"Integral > 0")
        else:
            print(f"Integral of SingleMuon = 0, skipping scaling")

        ratio = hist.Clone("ratio")
        ratio.Divide(hist_MinBias)
        ratio.SetStats(0)



        

       
        ratio.SetLineWidth(2)
        ratio.GetXaxis().SetTitle(plot_xlabel)
        ratio.GetYaxis().SetTitle("DY/MinBias")
        ratio.GetYaxis().SetLabelSize(0.03)
        ratio.GetYaxis().SetTitleSize(0.03)
        canvas.SetLogy()
        ratio.Draw("hist")


        # hist_MinBias.Draw("hist same")
        # hist_MinBias.SetLineColor(ROOT.kOrange+5)
        # hist_MinBias.SetLineWidth(2)
        max_val = ratio.GetBinContent(ratio.GetMaximumBin())

        if plot_maximum < max_val:
            plot_maximum = max_val

        legend.Draw()

        canvas.SaveAs(f"{var}_Quantiletest.pdf")
        canvas.Close()