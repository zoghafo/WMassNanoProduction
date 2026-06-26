import argparse
import array
import ROOT
import glob
import os
import csv

ROOT.gStyle.SetOptStat(0)


FILE_NAMES_SINGLEMUON = glob.glob("/pnfs/psi.ch/cms/trivcat/store/user/zoghafoo/crabsubmission_files/SingleMuon/NanoV9Run2016*DataPostVFP*/*/*/*.root")
print(f"\nNumber of SingleMuon files: {len(FILE_NAMES_SINGLEMUON)}\n")

FILE_NAMES_ZEROBIAS = glob.glob("/pnfs/psi.ch/cms/trivcat/store/user/zoghafoo/crabsubmission_files/ZeroBias/NanoV9Run2016*DataPostVFP_MinBias*/*/*/*.root")
print(f"Number of ZeroBias files: {len(FILE_NAMES_ZEROBIAS)}\n")



FILE_NAMES_MCDY = glob.glob("/pnfs/psi.ch/cms/trivcat/store/user/zoghafoo/crabsubmission_files/DYJetsToMuMu_H2ErratumFix_TuneCP5_13TeV-powhegMiNNLO-pythia8-photos/NanoV9MCPostVFP_DY_18052026/260518_072416/*/*.root")
print(f"Number of MC_DYJets files: {len(FILE_NAMES_MCDY)}\n")

FILE_NAMES_MCZEROBIAS = glob.glob("/pnfs/psi.ch/cms/trivcat/store/user/zoghafoo/crabsubmission_files/MinBias_TuneCP5_13TeV-pythia8/NanoV9MCPostVFP_ZeroBias_18052026/260518_072813/*/*.root")
print(f"Number of MC_ZeroBias files: {len(FILE_NAMES_MCZEROBIAS)}\n")


DATASET_FILES = {
    "SingleMuon": FILE_NAMES_SINGLEMUON,
    "MinBias": FILE_NAMES_ZEROBIAS,
    "MCDY": FILE_NAMES_MCDY,
    "MCMinBias": FILE_NAMES_MCZEROBIAS,
}


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


def MakeDataframes(dataset="all", maxevents=None):
    if dataset == "all":
        selected_datasets = DATASET_FILES.keys()
    else:
        selected_datasets = [dataset]

    dataframes = {}
    for name in selected_datasets:
        dataframes[name] = ROOT.RDataFrame("Events", list(DATASET_FILES[name]))
        if maxevents is not None:
            dataframes[name] = dataframes[name].Range(maxevents)

    if maxevents is not None:
        print(f"Processing only the first {maxevents} Events from each selected dataset.")

    return dataframes


def PrintDatasetCounts(dataframes):
    counts = {}

    for dataset_name, dataframe in dataframes.items():

        total_events = dataframe.Count().GetValue()
        total_PFcands = dataframe.Sum("nPFCands").GetValue()

        print(f"\nTotal number of Events in {dataset_name} file: {total_events}")
        print(f"Total number of PFCands in {dataset_name} file: {total_PFcands}")

        counts[f"total_events_{dataset_name}"] = total_events
        counts[f"total_PFCands_{dataset_name}"] = total_PFcands

    print()
    
    return counts


def SaveCountsToTXT(counts_dict, dataset, out_dir, output_suffix=""):
    out_dir = os.path.expanduser(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    filepath = os.path.join(out_dir, f"{dataset}_TotalEvents_{output_suffix}.txt")

    dataset_names = sorted({key.rsplit("_", 1)[-1] for key in counts_dict if key.startswith("total_events_")})
    header = "\t".join([""] + dataset_names) + "\n"
    events_row = "\t".join(["total_events"] + [str(counts_dict.get(f"total_events_{name}", "")) for name in dataset_names]) + "\n"
    pfcands_row = "\t".join(["total_PFCands"] + [str(counts_dict.get(f"total_PFCands_{name}", "")) for name in dataset_names]) + "\n"

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
    df = df.Define("DiMuon_pt", "pow(pow(Muon_pt[Muon_idx[0]] * cos(Muon_phi[Muon_idx[0]]) + Muon_pt[Muon_idx[1]] * cos(Muon_phi[Muon_idx[1]]), 2) + pow(Muon_pt[Muon_idx[0]] * sin(Muon_phi[Muon_idx[0]]) + Muon_pt[Muon_idx[1]] * sin(Muon_phi[Muon_idx[1]]), 2), 0.5)")
    return df


def PVSelection(df, dataset_name):
    df = df.Define(
        "PFCands_vertexRefUnique",
        """
        std::set<int> sorted_unique(PFCands_vertexRef.begin(), PFCands_vertexRef.end());
        return ROOT::VecOps::RVec<int>(sorted_unique.begin(), sorted_unique.end());
        """,
    )

    if dataset_name in {"SingleMuon", "MCDY"}:
        df = df.Define(
            "PFCands_vertexRefRandom",
            """
            if (PFCands_vertexRefUnique.size() == 0) return -1;
            return PFCands_vertexRefUnique[0];
            """,
        )
    else:
        df = df.Define(
            "PFCands_vertexRefRandom",
            """
            if (PFCands_vertexRefUnique.size() == 0) return -1;
            return PFCands_vertexRefUnique[gRandom->Integer(PFCands_vertexRefUnique.size())];
            """,
        )

    return df


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

def addDiMuon4Vector(df, dataset):
    if dataset in {"SingleMuon", "MCDY"}:
        
        print(f"Calculating DiMuon_4Vector for dataset {dataset}...")
        
        df = df.Define(
            "DiMuon_P",
            """
            TLorentzVector muon1, muon2;
            muon1.SetPtEtaPhiM(Muon_pt[Muon_idx[0]], Muon_eta[Muon_idx[0]], Muon_phi[Muon_idx[0]], Muon_mass[Muon_idx[0]]);
            muon2.SetPtEtaPhiM(Muon_pt[Muon_idx[1]], Muon_eta[Muon_idx[1]], Muon_phi[Muon_idx[1]], Muon_mass[Muon_idx[1]]);
            TLorentzVector diMuonSystem = muon1 + muon2;
            return diMuonSystem;
            """
        )
        df = df.Define("DiMuon_Mass", "DiMuon_P.M()")
        df = df.Define("DiMuon_Rapidity", "DiMuon_P.Rapidity()")
        df = df.Define("DiMuon_xmaxll", "exp(DiMuon_Rapidity)*DiMuon_Mass/std::sqrt(13000*13000)")
        df = df.Define("DiMuon_xminll", "exp(-DiMuon_Rapidity)*DiMuon_Mass/std::sqrt(13000*13000)")
        df = df.Define("DiMuon_Eta", "DiMuon_P.Eta()")
        df = df.Define("DiMuon_Pt", "DiMuon_P.Pt()")
        df = df.Define("DiMuon_Phi", "DiMuon_P.Phi()")
        df = df.Define("DiMuon_E", "DiMuon_P.E()")

    else:
        print(f"Dataset {dataset} not SingleMuon or MCDY. Skipping DiMuon_4Vector calculation.")
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


def SaveSelectedEvents(df_SingleMuon, df_MinBias, df_MCDY, df_MCMinBias, out_path="", output_suffix=""):

    variables_list_MinBias = [f"PFSelection_{var}" for var in VARIABLES.keys()]
    variables_list_SingleMuon = ["DiMuon_pt"] + variables_list_MinBias + ["DiMuon_P", "DiMuon_Mass", "DiMuon_Rapidity", "DiMuon_xmaxll", "DiMuon_xminll", "DiMuon_Eta", "DiMuon_Pt", "DiMuon_Phi", "DiMuon_E"]


    df_SingleMuon.Snapshot("Events", f"{out_path}/Data_SingleMuon_SelectedEvents_{output_suffix}.root", variables_list_SingleMuon)
    df_MinBias.Snapshot("Events", f"{out_path}/Data_MinBias_SelectedEvents_{output_suffix}.root", variables_list_MinBias)
    df_MCDY.Snapshot("Events", f"{out_path}/MC_DY_SelectedEvents_{output_suffix}.root", variables_list_SingleMuon)
    df_MCMinBias.Snapshot("Events", f"{out_path}/MC_MinBias_SelectedEvents_{output_suffix}.root", variables_list_MinBias)

def SnapshotColumns(dataset_name):
    variables_list_minbias = [f"PFSelection_{var}" for var in VARIABLES.keys()]
    if dataset_name in {"SingleMuon", "MCDY"}:
        return ["DiMuon_pt"] + variables_list_minbias + ["DiMuon_P", "DiMuon_Mass", "DiMuon_Rapidity", "DiMuon_xmaxll", "DiMuon_xminll", "DiMuon_Eta", "DiMuon_Pt", "DiMuon_Phi", "DiMuon_E"]
    return variables_list_minbias


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
        "--no-selection",
        action="store_true",
        help="Print counts only",
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
        default="/pnfs/psi.ch/cms/trivcat/store/user/zoghafoo/crabsubmission_files/selEvents/",
        help="Directory where output plots will be saved (default: '/pnfs/psi.ch/cms/trivcat/store/user/zoghafoo/crabsubmission_files/selEvents/')",
    )
    parser.add_argument(
        "--dataset",
        default="all",
        choices=["all"] + sorted(DATASET_FILES.keys()),
        help="Process only one dataset instead of all four",
    )
    parser.add_argument(
        "--nthreads",
        type=int,
        default=1
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.nthreads > 1:
        if args.maxevents is not None:
            print("WARNING: --maxevents uses RDataFrame.Range(), which is incompatible with EnableImplicitMT.")
            print("Running single-threaded for this test job.")
        else:
            ROOT.ROOT.EnableImplicitMT(args.nthreads)
            print("Number of threads:", args.nthreads, "\n")


    print("Selected dataset:", args.dataset)
    print("Output directory:", args.output_dir, "\n")

    dataframes = MakeDataframes(args.dataset, args.maxevents)
    SaveCountsToTXT(PrintDatasetCounts(dataframes), args.dataset, args.output_dir, args.output_suffix)

    if args.no_selection:
        print("Selections skipped by --no-selection.")
        return

    processed_dataframes = {}
    for dataset_name, dataframe in dataframes.items():
        if dataset_name in {"SingleMuon", "MCDY"}:
            dataframe = VetoMuons(dataframe)
            dataframe = GoodMuons(dataframe)
            dataframe = DiMuonSelection(dataframe)
            dataframe = addDiMuon4Vector(dataframe, args.dataset)

        dataframe = PVSelection(dataframe, dataset_name)
        dataframe = PFCandidateSelection(dataframe, args.charge)
        dataframe = addInvariantMass(dataframe)
        dataframe = ObservablesCalculation(dataframe)
        processed_dataframes[dataset_name] = dataframe

    if args.dataset == "all":
        SaveSelectedEvents(
            processed_dataframes["SingleMuon"],
            processed_dataframes["MinBias"],
            processed_dataframes["MCDY"],
            processed_dataframes["MCMinBias"],
            out_path=args.output_dir,
            output_suffix=args.output_suffix,
        )
    else:
        dataset_name = args.dataset
        output_file = os.path.join(args.output_dir, f"{dataset_name}_SelectedEvents_{args.output_suffix}.root")
        processed_dataframes[dataset_name].Snapshot("Events", output_file, SnapshotColumns(dataset_name))


if __name__ == "__main__":
    main()
