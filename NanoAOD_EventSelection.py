import argparse
import array
import ROOT
import glob
import os
import csv

ROOT.gStyle.SetOptStat(0)


FILE_NAMES_SINGLEMUON = glob.glob("/eos/user/z/zoghafoo/crabsubmission_files/SingleMuon/*/*/*/*.root")
print(f"\nNumber of SingleMuon files: {len(FILE_NAMES_SINGLEMUON)}\n")

FILE_NAMES_ZEROBIAS = glob.glob("/eos/user/z/zoghafoo/crabsubmission_files/ZeroBias/NanoV9Run2016FDataPostVFP_MinBias_02052026/260502_160901/*/*.root")
print(f"Number of ZeroBias files: {len(FILE_NAMES_ZEROBIAS)}\n")



FILE_NAMES_MCDYJETS = [
    "/home/z/zoghafoo/CMSSW_10_6_26/src/Configuration/WMassNanoProduction/NanoV9MCPostVFP_PF_DYJetsToMuMu_100000Events.root",
]

FILE_NAMES_MCZEROBIAS = glob.glob("/eos/user/z/zoghafoo/crabsubmission_files/MC_MinBias/NanoV9MCPostVFP_ZeroBias_02052026/*/*/*.root")
print(f"Number of MC_ZeroBias files: {len(FILE_NAMES_MCZEROBIAS)}\n")


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
    df_SingleMuon = ROOT.RDataFrame("Events", list(FILE_NAMES_SINGLEMUON))
    df_MinBias = ROOT.RDataFrame("Events", list(FILE_NAMES_ZEROBIAS))
    df_MCDYJets = ROOT.RDataFrame("Events", list(FILE_NAMES_MCDYJETS))
    df_MCMinBias = ROOT.RDataFrame("Events", list(FILE_NAMES_MCZEROBIAS))

    if maxevents is not None:
        print(f"Processing only the first {maxevents} Events from each file.")
        df_SingleMuon = df_SingleMuon.Range(maxevents)
        df_MinBias = df_MinBias.Range(maxevents)
        df_MCDYJets = df_MCDYJets.Range(maxevents)
        df_MCMinBias = df_MCMinBias.Range(maxevents)

    return df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias


def PrintDatasetCounts(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias):
    total_events_SingleMuon= df_SingleMuon.Count().GetValue()
    total_events_MinBias = df_MinBias.Count().GetValue()
    total_events_MCDYJets = df_MCDYJets.Count().GetValue()
    total_events_MCMinBias = df_MCMinBias.Count().GetValue()
    print(f"\nTotal number of Events in SingleMuon file: {total_events_SingleMuon}")
    print(f"Total number of Events in MinBias file: {total_events_MinBias}")
    print(f"Total number of Events in MCDYJets file: {total_events_MCDYJets}")
    print(f"Total number of Events in MCMinBias file: {total_events_MCMinBias}\n")

    total_PFCands_SingleMuon= df_SingleMuon.Sum("nPFCands").GetValue()
    total_PFCands_MinBias = df_MinBias.Sum("nPFCands").GetValue()
    total_PFCands_MCDYJets = df_MCDYJets.Sum("nPFCands").GetValue()
    total_PFCands_MCMinBias = df_MCMinBias.Sum("nPFCands").GetValue()
    print(f"\nTotal number of PFCands in SingleMuon file: {total_PFCands_SingleMuon}")
    print(f"Total number of PFCands in MinBias file: {total_PFCands_MinBias}")
    print(f"Total number of PFCands in MCDYJets file: {total_PFCands_MCDYJets}")
    print(f"Total number of PFCands in MCMinBias file: {total_PFCands_MCMinBias}\n")

    return {
        "total_events_SingleMuon": total_events_SingleMuon,
        "total_events_MinBias": total_events_MinBias,
        "total_events_MCDYJets": total_events_MCDYJets,
        "total_events_MCMinBias": total_events_MCMinBias,
        "total_PFCands_SingleMuon": total_PFCands_SingleMuon,
        "total_PFCands_MinBias": total_PFCands_MinBias,
        "total_PFCands_MCDYJets": total_PFCands_MCDYJets,
        "total_PFCands_MCMinBias": total_PFCands_MCMinBias,
    }


def SaveCountsToTXT(counts_dict, out_dir="selEvents", filename="totalEvents.txt"):
    out_dir = os.path.expanduser(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    filepath = os.path.join(out_dir, filename)

    header = "\t".join(["", "SingleMuon", "MinBias", "MCDYJets", "MCMinBias"]) + "\n"
    events_row = "\t".join([
        "total_events",
        str(counts_dict.get("total_events_SingleMuon", "")),
        str(counts_dict.get("total_events_MinBias", "")),
        str(counts_dict.get("total_events_MCDYJets", "")),
        str(counts_dict.get("total_events_MCMinBias", "")),
    ]) + "\n"
    pfcands_row = "\t".join([
        "total_PFCands",
        str(counts_dict.get("total_PFCands_SingleMuon", "")),
        str(counts_dict.get("total_PFCands_MinBias", "")),
        str(counts_dict.get("total_PFCands_MCDYJets", "")),
        str(counts_dict.get("total_PFCands_MCMinBias", "")),
    ]) + "\n"

    with open(filepath, "w") as f:
        f.write(header)
        f.write(events_row)
        f.write(pfcands_row)

    print(f"Saved dataset counts (txt) to {filepath}\n")
    return filepath


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


def PVSelection(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias):
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
    df_MCMinBias = df_MCMinBias.Define(
        "PFCands_vertexRefUnique",
        """
        std::set<int> sorted_unique(PFCands_vertexRef.begin(), PFCands_vertexRef.end());
        return ROOT::VecOps::RVec<int>(sorted_unique.begin(), sorted_unique.end());
        """,
    )
    df_MCMinBias = df_MCMinBias.Define(
        "PFCands_vertexRefRandom",
        """
        if (PFCands_vertexRefUnique.size() == 0) return -1;
        return PFCands_vertexRefUnique[gRandom->Integer(PFCands_vertexRefUnique.size())];
        """,
    )

    return df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias


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

def ObservablesCalculation(df):
    df = df.Define("PFSelection_PFCands_pt", "Take(PFCands_pt, PFSelection_idx)")
    df = df.Define("PFSelection_PFCands_eta", "Take(PFCands_eta, PFSelection_idx)")
    df = df.Define("PFSelection_PFCands_phi", "Take(PFCands_phi, PFSelection_idx)")
    df = df.Define("PFSelection_PFCands_pvAssocQuality", "Take(PFCands_pvAssocQuality, PFSelection_idx)")
    df = df.Define("PFSelection_PFCands_InvariantMass", "PFCands_InvariantMass")
    df = df.Define("PFSelection_nPFCands", "PFSelection_idx.size()")

    exprHt = "ROOT::VecOps::Sum(Take(PFCands_pt, PFSelection_idx))"
    df = df.Define("PFSelection_PFCands_Ht", exprHt)

    exprPt2sum = "ROOT::VecOps::Sum(Take(PFCands_pt * PFCands_pt, PFSelection_idx))"
    df = df.Define("PFSelection_PFCands_Pt2sum", exprPt2sum)

    exprPsum = "ROOT::VecOps::Sum(Take(PFCands_p, PFSelection_idx))"
    df = df.Define("PFSelection_PFCands_Psum", exprPsum)

    exprP2sum = "ROOT::VecOps::Sum(Take(PFCands_p * PFCands_p, PFSelection_idx))"
    df = df.Define("PFSelection_PFCands_P2sum", exprP2sum)

    return df


def SaveSelectedEvents(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias, out_path=""):

    
    variables_list_MinBias = [f"PFSelection_{var}" for var in VARIABLES.keys()]
    variables_list_SingleMuon = ["diMuon_pT"] + variables_list_MinBias


    df_SingleMuon.Snapshot("Events", f"{out_path}/Data_SingleMuon_SelectedEvents.root", variables_list_SingleMuon)
    df_MinBias.Snapshot("Events", f"{out_path}/Data_MinBias_SelectedEvents.root", variables_list_MinBias)
    df_MCDYJets.Snapshot("Events", f"{out_path}/MC_DYJets_SelectedEvents.root", variables_list_SingleMuon)
    df_MCMinBias.Snapshot("Events", f"{out_path}/MC_MinBias_SelectedEvents.root", variables_list_MinBias)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Combined plotting driver for NanoAOD PF-candidate studies"
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
        "--output-suffix",
        default="",
        help="Optional suffix appended to output plot filenames",
    )
    parser.add_argument(
        "--output-dir",
        default="",
        help="Directory where output plots will be saved (default: 'plots')",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias = MakeDataframes(args.maxevents)

    SaveCountsToTXT(PrintDatasetCounts(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias), out_dir=args.output_dir)

    df_SingleMuon = VetoMuons(df_SingleMuon)
    df_SingleMuon = GoodMuons(df_SingleMuon)
    df_SingleMuon = DiMuonSelection(df_SingleMuon)

    df_MCDYJets = VetoMuons(df_MCDYJets)
    df_MCDYJets = GoodMuons(df_MCDYJets)
    df_MCDYJets = DiMuonSelection(df_MCDYJets)

    df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias = PVSelection(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias)
    df_SingleMuon = PFCandidateSelection(df_SingleMuon, args.charge)
    df_MinBias = PFCandidateSelection(df_MinBias, args.charge)
    df_MCDYJets = PFCandidateSelection(df_MCDYJets, args.charge)
    df_MCMinBias = PFCandidateSelection(df_MCMinBias, args.charge)



    df_SingleMuon = addInvariantMass(df_SingleMuon)
    df_MinBias = addInvariantMass(df_MinBias)
    df_MCDYJets = addInvariantMass(df_MCDYJets)
    df_MCMinBias = addInvariantMass(df_MCMinBias)

    df_SingleMuon = ObservablesCalculation(df_SingleMuon)
    df_MinBias = ObservablesCalculation(df_MinBias)
    df_MCDYJets = ObservablesCalculation(df_MCDYJets)
    df_MCMinBias = ObservablesCalculation(df_MCMinBias)

    SaveSelectedEvents(df_SingleMuon, df_MinBias, df_MCDYJets, df_MCMinBias, out_path=args.output_dir)


    if args.no_plot:
        print("Selections finished. Plotting disabled by --no-plot.")
        return


if __name__ == "__main__":
    main()
