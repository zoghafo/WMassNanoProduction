import ROOT
from ROOT import gPad
import sys
import matplotlib as mat
import matplotlib.pyplot as plt
import numpy as np
import os
import random

ROOT.gStyle.SetOptStat(0)

fileName_SingleMuon = '/home/z/zoghafoo/CMSSW_10_6_26/src/Configuration/WMassNanoProduction/myFiles/NanoV9DataPostVFP_PF_SingleMuon_100000Events.root'
fileName_MinBias = '/home/z/zoghafoo/CMSSW_10_6_26/src/Configuration/WMassNanoProduction/myFiles/NanoV9DataPostVFP_PF_ZeroBias_100000Events.root'

file_SingleMuon = ROOT.TFile.Open(fileName_SingleMuon, "READ")
file_MinBias = ROOT.TFile.Open(fileName_MinBias, "READ")

events_SingleMuon = file_SingleMuon.Get("Events")
events_MinBias = file_MinBias.Get("Events")

# Set to None to use all events.
MAX_EVENTS = int(sys.argv[1]) if len(sys.argv) > 1 else None

df_SingleMuon = ROOT.RDataFrame("Events", file_SingleMuon)
df_MinBias = ROOT.RDataFrame("Events", file_MinBias)

if MAX_EVENTS is not None:
    print(f"Processing only the first {MAX_EVENTS} events from each file.")
    df_SingleMuon = df_SingleMuon.Range(MAX_EVENTS)
    df_MinBias = df_MinBias.Range(MAX_EVENTS)
# columns = df_SingleMuon.GetColumnNames()

totalNumberOfEvents_SingleMuon = df_SingleMuon.Count().GetValue()
print(f"Total number of events in SingleMuon file: {totalNumberOfEvents_SingleMuon}")
totalNumberOfEvents_MinBias = df_MinBias.Count().GetValue()
print(f"Total number of events in MinBias file: {totalNumberOfEvents_MinBias}")


variables = {
    'PFCands_pt': 'p_{T} [GeV]',
    'PFCands_eta': '\\eta',
    'PFCands_phi': '\\phi',
    'PFCands_mass': 'm [GeV]',
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
    'PFCands_mass': [10, 0, 0.2],
    'PFCands_pvAssocQuality': [9, 0, 9],
    'nPFCands': [3.0, 5.0, 8.0, 11.0, 15.0, 20.0, 27.0, 34.0, 43.0, 54.0, 65.0, 90.0, 130., 160.],
    'PFCands_Ht': [0, 5, 10, 15, 20, 30, 50, 70, 90, 110, 130, 150, 170, 200, 230, 260, 300, 350, 370],
    'PFCands_Pt2sum': [0, 10, 20, 30, 40, 50, 70, 90, 120, 140, 160, 200, 250, 300, 350, 400],
    'PFCands_Psum': [0, 10, 20, 30, 40, 50, 60, 70, 100, 150, 200, 250, 300, 350, 400],
    'PFCands_P2sum': [0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 250, 300, 400, 500, 600, 800, 1000, 1500, 2000, 2500, 3000, 3500, 4000],
}

def deltaPhi(phi1, phi2):
    result = phi1 - phi2
    while result > np.pi:
        result -= 2 * np.pi
    while result <= -1.0 * np.pi:
        result += 2 * np.pi
    return result

def deltaR2(eta1, phi1, eta2, phi2):
    deta = eta1 - eta2
    dphi = deltaPhi(phi1, phi2)
    return deta**2 + dphi**2

def vectdeltaR2(eta1, phi1, eta2, phi2):
    vect = []
    for i in range(len(eta1)):
        vect.append(deltaR2(eta1[i], phi1[i], eta2[i], phi2[i]))
    return vect

def hasTriggerMatch(eta, phi, TrigObj_eta, TrigObj_phi):
  for jtrig in range(TrigObj_eta.size()):  
    if deltaR2(eta, phi, TrigObj_eta[jtrig], TrigObj_phi[jtrig]) < 0.09:
      return True  
  
  return False


#---------- Muon Selection ----------

def VetoMuons(df):
    df = df.Define("Muon_veto",
                   "Muon_standalonePt > 15 && Muon_highPurity && " "Muon_standaloneNumberOfValidHits >= 1 && Muon_looseId && "
                    "abs(Muon_dxybs) < 0.05"
                    )
    return df

def GoodMuons(df):
    df = df.Define("Muon_good",
                   "Muon_pt > 26 && "
                   "abs(Muon_eta) < 2.4"
                   )
    return df

# def diMuonSelection(df):
#     df = df.Filter("nMuon == 2")
#     df = df.Filter("Muon_veto[0] == 1 && Muon_veto[1] == 1 && Muon_good[0] == 1 && Muon_good[1] == 1")
#     df = df.Filter("Muon_charge[0] * Muon_charge[1] < 0")
#     return df

# df_SingleMuon.Display(["nMuon", "Muon_veto", "Muon_good", "Muon_charge"], 20).Print()


def diMuonSelection(df):
    df = df.Define("Muon_sel", "Muon_veto && Muon_good")
    df = df.Filter("Sum(Muon_sel) == 2")
    df = df.Define("Muon_idx", "Nonzero(Muon_sel)")
    df = df.Filter("Muon_charge[Muon_idx[0]] * Muon_charge[Muon_idx[1]] < 0")
    return df

df_SingleMuon = VetoMuons(df_SingleMuon)
df_SingleMuon = GoodMuons(df_SingleMuon)
df_SingleMuon = diMuonSelection(df_SingleMuon)

# df_SingleMuon.Filter("nMuon == 3").Display(["nMuon", "Muon_veto", "Muon_good", "Muon_sel", "Muon_idx", "Muon_charge"], 50).Print()




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

    return df



# Apply PF Candidates selection to both triggers
df_SingleMuon = PFCandidateSelection(df_SingleMuon, 1)
df_MinBias = PFCandidateSelection(df_MinBias, 1)

# df_SingleMuon.Display(["PFCands_pt", "PF", "PFSelection_idx"], 50).Print()



for var, label in variables.items():


    #----------- Calculation of variables ----------

    if var in ['PFCands_pt', 'PFCands_eta', 'PFCands_phi', 'PFCands_mass', 'PFCands_pvAssocQuality']:
        df_SingleMuon = df_SingleMuon.Define(f"PFSelection_{var}", f"Take({var}, PFSelection_idx)")
        df_MinBias = df_MinBias.Define(f"PFSelection_{var}", f"Take({var}, PFSelection_idx)")
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
        # uniform binning
        h_SingleMuon = df_SingleMuon.Histo1D(
            (f"h_SingleMuon_{var}", f"; {label}; Number of PF Candidates (normalised)",
            bins[0], bins[1], bins[2]),
            f"PFSelection_{var}"
        )

        h_MinBias = df_MinBias.Histo1D(
            (f"h_MinBias_{var}", f"; {label}; Number of PF Candidates (normalised)",
            bins[0], bins[1], bins[2]),
            f"PFSelection_{var}"
        )

    else:
        # variable binning
        edges = array.array('d', bins)

        h_SingleMuon = df_SingleMuon.Histo1D(
            (f"h_SingleMuon_{var}", f"; {label}; Number of PF Candidates (normalised)",
            len(edges) - 1, edges),
            f"PFSelection_{var}"
        )

        h_MinBias = df_MinBias.Histo1D(
            (f"h_MinBias_{var}", f"; {label}; Number of PF Candidates (normalised)",
            len(edges) - 1, edges),
            f"PFSelection_{var}"
        )

    hist_SingleMuon = h_SingleMuon.GetValue()
    h_SingleMuon.Scale(1 / hist_SingleMuon.Integral())
    h_SingleMuon.SetStats(0)

    hist_MinBias = h_MinBias.GetValue()
    h_MinBias.Scale(1 / hist_MinBias.Integral())
    h_MinBias.SetStats(0)


    # bins = binning[var] if var in binning.keys() else None
    # if bins is not None:
    #     bin_widths = np.diff(bins)
    #     bin_indices = np.digitize(h_MinBias.GetValue(), bins) - 1

    #     weights = [
    #         1.0 / bin_widths[i] if 0 <= i < len(bin_widths) else 0
    #         for i in bin_indices
    #     ]
    # else:
    #     weights = None
    

    canvas = ROOT.TCanvas("c")
    pad1 = ROOT.TPad("pad1", "pad1", 0, 0.32, 1, 1)
    pad1.Draw()
    pad1.cd()
    pad1.SetBottomMargin(0.05)
    pad1.SetLogy()
    hist_SingleMuon.GetXaxis().SetLabelSize(0)
    hist_SingleMuon.Draw("hist")
    hist_SingleMuon.SetLineColor(ROOT.kViolet-6)
    hist_SingleMuon.SetLineWidth(2)
    hist_SingleMuon.GetXaxis().SetTitle("")
    hist_SingleMuon.GetYaxis().SetTitle("Number of PF Candidates (normalised)")
    hist_SingleMuon.GetYaxis().SetLabelSize(0.048)
    hist_SingleMuon.GetYaxis().SetTitleSize(0.045)
    hist_SingleMuon.GetYaxis().SetTitleOffset(1)

    hist_MinBias.Draw("hist same")
    hist_MinBias.SetLineColor(ROOT.kOrange+5)
    hist_MinBias.SetLineWidth(2)

    hist_SingleMuon.SetMaximum(max(hist_SingleMuon.GetMaximum(), hist_MinBias.GetMaximum()) * 1.3)

    legend = ROOT.TLegend(0.68, 0.75, 0.87, 0.87)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    legend.SetTextSize(0.04)
    legend.SetMargin(0.2)
    legend.AddEntry(hist_SingleMuon, "SingleMuon Trigger", "l")
    legend.AddEntry(hist_MinBias, "ZeroBias Trigger", "l")
    legend.Draw()

    canvas.cd()

    pad2 = ROOT.TPad("pad2", "pad2", 0, 0, 1, 0.35)
    pad2.Draw()
    pad2.cd()
    pad2.SetTopMargin(0.05)
    pad2.SetBottomMargin(0.35)
    ratio = hist_SingleMuon.Clone("ratio")
    ratio.Divide(hist_MinBias)
    ratio.SetLineColor(ROOT.kBlack)
    ratio.SetMarkerStyle(20)
    ratio.GetYaxis().SetTitle("SingleMuon / ZeroBias")
    ratio.Draw("pe")
    ratio.GetXaxis().SetTitle(label)
    ratio.GetXaxis().SetTitleSize(0.1)
    ratio.GetXaxis().SetTitleOffset(1.3)
    ratio.GetXaxis().SetLabelSize(0.09)
    ratio.GetXaxis().SetTickLength(0.07)
    ratio.GetYaxis().SetTitleSize(0.09)
    ratio.GetYaxis().SetLabelSize(0.09)
    ratio.GetYaxis().SetTitleOffset(0.5)
    ratio.SetMarkerSize(0.8)
    min_val = ratio.GetBinContent(ratio.GetMinimumBin()) if ratio.GetBinContent(ratio.GetMinimumBin()) > 0 else 1e-3
    max_val = ratio.GetBinContent(ratio.GetMaximumBin())
    ratio.SetMinimum(min_val * 0.2)
    ratio.SetMaximum(max_val * 10)
    # ratio.GetYaxis().SetNdivisions(500)
    pad2.SetLogy()
    # line = ROOT.TLine(ratio.GetXaxis().GetXmin(), 0, ratio.GetXaxis().GetXmax(), 0)
    # for y in [1, 10, 100]:
        # line = ROOT.TLine(ratio.GetXaxis().GetXmin(), y, ratio.GetXaxis().GetXmax(), y)
    # line.SetLineStyle(".")
    # line.Draw("same")
    gPad.SetGridy()
    gPad.SetLineStyle(2)
    gPad.SetLineWidth(1)
    gPad.SetLineColor(15)
    legend_ratio = ROOT.TLegend(0.84, 0.4, 0.895, 0.5)
    legend_ratio.SetBorderSize(0)
    # legend_ratio.SetFillStyle(0)
    legend_ratio.SetTextSize(0.08)
    legend_ratio.AddEntry(ratio, "Ratio", "pe")
    legend_ratio.Draw()
    
    canvas.SaveAs(f"{var}.pdf")
    canvas.Close()