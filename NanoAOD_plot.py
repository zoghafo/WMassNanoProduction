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


if len(sys.argv) < 2:
    print(f"USAGE: {sys.argv[0]} <TRIGGER> <NUMBER_OF_EVENTS_IN_FILE (100 OR 100000)> <NUMBER_OF_EVENTS_TO_PROCESS>")
    sys.exit(1)

trigger = sys.argv[1]

file_NEvents = sys.argv[2] if len(sys.argv) > 2 else 100000
if file_NEvents not in ['100', '100000']:
    print(f"Invalid value for NUMBER_OF_EVENTS_IN_FILE. Please use '100' or '100000'.")
    sys.exit(1)
else:
    fileName = '/home/z/zoghafoo/CMSSW_10_6_26/src/Configuration/WMassNanoProduction/myFiles/NanoV9DataPostVFP_PF_'+ trigger +'_' + file_NEvents + 'Events.root'

NEvents = int(sys.argv[3] if len(sys.argv) > 3 else 100000)


file = ROOT.TFile.Open(fileName, "READ")
events = file.Get("Events")

df = ROOT.RDataFrame("Events", file)
columns = df.GetColumnNames()


variables = {
    'predefined_variables': {
        'pt': '$p_\\mathrm{T}\\,\\mathrm{[GeV]}$',
        'eta': '$\\eta$',
        'phi': '$\\phi$',
        # 'mass': '$m\\,\\mathrm{[GeV]}$',
        # 'pvAssocQuality': 'PV association quality',
        # 'N': 'Number of PF candidates',
        },
    'calculated_variables': {
        # 'Ht': '$H_\\mathrm{T}\\,\\mathrm{[GeV]}$',
        # 'Pt2sum': '$\\sum_\mathrm{cands} p^2_{T}\\,\\mathrm{[GeV^2]}$',
        # 'Psum': '$\\sum_\mathrm{cands} p\\,\\mathrm{[GeV]}$',
        # 'P2sum': '$\\sum_\mathrm{cands} p^2\\,\\mathrm{[GeV^2]}$',
    },
}

binning = {
    'pt': [10, 0, 10],
    'eta': [50, -2.5, 2.5],
    'phi': [50, -3.14, 3.14],
    'mass': [0,2,5,10,15,20,25,35,45,60,80,120,160,200,300,400],
    'mass': [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3],
    'pvAssocQuality': [8, -0.5, 7.5],
    'N': [3.0, 5.0, 8.0, 11.0, 15.0, 20.0, 27.0, 34.0, 43.0, 54.0, 65.0, 90.0, 130., 160.],
    'Ht': [0, 5, 10, 15, 20, 30, 50, 70, 90, 110, 130 ],
    'Pt2sum': [ 0., 10, 20, 30, 40, 50, 70, 90, 120, 140, 160, 200, 300],
    'Psum': [0, 10, 20, 30, 40, 50, 60, 70, 100, 150, 200, 250],
    'P2sum': [0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 250, 300, 400, 500, 600, 800, 1000, 1500, 2000, 2500],
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


def VetoMuons(df):
    df = df.Define("Muon_veto",
                   "Muon_standalonePt > 15 && Muon_highPurity && Muon_standaloneNumberOfValidHits >= 1 && Muon_looseId && abs(Muon_dxybs) < 0.05"
                   )

    # df = df.Define("Muon_vetoSelection", """
    #                     ROOT::VecOps::RVec<int> mask;
    #                     for (size_t i = 0; i < Muon_veto.size(); ++i) {
    #                         if (Muon_veto[i] == 1) mask.push_back(1);
    #                     }
    #                     return mask;
    #                     """)
    
    
    return df

def GoodMuons(df):
    df = df.Define("Muon_good", "Muon_pt > 26 && abs(Muon_eta) < 2.4")

    # df = df.Define("Muon_goodSelection", """
    #                     ROOT::VecOps::RVec<int> mask;
    #                     for (size_t i = 0; i < Muon_good.size(); ++i) {
    #                         if (Muon_good[i] == 1) mask.push_back(1);
    #                     }
    #                     return mask;
    #                     """)
    
    return df


def diMuonSelection(df):
    df = df.Filter("nMuon == 2")
    df = df.Filter("Muon_veto[0] == 1 && Muon_veto[1] == 1 && Muon_good[0] == 1 && Muon_good[1] == 1")
    df = df.Filter("Muon_charge[0] * Muon_charge[1] < 0")
    
    return df

if trigger == 'SingleMuon':
    df = VetoMuons(df)
    df = GoodMuons(df)
    df = diMuonSelection(df)


# df.Display(["Muon_veto", "Muon_vetoSelection", "Muon_good", "Muon_goodSelection", "Muon_charge"], 20).Print()

# df.Display(["Muon_veto", "Muon_good", "Muon_charge"], 20).Print()


# arrays = df.AsNumpy(["PFCands_pt"])
# print(f"Number of events in the dataframe: {arrays}")
# for i, event_pt in enumerate(arrays["PFCands_pt"][:2]):  # first 2 events
#     print(f"Event {i}: {event_pt}")
# all_pt = np.concatenate(arrays["PFCands_pt"])
# print(all_pt[:20])  # first 20 PFCands




df = df.Define("PFCands_vertexRefUnique",
                """
                std::set<int> sorted_unique(PFCands_vertexRef.begin(), PFCands_vertexRef.end());
                return ROOT::VecOps::RVec<int>(sorted_unique.begin(), sorted_unique.end());
                """
                )

df = df.Define("PFCands_vertexRefRandom",
                """
                if (PFCands_vertexRefUnique.size() == 0) return -1;
                return PFCands_vertexRefUnique[gRandom->Integer(PFCands_vertexRefUnique.size())];
                """
                )

# df.Display(["PFCands_vertexRefUnique", "PFCands_vertexRefRandom"], 20).Print()


def PFCandidateSelection(df, PFCands_obs, eleccharge = -1):

    df = df.Define("PFSelection",
                    f"""
                    ROOT::VecOps::Where(
                        (PFCands_charge != {eleccharge}) &&
                        (PFCands_vertexRef == PFCands_vertexRefRandom) &&
                        ((PFCands_pvAssocQuality == 6) || (PFCands_pvAssocQuality == 7)),
                        {PFCands_obs},
                        -999.f
                    )
                    """
                )
    df = df.Filter("ROOT::VecOps::Sum(PFSelection != -999.f) >= 2")

    return df




# df = PFCandidateSelection(df, "PFCands_pt", -1)

# df.Display(["PFSelection"], 10).Print()





for groupvar, grouplabel in variables.items():
    for var, label in grouplabel.items():

        # values_list = []

        # total_pf_cands = 0
        # selected_pf_cands = 0

        # total_events = df.GetEntries()
        # print(f"Total number of events in the file: {total_events}")

        # selected_events = 0
        # selected_events += 1

        # Assuming pt is always available for counting total PF candidates
        # total_pf_cands += len(getattr(events, "PFCands_pt"))  
        
        df = PFCandidateSelection(df, f"PFCands_{var}", -1)

        bins = binning[var] if len(binning[var]) == 3 else [len(binning[var]) - 1, binning[var][0], binning[var][-1]]

        h = df.Histo1D((f"PFCands_{var}", f"; {label}; Number of PF Candidates per Unit", bins[0], bins[1], bins[2]), f"PFCands_{var}")

        hist = h.GetValue()
        hist.Scale(1.0, "width")
        hist.SetStats(0)

        c = ROOT.TCanvas("c")
        hist.Draw("hist")
        hist.SetLineColor(ROOT.kViolet-6)
        hist.SetLineWidth(2)

        c.SaveAs(f"PFCands_{var}.pdf")

        c.Close()
        











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