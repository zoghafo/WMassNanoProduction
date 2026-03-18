import ROOT
import sys
import matplotlib as mat
import matplotlib.pyplot as plt
import numpy as np
import os
import random

from wremnants import muon_selections


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

variables = {
    'predefined_variables': {
        # 'pt': '$p_\\mathrm{T}\\,\\mathrm{[GeV]}$',
        # 'eta': '$\\eta$',
        # 'phi': '$\\phi$',
        # 'mass': '$m\\,\\mathrm{[GeV]}$',
        # 'pvAssocQuality': 'PV association quality',
        # 'N': 'Number of PF candidates',
        },
    'calculated_variables': {
        'Ht': '$H_\\mathrm{T}\\,\\mathrm{[GeV]}$',
        # 'Pt2sum': '$\\sum_\mathrm{cands} p^2_{T}\\,\\mathrm{[GeV^2]}$',
        # 'Psum': '$\\sum_\mathrm{cands} p\\,\\mathrm{[GeV]}$',
        # 'P2sum': '$\\sum_\mathrm{cands} p^2\\,\\mathrm{[GeV^2]}$',
    },
}

binning = {
    # 'pt': [50, 0, 100],
    # 'eta': [50, -2.5, 2.5],
    # 'phi': [50, -3.14, 3.14],
    # 'mass': [0,2,5,10,15,20,25,35,45,60,80,120,160,200,300,400],
    # 'mass': [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3],
    # 'pvAssocQuality': [8, -0.5, 7.5],
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





for eleccharge in [
    'Charged',
    # 'All',
    # 'Neutral'
    ]:
    charged_only = (eleccharge == 'Charged')
    neutral_only = (eleccharge == 'Neutral')
    output_suffix = eleccharge

    for groupvar, grouplabel in variables.items():
        for var, label in grouplabel.items():

            values_list = []

            total_pf_cands = 0
            selected_pf_cands = 0

            total_events = events.GetEntries()
            selected_events = 0


            # for entryNum in range(events.GetEntries()):
            for entryNum in range(NEvents):
                events.GetEntry(entryNum)

                corrected_pt = getattr(events, "Muon_cvhPt")
                print(f"Entry {entryNum}: correctedPt = {corrected_pt}")

                

                if trigger == 'SingleMuon':
                    # Cuts for Global Muons to be defined as Veto Muons

                    standalone_pt = list(getattr(events, "Muon_standalonePt"))
                    standalone_eta = list(getattr(events, "Muon_standaloneEta"))
                    standalone_phi = list(getattr(events, "Muon_standalonePhi"))

                    corrected_pt = list(getattr(events, "Muon_cvhPt"))
                    corrected_eta = list(getattr(events, "Muon_cvhEta"))
                    corrected_phi = list(getattr(events, "Muon_cvhPhi"))

                    # standalone_pt > 15 GeV
                    if not any(pt > 15 for pt in standalone_pt):
                        continue

                    # inner and outer tracks must be matched within a cone size of DeltaR = 0.3
                    if not any(v < 0.9 for v in vectdeltaR2(standalone_eta, standalone_phi, corrected_eta, corrected_phi)):
                        continue

                    # inner track must pass the high-purity flag
                    highPurity = list(getattr(events, "Muon_highPurity"))
                    if not any(highPurity):
                        continue

                    # the standalone track must have at least one valid hit
                    standaloneNumberOfValidHits = list(getattr(events, "Muon_standaloneNumberOfValidHits"))
                    if not any(n >= 1 for n in standaloneNumberOfValidHits):
                        continue

                    # p_T > 15 GeV and |eta| < 2.5 cuts on the standalone muon






                    

                    # for impactparam in getattr(events, "Muon_dxybs"):
                    #     if abs(impactparam) > 0.05:
                    #         continue
                    # for looseId in getattr(events, "Muon_looseId"):
                    #     if not looseId:
                    #         continue
                    # for isGlobal in getattr(events, "Muon_isGlobal"):
                    #     if not isGlobal:
                    #         continue
                    
                    # for tracker in getattr(events, "Muon_isTracker"): # select tracker muons, similar to mZ_dilepton.py
                    #     if not tracker:
                    #         continue
                    # for highPurity in getattr(events, "Muon_highPurity"):
                    #     if not highPurity:
                    #         continue
                    # for innerTrackerOriginalAlgo in getattr(events, "Muon_innerTrackOriginalAlgo"):
                    #     if innerTrackerOriginalAlgo == 13 or innerTrackerOriginalAlgo == 14:
                    #         continue
                    # for standaloneNumberOfValidHits in getattr(events, "Muon_standaloneNumberOfValidHits"):
                    #     if standaloneNumberOfValidHits < 0:
                    #         continue

                    # pT cut
                    muon_pts = list(getattr(events, "Muon_pt"))
                    # print(len(muon_pts))
                    # if not any(pt > 15 for pt in muon_pts):
                    #     continue
                    # eta cut
                    muon_etas = list(getattr(events, "Muon_eta"))
                    # print(len(muon_etas))
                    # if not any(abs(eta) < 2.5 for eta in muon_etas):
                    #     continue



                selected_events += 1
                # print(selected_events)
                

                total_pf_cands += len(getattr(events, "PFCands_pt"))  # Assuming pt is always available for counting total PF candidates 
                # print(f"{len(getattr(events, 'PFCands_pt'))} PF candidates in entry {entryNum}. Total so far: {total_pf_cands}")


                charges = list(getattr(events, "PFCands_charge"))
                vertexRef = list(getattr(events, "PFCands_vertexRef"))
                pvAssociationQuality = list(getattr(events, "PFCands_pvAssocQuality"))

                vertexRef_unique = []
                check = 0

                for i in vertexRef:
                    if i not in vertexRef_unique:
                        vertexRef_unique.append(i)

                vertexRef_random = random.choice(vertexRef_unique) if vertexRef_unique else print(f"Warning: No unique vertexRef found for entry {entryNum}.")

                # for i in range(len(vertexRef)):
                #     if vertexRef[i] == vertexRef_random:
                #         check += 1

                # print(f"Total Number of PF candidates in event {entryNum}: {len(getattr(events, 'PFCands_pt'))}")

                # print(f"Number of different vertices in the event: {len(vertexRef_unique)}")

                # print(f"Number of PF candidates associated with the randomly selected vertex (vertexRef_random = {vertexRef_random}): {check}")



                if groupvar == 'predefined_variables':

                    if var != 'N':
                        values = list(getattr(events, f"PFCands_{var}"))

                        
                        # to check if the length of values and charges are the same, if not, we just take the values without checking the charge
                        if len(values) == len(charges) and len(charges) == len(pvAssociationQuality):
                            if charged_only:

                                new_vals = [v for v, q, ref, pv in zip(values, charges, vertexRef, pvAssociationQuality) if q != 0 and ref == vertexRef_random and pv in (6, 7)]
                                # cut to have at least two tracks in the event
                                if len(new_vals) < 2:
                                    # print(f"\n\n\nSkipping entry {entryNum} because it has less than 2 charged tracks after selection.\n\n\n")
                                    continue
                                else:
                                    values_list.extend(new_vals)
                                    selected_pf_cands += len(new_vals)
                                
                            elif neutral_only:

                                new_vals = [v for v, q, ref, pv in zip(values, charges, vertexRef, pvAssociationQuality) if q == 0 and ref == vertexRef_random and pv in (6, 7)]
                                # cut to have at least two tracks in the event
                                if len(new_vals) < 2:
                                    continue
                                else:   
                                    values_list.extend(new_vals)
                                    selected_pf_cands += len(new_vals)
                            else:
                                values_list.extend(values)
                                selected_pf_cands += len(values)
                        else:
                            print(f"Warning: Length of values and charges do not match for entry {entryNum}.")
                            continue



                    elif var == 'N':  # var == 'Ncharged'
                        values = 0
                        if len(charges) > 0:
                            if charged_only:
                                new_vals = [1 for q, ref, pv in zip(charges, vertexRef, pvAssociationQuality) if q != 0 and ref == vertexRef_random and pv in (6, 7)]
                                # cut to have at least two tracks in the event
                                if len(new_vals) < 2:
                                    # print(f"\n\n\nSkipping entry {entryNum} because it has less than 2 charged tracks after selection.\n\n\n")
                                    continue
                                else:
                                    values_list.append(len(new_vals))
                                    selected_pf_cands += len(new_vals)
                            elif neutral_only:
                                new_vals = [1 for q, ref, pv in zip(charges, vertexRef, pvAssociationQuality) if q == 0 and ref == vertexRef_random and pv in (6, 7)]
                                if len(new_vals) < 2:
                                    continue
                                else:
                                    values_list.append(len(new_vals))
                                    selected_pf_cands += len(new_vals)
                            else:
                                values_list.append(len(new_vals))
                                selected_pf_cands += len(new_vals)
                        else:
                            print(f"Warning: No charge information available for entry {entryNum}.")
                            continue

                elif groupvar == 'calculated_variables':
            
                    if var == 'Ht':
                        values = list(getattr(events, "PFCands_pt"))

                        if len(values) == len(charges) and len(charges) == len(pvAssociationQuality):
                            if charged_only:

                                new_vals = [pt for pt, q, ref, pv in zip(values, charges, vertexRef, pvAssociationQuality) if q != 0 and ref == vertexRef_random and pv in (6, 7)]
                                # cut to have at least two tracks in the event
                                if len(new_vals) < 2:
                                    # print(f"\n\n\nSkipping entry {entryNum} because it has less than 2 charged tracks after selection.\n\n\n")
                                    continue
                                else:
                                    Ht = sum(new_vals)
                                    values_list.append(Ht)
                                    selected_pf_cands += len(new_vals)
                            elif neutral_only:
                                new_vals = [pt for pt, q, ref, pv in zip(values, charges, vertexRef, pvAssociationQuality) if q == 0 and ref == vertexRef_random and pv in (6, 7)]
                                # cut to have at least two tracks in the event
                                if len(new_vals) < 2:
                                    # print(f"\n\n\nSkipping entry {entryNum} because it has less than 2 charged tracks after selection.\n\n\n")
                                    continue
                                else:
                                    Ht = sum(new_vals)
                                    values_list.append(Ht)
                                    selected_pf_cands += len(new_vals)
                            else:
                                Ht = sum(values)
                                values_list.append(Ht)
                                selected_pf_cands += len(values)
                        else:
                            print(f"Warning: Length of PFCands_pt and charges do not match for entry {entryNum}.")
                            continue


                    elif var == 'Psum':
                        values = list(getattr(events, "PFCands_p"))

                        if len(values) == len(charges) and len(charges) == len(pvAssociationQuality):
                            if charged_only:

                                new_vals = [p for p, q, ref, pv in zip(values, charges, vertexRef, pvAssociationQuality) if q != 0 and ref == vertexRef_random and pv in (6, 7)]
                                # cut to have at least two tracks in the event
                                if len(new_vals) < 2:
                                    # print(f"\n\n\nSkipping entry {entryNum} because it has less than 2 charged tracks after selection.\n\n\n")
                                    continue
                                else:
                                    Psum = sum(new_vals)
                                    values_list.append(Psum)
                                    selected_pf_cands += len(new_vals)
                            elif neutral_only:
                                new_vals = [p for p, q, ref, pv in zip(values, charges, vertexRef, pvAssociationQuality) if q == 0 and ref == vertexRef_random and pv in (6, 7)]
                                # cut to have at least two tracks in the event
                                if len(new_vals) < 2:
                                    # print(f"\n\n\nSkipping entry {entryNum} because it has less than 2 charged tracks after selection.\n\n\n")
                                    continue
                                else:
                                    Psum = sum(new_vals)
                                    values_list.append(Psum)
                                    selected_pf_cands += len(new_vals)
                            else:
                                Psum = sum(values)
                                values_list.append(Psum)
                                selected_pf_cands += len(values)
                        else:
                            print(f"Warning: Length of PFCands_p and charges do not match for entry {entryNum}.")
                            continue


                    elif var == 'P2sum':
                        values = list(getattr(events, "PFCands_p"))

                        if len(values) == len(charges) and len(charges) == len(pvAssociationQuality):
                            if charged_only:
                                new_vals = [p for p, q, ref, pv in zip(values, charges, vertexRef, pvAssociationQuality) if q != 0 and ref == vertexRef_random and pv in (6, 7)]
                                # cut to have at least two tracks in the event
                                if len(new_vals) < 2:
                                    # print(f"\n\n\nSkipping entry {entryNum} because it has less than 2 charged tracks after selection.\n\n\n")
                                    continue
                                else:
                                    P2sum = sum(p*p for p in new_vals)
                                    values_list.append(P2sum)
                                    selected_pf_cands += len(new_vals)
                            elif neutral_only:
                                new_vals = [p for p, q, ref, pv in zip(values, charges, vertexRef, pvAssociationQuality) if q == 0 and ref == vertexRef_random and pv in (6, 7)]
                                # cut to have at least two tracks in the event
                                if len(new_vals) < 2:
                                    # print(f"\n\n\nSkipping entry {entryNum} because it has less than 2 charged tracks after selection.\n\n\n")
                                    continue
                                else:
                                    P2sum = sum(p*p for p in new_vals)
                                    values_list.append(P2sum)
                                    selected_pf_cands += len(new_vals)
                            else:
                                P2sum = sum(p*p for p in values)
                                values_list.append(P2sum)
                                selected_pf_cands += len(values)
                        else:
                            print(f"Warning: Length of PFCands_p and charges do not match for entry {entryNum}.")
                            continue

                    elif var == 'Pt2sum':
                        values = list(getattr(events, "PFCands_pt"))

                        if len(values) == len(charges) and len(charges) == len(pvAssociationQuality):
                            if charged_only:
                                new_vals = [pt for pt, q, ref, pv in zip(values, charges, vertexRef, pvAssociationQuality) if q != 0 and ref == vertexRef_random and pv in (6, 7)]
                                if len(new_vals) < 2:
                                    # print(f"\n\n\nSkipping entry {entryNum} because it has less than 2 charged tracks after selection.\n\n\n")
                                    continue
                                else:
                                    Pt2sum = sum(pt*pt for pt in new_vals)
                                    values_list.append(Pt2sum)
                                    selected_pf_cands += len(new_vals)
                            elif neutral_only:
                                new_vals = [pt for pt, q, ref, pv in zip(values, charges, vertexRef, pvAssociationQuality) if q == 0 and ref == vertexRef_random and pv in (6, 7)]
                                if len(new_vals) < 2:
                                    # print(f"\n\n\nSkipping entry {entryNum} because it has less than 2 charged tracks after selection.\n\n\n")
                                    continue
                                else:
                                    Pt2sum = sum(pt*pt for pt in new_vals)
                                    values_list.append(Pt2sum)
                                    selected_pf_cands += len(new_vals)
                            else:
                                Pt2sum = sum(pt*pt for pt in values)
                                values_list.append(Pt2sum)
                                selected_pf_cands += len(values)
                        else:
                            print(f"Warning: Length of PFCands_pt and charges do not match for entry {entryNum}.")
                            continue


            figure = plt.figure(figsize=(9, 6))
            bins = binning[var] if var in binning.keys() else None
            if bins is not None:
                bin_widths = np.diff(bins)
                bin_indices = np.digitize(values_list, bins) - 1

                weights = [
                    1.0 / bin_widths[i] if 0 <= i < len(bin_widths) else 0
                    for i in bin_indices
                ]
            else:
                weights = None

            plt.hist(
                values_list,
                bins=bins,
                weights=weights,
                histtype='stepfilled',
                color='purple',
                linewidth=2,
                density=True if var == 'N' else False,
                label=f'{eleccharge} PFCands',
                zorder=6
            )
            # plt.hist(values_list, bins=binning[var] if var in binning.keys() else None, histtype='stepfilled', color='purple', linewidth=2, label=f'{eleccharge} PFCands', density=True if var == 'N' and var == 'Ht' else False, zorder=6)
            plt.legend(loc='upper right', frameon=True, fontsize=10, title=f"{trigger} Trigger\n\n{selected_events} selected Events\n{(selected_events/total_events)*100:.2f}% efficiency Events\n{selected_pf_cands} selected PF Candidates\n{(selected_pf_cands/total_pf_cands)*100:.2f}% efficiency PF Candidates", facecolor='white')
            leg = plt.gca().get_legend()
            leg._legend_box.align = "left"
            plt.grid(linestyle='-', alpha=0.7)
            plt.xlabel(label)
            plt.ylabel("Entries per Unit" if var !='N' else fr"$\frac{{1}}{{N}}\frac{{dN}}{{dN_\mathrm{{charged}}}}$")
            # if var != 'N' and var != 'Ht' and var != 'P2sum':
            #     plt.ylim(0, max(plt.ylim())*1.5)
            plt.yscale('log' if var == 'N' or var == 'P2sum' or var == 'Pt2sum' or var == 'Psum' or var == 'Ht' else 'linear')
            # plt.savefig(f'/eos/user/z/zoghafoo/www/PF/{trigger}/PFCands_{trigger}_{var}{output_suffix}.pdf')
            # plt.savefig(f'/home/z/zoghafoo/CMSSW_10_6_26/src/Configuration/WMassNanoProduction/plots/{trigger}/PFCands_{trigger}_{var}{output_suffix}_100000EventsPVSelectionPTEtaCut.pdf')
            # plt.savefig(f'PFCandsTEST_{trigger}_{var}{output_suffix}_{NEvents}EventsPVSelection.pdf')
            print(f"Plot for variable '{var}' saved as '/eos/user/z/zoghafoo/www/PF/{trigger}/PFCands_{trigger}_{var}{output_suffix}.pdf'.")
            plt.clf()

file.Close()