import ROOT
import sys
import matplotlib as mat
import matplotlib.pyplot as plt
import numpy as np
import os
import random

# from wremnants.muon_selections import *

# Disable ROOT's default statistics box on plots.
ROOT.gStyle.SetOptStat(0)


if len(sys.argv) < 1:
    print(f"USAGE: {sys.argv[0]} <TRIGGER> <NUMBER_OF_EVENTS_IN_FILE (100 OR 100000)> <NUMBER_OF_EVENTS_TO_PROCESS>")
    sys.exit(1)

# trigger = sys.argv[1]

# file_NEvents = sys.argv[2] if len(sys.argv) > 2 else 100000
# if file_NEvents not in ['100', '100000']:
#     print(f"Invalid value for NUMBER_OF_EVENTS_IN_FILE. Please use '100' or '100000'.")
#     sys.exit(1)
# else:
fileName_SingleMuon = '/home/z/zoghafoo/CMSSW_10_6_26/src/Configuration/WMassNanoProduction/myFiles/NanoV9DataPostVFP_PF_SingleMuon_100000Events.root'
fileName_MinBias = '/home/z/zoghafoo/CMSSW_10_6_26/src/Configuration/WMassNanoProduction/myFiles/NanoV9DataPostVFP_PF_ZeroBias_100000Events.root'

# NEvents = int(sys.argv[3] if len(sys.argv) > 3 else 100000)


file_SingleMuon = ROOT.TFile.Open(fileName_SingleMuon, "READ")
file_MinBias = ROOT.TFile.Open(fileName_MinBias, "READ")
events_SingleMuon = file_SingleMuon.Get("Events")
events_MinBias = file_MinBias.Get("Events")

df_SingleMuon = ROOT.RDataFrame("Events", file_SingleMuon)
df_MinBias = ROOT.RDataFrame("Events", file_MinBias)
# columns = df_SingleMuon.GetColumnNames()

# df_SingleMuon.Display(["PFCands_Ht"], 20).Print()

# print(list(df_SingleMuon.GetColumnNames()))

# if "PFCands_Ht" not in df_MinBias.GetColumnNames():
#     print("PFCands_Ht not found in the dataframe. Please check the column names.")
#     sys.exit(1)
# else:
#     print("PFCands_Ht found in the dataframe. Proceeding with calculations.")

variables = {
    # 'PFCands_pt': 'p_{T} [GeV]',
    # 'PFCands_eta': '\\eta',
    # 'PFCands_phi': '\\phi',
    # 'PFCands_mass': 'm [GeV]',
    # 'PFCands_pvAssocQuality': 'PV association quality',
    # 'nPFCands': 'Number of PF candidates',
    'PFCands_Ht': 'H_{T} [GeV]',
    # 'PFCands_Pt2sum': '\\sum_{cands} p^{2}_{T} [GeV^{2}]',
    # 'PFCands_Psum': '\\sum_{cands} p [GeV]',
    # 'PFCands_P2sum': '\\sum_{cands} p^{2} [GeV^{2}]',
}

binning = {
    'PFCands_pt': [10, 0, 10],
    'PFCands_eta': [50, -2.5, 2.5],
    'PFCands_phi': [10, -3.14, 3.14],
    'PFCands_mass': [0, 2, 5, 10, 15, 20, 25, 35, 45, 60, 80, 120, 160, 200, 300, 400],
    'PFCands_pvAssocQuality': [7, 0, 7],
    'nPFCands': [3.0, 5.0, 8.0, 11.0, 15.0, 20.0, 27.0, 34.0, 43.0, 54.0, 65.0, 90.0, 130., 160.],
    # 'PFCands_Ht': [0, 5, 10, 15, 20, 30, 50, 70, 90, 110, 130 ],
    'PFCands_Ht': [20, 0, 300],
    'PFCands_Pt2sum': [ 0, 10, 20, 30, 40, 50, 70, 90, 120, 140, 160, 200, 300],
    'PFCands_Psum': [0, 10, 20, 30, 40, 50, 60, 70, 100, 150, 200, 250],
    'PFCands_P2sum': [0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 250, 300, 400, 500, 600, 800, 1000, 1500, 2000, 2500],
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
    df = df.Define("Muon_veto", "Muon_standalonePt > 15 && Muon_highPurity && Muon_standaloneNumberOfValidHits >= 1 && Muon_looseId && abs(Muon_dxybs) < 0.05")
    return df

def GoodMuons(df):
    df = df.Define("Muon_good", "Muon_pt > 26 && abs(Muon_eta) < 2.4")
    return df

def diMuonSelection(df):
    df = df.Filter("nMuon == 2")
    df = df.Filter("Muon_veto[0] == 1 && Muon_veto[1] == 1 && Muon_good[0] == 1 && Muon_good[1] == 1")
    df = df.Filter("Muon_charge[0] * Muon_charge[1] < 0")
    return df



df_SingleMuon = VetoMuons(df_SingleMuon)
df_SingleMuon = GoodMuons(df_SingleMuon)
df_SingleMuon = diMuonSelection(df_SingleMuon)




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


#----------- Calculation of variables ----------

for var, label in variables.items():

    if var == 'PFCands_Ht':
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




for var, label in variables.items():
        

    bins = binning[var] if len(binning[var]) == 3 else [len(binning[var]) - 1, binning[var][0], binning[var][-1]]

    h_SingleMuon = df_SingleMuon.Histo1D((f"h_SingleMuon_{var}", f"; {label}; Number of PF Candidates per Unit", bins[0], bins[1], bins[2]), f"PFSelection_{var}")

    h_MinBias = df_MinBias.Histo1D((f"h_MinBias_{var}", f"; {label}; Number of PF Candidates (normalised)", bins[0], bins[1], bins[2]), f"PFSelection_{var}")

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
    pad1 = ROOT.TPad("pad1", "pad1", 0, 0.3, 1, 1)
    pad1.Draw()
    pad1.cd()
    pad1.SetBottomMargin(0)
    pad1.SetLogy()
    hist_SingleMuon.Draw("hist")
    hist_SingleMuon.SetLineColor(ROOT.kViolet-6)
    hist_SingleMuon.SetLineWidth(2)
    hist_SingleMuon.GetXaxis().SetTitle("")

    hist_MinBias.Draw("hist same")
    hist_MinBias.SetLineColor(ROOT.kAzure+10)
    hist_MinBias.SetLineWidth(2)

    hist_SingleMuon.SetMaximum(max(hist_SingleMuon.GetMaximum(), hist_MinBias.GetMaximum()) * 1.3)

    legend = ROOT.TLegend(0.65, 0.75, 0.9, 0.87)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    legend.SetTextSize(0.04)
    legend.AddEntry(hist_SingleMuon, "SingleMuon Trigger", "l")
    legend.AddEntry(hist_MinBias, "ZeroBias Trigger", "l")
    legend.Draw()

    canvas.cd()

    pad2 = ROOT.TPad("pad2", "pad2", 0, 0.05, 1, 0.3)
    pad2.Draw()
    pad2.cd()
    pad2.SetTopMargin(0)
    pad2.SetBottomMargin(0.25)
    ratio = hist_SingleMuon.Clone("ratio")
    ratio.Divide(hist_MinBias)
    ratio.SetLineColor(ROOT.kBlack)
    ratio.SetMarkerStyle(20)
    ratio.GetYaxis().SetTitle("SingleMuon / ZeroBias")
    ratio.Draw("pe")
    ratio.GetXaxis().SetTitle(label)
    ratio.GetXaxis().SetTitleSize(0.1)
    ratio.GetXaxis().SetTitleOffset(1.0)
    ratio.GetXaxis().SetLabelSize(0.11)
    ratio.GetYaxis().SetTitleSize(0.08)
    ratio.GetYaxis().SetLabelSize(0.11)
    ratio.GetYaxis().SetTitleOffset(0.5)
    ratio.SetMinimum(-1)
    ratio.SetMaximum(1)
    ratio.GetYaxis().SetNdivisions(505)
    line = ROOT.TLine(ratio.GetXaxis().GetXmin(), 0, ratio.GetXaxis().GetXmax(), 0);
    line.SetLineStyle(2)
    line.Draw("same")

    canvas.SaveAs(f"{var}.pdf")
    canvas.Close()











# for eleccharge in [
#     'Charged',
#     # 'All',
#     # 'Neutral'
#     ]:
#     charged_only = (eleccharge == 'Charged')
#     neutral_only = (eleccharge == 'Neutral')
#     output_suffix = eleccharge

#     for groupvar, grouplabel in variables.items():
#         for var, label in grouplabel.items():

#             values_list = []

#             total_pf_cands = 0
#             selected_pf_cands = 0

#             total_events = events.GetEntries()
#             # print(f"Total number of events in the file: {total_events}")
#             selected_events = 0

            
#             for entryNum in range(events.GetEntries()):
#             # for entryNum in range(NEvents):
#                 events.GetEntry(entryNum)

#                 nMuons = getattr(events, 'nMuon')
#                 muon0_counter = 0
#                 muon1_counter = 0
#                 muon2_counter = 0

#                 if nMuons == 0:
#                     muon0_counter += 1
#                 elif nMuons == 1:
#                     muon1_counter += 1
#                 elif nMuons == 2:
#                     muon2_counter += 1

           


#                 if trigger == 'SingleMuon':

#                     # Veto Muons

#                     standalone_pt = list(getattr(events, "Muon_standalonePt"))
#                     standalone_eta = list(getattr(events, "Muon_standaloneEta"))
#                     standalone_phi = list(getattr(events, "Muon_standalonePhi"))

#                     # standalone_pt > 15 GeV
#                     if all(pt <= 15 for pt in standalone_pt):
#                         continue

#                     # inner track must pass the high-purity flag
#                     highPurity = list(getattr(events, "Muon_highPurity"))
#                     if not any(highPurity):
#                         continue

#                     # the standalone track must have at least one valid hit
#                     standaloneNumberOfValidHits = list(getattr(events, "Muon_standaloneNumberOfValidHits"))
#                     if not any(n >= 1 for n in standaloneNumberOfValidHits):
#                         continue

#                     # p_T > 15 GeV (tracker p_T?)
#                     # pt = list(getattr(events, "Muon_pt"))
#                     # if not any(momT > 15 for momT in pt):
#                     #     continue

#                     # # |eta| < 2.5 (tracker eta?)
#                     # eta = list(getattr(events, "Muon_eta"))
#                     # if not any(abs(eta) < 2.5 for e in eta):
#                     #     continue

#                     # Muons POG ID
#                     looseID = list(getattr(events, "Muon_looseId"))
#                     if not any(looseID):
#                         continue


#                     # dxybs < 0.05 cm
#                     dxybs = list(getattr(events, "Muon_dxybs"))
#                     if any (abs(d) > 0.05 for d in dxybs):
#                         continue



# # -----------------------------------------------------------
#                     # Good Muons

#                     pt = list(getattr(events, "Muon_pt"))
#                     if not any(mom > 26 for mom in pt):
#                         continue

#                     e = list(getattr(events, "Muon_eta"))
#                     if not any (abs(eta) < 2.4 for eta in e):
#                         continue

#                     # medium ID
#                     # mediumID = list(getattr(events, "Muon_mediumID"))
#                     # if not any(mediumID):
#                     #     continue


# # -----------------------------------------------------------
#                     # Di-Muon selection

#                     # Requiring exactly two muons per event
#                     nMuons = getattr(events, "nMuon")
#                     # print(f"Number of muons in event {entryNum}: {nMuons}")
#                     if nMuons != 2:
#                         continue

#                     # Requiring opposite charge for the two muons
#                     charge = list(getattr(events, "Muon_charge"))
#                     muon1_charge = charge[0]
#                     muon2_charge = charge[1]
#                     if not (muon1_charge * muon2_charge < 0):
#                         continue

#                     # invariant mass of the two muons must be between 60 and 120 GeV
#                     # muon1 = ROOT.TLorentzVector()
#                     # muon2 = ROOT.TLorentzVector()

#                     # pt = list(getattr(events, "Muon_pt"))
#                     # eta = list(getattr(events, "Muon_eta"))
#                     # phi = list(getattr(events, "Muon_phi"))

#                     # muon1.SetPtEtaPhiM(pt[0],
#                     #                    eta[0],
#                     #                    phi[0],
#                     #                    getattr(events, "Muon_mass")[0]
#                     #                    )
#                     # muon2.SetPtEtaPhiM(pt[1],
#                     #                    eta[1],
#                     #                    phi[1],
#                     #                    getattr(events, "Muon_mass")[1]
#                     #                    )
                    
#                     # dilepton_mass = (muon1 + muon2).M()
#                     # if not (60 < dilepton_mass < 120):
#                     #     continue







                    

#                     # for impactparam in getattr(events, "Muon_dxybs"):
#                     #     if abs(impactparam) > 0.05:
#                     #         continue
#                     # for looseId in getattr(events, "Muon_looseId"):
#                     #     if not looseId:
#                     #         continue
#                     # for isGlobal in getattr(events, "Muon_isGlobal"):
#                     #     if not isGlobal:
#                     #         continue
                    
#                     # for tracker in getattr(events, "Muon_isTracker"): # select tracker muons, similar to mZ_dilepton.py
#                     #     if not tracker:
#                     #         continue
#                     # for highPurity in getattr(events, "Muon_highPurity"):
#                     #     if not highPurity:
#                     #         continue
#                     # for innerTrackerOriginalAlgo in getattr(events, "Muon_innerTrackOriginalAlgo"):
#                     #     if innerTrackerOriginalAlgo == 13 or innerTrackerOriginalAlgo == 14:
#                     #         continue
#                     # for standaloneNumberOfValidHits in getattr(events, "Muon_standaloneNumberOfValidHits"):
#                     #     if standaloneNumberOfValidHits < 0:
#                     #         continue

#                     # pT cut
#                     muon_pts = list(getattr(events, "Muon_pt"))
#                     # print(len(muon_pts))
#                     # if not any(pt > 15 for pt in muon_pts):
#                     #     continue
#                     # eta cut
#                     muon_etas = list(getattr(events, "Muon_eta"))
#                     # print(len(muon_etas))
#                     # if not any(abs(eta) < 2.5 for eta in muon_etas):
#                     #     continue



#                 selected_events += 1
#                 # print(selected_events)
                

#                 total_pf_cands += len(getattr(events, "PFCands_pt"))  # Assuming pt is always available for counting total PF candidates 
#                 # print(f"{len(getattr(events, 'PFCands_pt'))} PF candidates in entry {entryNum}. Total so far: {total_pf_cands}")


#                 charges = list(getattr(events, "PFCands_charge"))
#                 vertexRef = list(getattr(events, "PFCands_vertexRef"))
#                 pvAssociationQuality = list(getattr(events, "PFCands_pvAssocQuality"))

#                 vertexRef_unique = []
#                 check = 0

#                 for i in vertexRef:
#                     if i not in vertexRef_unique:
#                         vertexRef_unique.append(i)

#                 vertexRef_random = random.choice(vertexRef_unique) if vertexRef_unique else print(f"Warning: No unique vertexRef found for entry {entryNum}.")

#                 # for i in range(len(vertexRef)):
#                 #     if vertexRef[i] == vertexRef_random:
#                 #         check += 1

#                 # print(f"Total Number of PF candidates in event {entryNum}: {len(getattr(events, 'PFCands_pt'))}")

#                 # print(f"Number of different vertices in the event: {len(vertexRef_unique)}")

#                 # print(f"Number of PF candidates associated with the randomly selected vertex (vertexRef_random = {vertexRef_random}): {check}")



#                 if groupvar == 'predefined_variables':

#                     if var != 'N':
#                         values = list(getattr(events, f"PFCands_{var}"))

                        
#                         # to check if the length of values and charges are the same, if not, we just take the values without checking the charge
#                         if len(values) == len(charges) and len(charges) == len(pvAssociationQuality):
#                             if charged_only:

#                                 new_vals = [v for v, q, ref, pv in zip(values, charges, vertexRef, pvAssociationQuality) if q != 0 and ref == vertexRef_random and pv in (6, 7)]
#                                 # cut to have at least two tracks in the event
#                                 if len(new_vals) < 2:
#                                     # print(f"\n\n\nSkipping entry {entryNum} because it has less than 2 charged tracks after selection.\n\n\n")
#                                     continue
#                                 else:
#                                     values_list.extend(new_vals)
#                                     selected_pf_cands += len(new_vals)
                                
#                             elif neutral_only:

#                                 new_vals = [v for v, q, ref, pv in zip(values, charges, vertexRef, pvAssociationQuality) if q == 0 and ref == vertexRef_random and pv in (6, 7)]
#                                 # cut to have at least two tracks in the event
#                                 if len(new_vals) < 2:
#                                     continue
#                                 else:   
#                                     values_list.extend(new_vals)
#                                     selected_pf_cands += len(new_vals)
#                             else:
#                                 values_list.extend(values)
#                                 selected_pf_cands += len(values)
#                         else:
#                             print(f"Warning: Length of values and charges do not match for entry {entryNum}.")
#                             continue



#                     elif var == 'N':  # var == 'Ncharged'
#                         values = 0
#                         if len(charges) > 0:
#                             if charged_only:
#                                 new_vals = [1 for q, ref, pv in zip(charges, vertexRef, pvAssociationQuality) if q != 0 and ref == vertexRef_random and pv in (6, 7)]
#                                 # cut to have at least two tracks in the event
#                                 if len(new_vals) < 2:
#                                     # print(f"\n\n\nSkipping entry {entryNum} because it has less than 2 charged tracks after selection.\n\n\n")
#                                     continue
#                                 else:
#                                     values_list.append(len(new_vals))
#                                     selected_pf_cands += len(new_vals)
#                             elif neutral_only:
#                                 new_vals = [1 for q, ref, pv in zip(charges, vertexRef, pvAssociationQuality) if q == 0 and ref == vertexRef_random and pv in (6, 7)]
#                                 if len(new_vals) < 2:
#                                     continue
#                                 else:
#                                     values_list.append(len(new_vals))
#                                     selected_pf_cands += len(new_vals)
#                             else:
#                                 values_list.append(len(new_vals))
#                                 selected_pf_cands += len(new_vals)
#                         else:
#                             print(f"Warning: No charge information available for entry {entryNum}.")
#                             continue

#                 elif groupvar == 'calculated_variables':
            
#                     if var == 'Ht':
#                         values = list(getattr(events, "PFCands_pt"))

#                         if len(values) == len(charges) and len(charges) == len(pvAssociationQuality):
#                             if charged_only:

#                                 new_vals = [pt for pt, q, ref, pv in zip(values, charges, vertexRef, pvAssociationQuality) if q != 0 and ref == vertexRef_random and pv in (6, 7)]
#                                 # cut to have at least two tracks in the event
#                                 if len(new_vals) < 2:
#                                     # print(f"\n\n\nSkipping entry {entryNum} because it has less than 2 charged tracks after selection.\n\n\n")
#                                     continue
#                                 else:
#                                     Ht = sum(new_vals)
#                                     values_list.append(Ht)
#                                     selected_pf_cands += len(new_vals)
#                             elif neutral_only:
#                                 new_vals = [pt for pt, q, ref, pv in zip(values, charges, vertexRef, pvAssociationQuality) if q == 0 and ref == vertexRef_random and pv in (6, 7)]
#                                 # cut to have at least two tracks in the event
#                                 if len(new_vals) < 2:
#                                     # print(f"\n\n\nSkipping entry {entryNum} because it has less than 2 charged tracks after selection.\n\n\n")
#                                     continue
#                                 else:
#                                     Ht = sum(new_vals)
#                                     values_list.append(Ht)
#                                     selected_pf_cands += len(new_vals)
#                             else:
#                                 Ht = sum(values)
#                                 values_list.append(Ht)
#                                 selected_pf_cands += len(values)
#                         else:
#                             print(f"Warning: Length of PFCands_pt and charges do not match for entry {entryNum}.")
#                             continue


#                     elif var == 'Psum':
#                         values = list(getattr(events, "PFCands_p"))

#                         if len(values) == len(charges) and len(charges) == len(pvAssociationQuality):
#                             if charged_only:

#                                 new_vals = [p for p, q, ref, pv in zip(values, charges, vertexRef, pvAssociationQuality) if q != 0 and ref == vertexRef_random and pv in (6, 7)]
#                                 # cut to have at least two tracks in the event
#                                 if len(new_vals) < 2:
#                                     # print(f"\n\n\nSkipping entry {entryNum} because it has less than 2 charged tracks after selection.\n\n\n")
#                                     continue
#                                 else:
#                                     Psum = sum(new_vals)
#                                     values_list.append(Psum)
#                                     selected_pf_cands += len(new_vals)
#                             elif neutral_only:
#                                 new_vals = [p for p, q, ref, pv in zip(values, charges, vertexRef, pvAssociationQuality) if q == 0 and ref == vertexRef_random and pv in (6, 7)]
#                                 # cut to have at least two tracks in the event
#                                 if len(new_vals) < 2:
#                                     # print(f"\n\n\nSkipping entry {entryNum} because it has less than 2 charged tracks after selection.\n\n\n")
#                                     continue
#                                 else:
#                                     Psum = sum(new_vals)
#                                     values_list.append(Psum)
#                                     selected_pf_cands += len(new_vals)
#                             else:
#                                 Psum = sum(values)
#                                 values_list.append(Psum)
#                                 selected_pf_cands += len(values)
#                         else:
#                             print(f"Warning: Length of PFCands_p and charges do not match for entry {entryNum}.")
#                             continue


#                     elif var == 'P2sum':
#                         values = list(getattr(events, "PFCands_p"))

#                         if len(values) == len(charges) and len(charges) == len(pvAssociationQuality):
#                             if charged_only:
#                                 new_vals = [p for p, q, ref, pv in zip(values, charges, vertexRef, pvAssociationQuality) if q != 0 and ref == vertexRef_random and pv in (6, 7)]
#                                 # cut to have at least two tracks in the event
#                                 if len(new_vals) < 2:
#                                     # print(f"\n\n\nSkipping entry {entryNum} because it has less than 2 charged tracks after selection.\n\n\n")
#                                     continue
#                                 else:
#                                     P2sum = sum(p*p for p in new_vals)
#                                     values_list.append(P2sum)
#                                     selected_pf_cands += len(new_vals)
#                             elif neutral_only:
#                                 new_vals = [p for p, q, ref, pv in zip(values, charges, vertexRef, pvAssociationQuality) if q == 0 and ref == vertexRef_random and pv in (6, 7)]
#                                 # cut to have at least two tracks in the event
#                                 if len(new_vals) < 2:
#                                     # print(f"\n\n\nSkipping entry {entryNum} because it has less than 2 charged tracks after selection.\n\n\n")
#                                     continue
#                                 else:
#                                     P2sum = sum(p*p for p in new_vals)
#                                     values_list.append(P2sum)
#                                     selected_pf_cands += len(new_vals)
#                             else:
#                                 P2sum = sum(p*p for p in values)
#                                 values_list.append(P2sum)
#                                 selected_pf_cands += len(values)
#                         else:
#                             print(f"Warning: Length of PFCands_p and charges do not match for entry {entryNum}.")
#                             continue

#                     elif var == 'Pt2sum':
#                         values = list(getattr(events, "PFCands_pt"))

#                         if len(values) == len(charges) and len(charges) == len(pvAssociationQuality):
#                             if charged_only:
#                                 new_vals = [pt for pt, q, ref, pv in zip(values, charges, vertexRef, pvAssociationQuality) if q != 0 and ref == vertexRef_random and pv in (6, 7)]
#                                 if len(new_vals) < 2:
#                                     # print(f"\n\n\nSkipping entry {entryNum} because it has less than 2 charged tracks after selection.\n\n\n")
#                                     continue
#                                 else:
#                                     Pt2sum = sum(pt*pt for pt in new_vals)
#                                     values_list.append(Pt2sum)
#                                     selected_pf_cands += len(new_vals)
#                             elif neutral_only:
#                                 new_vals = [pt for pt, q, ref, pv in zip(values, charges, vertexRef, pvAssociationQuality) if q == 0 and ref == vertexRef_random and pv in (6, 7)]
#                                 if len(new_vals) < 2:
#                                     # print(f"\n\n\nSkipping entry {entryNum} because it has less than 2 charged tracks after selection.\n\n\n")
#                                     continue
#                                 else:
#                                     Pt2sum = sum(pt*pt for pt in new_vals)
#                                     values_list.append(Pt2sum)
#                                     selected_pf_cands += len(new_vals)
#                             else:
#                                 Pt2sum = sum(pt*pt for pt in values)
#                                 values_list.append(Pt2sum)
#                                 selected_pf_cands += len(values)
#                         else:
#                             print(f"Warning: Length of PFCands_pt and charges do not match for entry {entryNum}.")
#                             continue

#             print(f"\n\n\nNumber of events with exactly 0 muon: {muon0_counter} out of {entryNum+1} events processed.\n")
#             print(f"Number of events with exactly 1 muon: {muon1_counter} out of {entryNum+1} events processed.\n")
#             print(f"Number of events with exactly 2 muon: {muon2_counter} out of {entryNum+1} events processed.\n\n\n")

#             figure = plt.figure(figsize=(9, 6))
            # bins = binning[var] if var in binning.keys() else None
            # if bins is not None:
            #     bin_widths = np.diff(bins)
            #     bin_indices = np.digitize(values_list, bins) - 1

            #     weights = [
            #         1.0 / bin_widths[i] if 0 <= i < len(bin_widths) else 0
            #         for i in bin_indices
            #     ]
            # else:
            #     weights = None

#             plt.hist(
#                 values_list,
#                 bins=bins,
#                 weights=weights,
#                 histtype='stepfilled',
#                 color='purple',
#                 linewidth=2,
#                 density=True if var == 'N' else False,
#                 label=f'{eleccharge} PFCands',
#                 zorder=6
#             )
#             # plt.hist(values_list, bins=binning[var] if var in binning.keys() else None, histtype='stepfilled', color='purple', linewidth=2, label=f'{eleccharge} PFCands', density=True if var == 'N' and var == 'Ht' else False, zorder=6)
#             print(f"Selected events: {selected_events} out of {total_events} total events.")

#             plt.legend(loc='upper right', frameon=True, fontsize=10, title=f"{trigger} Trigger\n\n{selected_events} selected Events\n{(selected_events/total_events)*100:.2f}% efficiency Events\n{selected_pf_cands} selected PF Candidates\n{(selected_pf_cands/total_pf_cands)*100:.2f}% efficiency PF Candidates", facecolor='white')
#             leg = plt.gca().get_legend()
#             leg._legend_box.align = "left"
#             plt.grid(linestyle='-', alpha=0.7)
#             plt.xlabel(label)
#             plt.ylabel("Entries per Unit" if var !='N' else fr"$\frac{{1}}{{N}}\frac{{dN}}{{dN_\mathrm{{charged}}}}$")
#             # if var != 'N' and var != 'Ht' and var != 'P2sum':
#             #     plt.ylim(0, max(plt.ylim())*1.5)
#             plt.yscale('log' if var == 'N' or var == 'P2sum' or var == 'Pt2sum' or var == 'Psum' or var == 'Ht' else 'linear')
#             # plt.savefig(f'/eos/user/z/zoghafoo/www/PF/{trigger}/PFCands_{trigger}_{var}{output_suffix}.pdf')
#             # plt.savefig(f'/home/z/zoghafoo/CMSSW_10_6_26/src/Configuration/WMassNanoProduction/plots/{trigger}/PFCands_{trigger}_{var}{output_suffix}_100000EventsPVSelectionPTEtaCut.pdf')
#             # plt.savefig(f'plots/{trigger}/PFCands_{trigger}_{var}{output_suffix}_{total_events}.pdf')
#             print(f"Plot for variable '{var}' saved as '/eos/user/z/zoghafoo/www/PF/{trigger}/PFCands_{trigger}_{var}{output_suffix}.pdf'.")
#             plt.clf()

# file.Close()