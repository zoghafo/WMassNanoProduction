import argparse
import array
import ROOT
import glob
import os
import csv
import json
import sys
import types
import functools

# WRemnants (scripts/histmakers/mz_dilepton.py) for the muon calibration and the MC weights: run this script
# inside the WRemnants container, after "source /work/zoghafoo/WRemnants/setup.sh".
# WRemnants reads the command line when it is imported: give it only "--nThreads 1", the threads are set by this script
_argv = sys.argv
sys.argv = [_argv[0], "--nThreads", "1"]
from utilities import common, parsing
from wremnants.datasets.datagroups import Datagroups
_wrem_parser, _ = parsing.common_parser(Datagroups.analysisLabel("mz_dilepton.py"))
import narf
from wremnants import muon_calibration, muon_efficiencies_smooth, muon_prefiring, muon_selections, pileup, theory_corrections, theory_tools, vertex
WREM_ARGS = _wrem_parser.parse_args(["--nThreads", "1"])  # all WRemnants default options
sys.argv = _argv

ERA = WREM_ARGS.era
# WRemnants dataset names, used by WRemnants to choose the corrections (wremnants/datasets/datasetDict_2016PostVFP.py)
WREM_DATASETS = {
    "SingleMuon": types.SimpleNamespace(name="SingleMuon_2016PostVFP", is_data=True, group="Data"),
    "MCDY": types.SimpleNamespace(name="Zmumu_2016PostVFP", is_data=False, group="Zmumu"),
    "MCZtautau": types.SimpleNamespace(name="Ztautau_2016PostVFP", is_data=False, group="Ztautau"),
    "MCTTbar": types.SimpleNamespace(name="TTLeptonic_2016PostVFP", is_data=False, group="Top"),
    "MCMinBias": types.SimpleNamespace(name="MinBias", is_data=False, group="MinBias"),
}
# diboson samples, WRemnants group "Diboson" (datasetDict_2016PostVFP.py): dataset name: (WRemnants name, NanoAOD production)
DIBOSON_SAMPLES = {
    "MCWWTo2L2Nu": ("WWTo2L2Nu_2016PostVFP", "WWTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/NanoV9MCPostVFP_WWTo2L2Nu_10112026"),
    "MCWWTo1L1Nu2Q": ("WWTo1L1Nu2Q_2016PostVFP", "WWTo1L1Nu2Q_4f_TuneCP5_13TeV-amcatnloFXFX-pythia8/NanoV9MCPostVFP_WWTo1L1Nu2Q_10112026"),
    "MCWZTo3LNu": ("WZTo3LNu_2016PostVFP", "WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8/NanoV9MCPostVFP_WZTo3LNu_10112026"),
    "MCWZTo2Q2L": ("WZTo2Q2L_2016PostVFP", "WZTo2Q2L_mllmin4p0_TuneCP5_13TeV-amcatnloFXFX-pythia8/NanoV9MCPostVFP_WZTo2Q2L_10112026"),
    "MCWZTo1L1Nu2Q": ("WZTo1L1Nu2Q_2016PostVFP", "WZTo1L1Nu2Q_4f_TuneCP5_13TeV-amcatnloFXFX-pythia8/NanoV9MCPostVFP_WZTo1L1Nu2Q_10112026"),
    "MCZZTo2L2Nu": ("ZZTo2L2Nu_2016PostVFP", "ZZTo2L2Nu_TuneCP5_13TeV_powheg_pythia8/NanoV9MCPostVFP_ZZTo2L2Nu_10112026"),
    "MCZZTo2Q2L": ("ZZTo2Q2L_2016PostVFP", "ZZTo2Q2L_mllmin4p0_TuneCP5_13TeV-amcatnloFXFX-pythia8/NanoV9MCPostVFP_ZZTo2Q2L_10112026"),
}
for _name, (_wrem_name, _production) in DIBOSON_SAMPLES.items():
    WREM_DATASETS[_name] = types.SimpleNamespace(name=_wrem_name, is_data=False, group="Diboson")
# photon-induced samples, WRemnants group "PhotonInduced" (datasetDict_2016PostVFP.py): dataset name: (WRemnants name, NanoAOD production)
PHOTON_INDUCED_SAMPLES = {
    "MCGGToLL": ("GGToLL_2016PostVFP", "GGToLL_TuneCP5_13TeV-pythia8/NanoV9MCPostVFP_GGToLL_16112026"),
    "MCQGToDYQTo2L": ("QGToDYQTo2L_2016PostVFP", "QGToDYQTo2L_TuneCP5_13TeV-pythia8-photos/NanoV9MCPostVFP_QGToDYQTo2L_16112026"),
}
for _name, (_wrem_name, _production) in PHOTON_INDUCED_SAMPLES.items():
    WREM_DATASETS[_name] = types.SimpleNamespace(name=_wrem_name, is_data=False, group="PhotonInduced")
# single top samples, WRemnants group "Top" like ttbar (datasetDict_2016PostVFP.py): dataset name: (WRemnants name, NanoAOD production)
SINGLE_TOP_SAMPLES = {
    "MCSingleTschanLepDecays": ("SingleTschanLepDecays_2016PostVFP", "ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-amcatnlo-pythia8/NanoV9MCPostVFP_ST_s-channel_17112026"),
    "MCSingleTtWAntitop": ("SingleTtWAntitop_2016PostVFP", "ST_tW_antitop_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8/NanoV9MCPostVFP_ST_tW_antitop_17112026"),
    "MCSingleTtWTop": ("SingleTtWTop_2016PostVFP", "ST_tW_top_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8/NanoV9MCPostVFP_ST_tW_top_17112026"),
    "MCSingleTtchanAntitop": ("SingleTtchanAntitop_2016PostVFP", "ST_t-channel_antitop_5f_InclusiveDecays_TuneCP5_13TeV-powheg-pythia8/NanoV9MCPostVFP_ST_t-channel_antitop_17112026"),
    "MCSingleTtchanTop": ("SingleTtchanTop_2016PostVFP", "ST_t-channel_top_5f_InclusiveDecays_TuneCP5_13TeV-powheg-pythia8/NanoV9MCPostVFP_ST_t-channel_top_17112026"),
}
for _name, (_wrem_name, _production) in SINGLE_TOP_SAMPLES.items():
    WREM_DATASETS[_name] = types.SimpleNamespace(name=_wrem_name, is_data=False, group="Top")
# MC samples that are neither W/Z nor ttbar, all treated the same way
OTHER_MC_SAMPLES = {**DIBOSON_SAMPLES, **PHOTON_INDUCED_SAMPLES, **SINGLE_TOP_SAMPLES}
# samples with the Z -> mumu selection and the MC weights, and SingleMuon data. As WRemnants: the Z samples (common.zprocs)
# get the muon calibration with smearing, the CT18Z PDF weight and the theory correction; ttbar, single top, the dibosons
# and the photon-induced samples keep the uncorrected muons, central_pdf_weight and theory_corr_weight are 1, and uT uses
# all prompt gen leptons, photons and neutrinos
Z_MC = {"MCDY", "MCZtautau"}
DIMUON_MC = Z_MC | {"MCTTbar"} | set(OTHER_MC_SAMPLES)
DIMUON_DATASETS = {"SingleMuon"} | DIMUON_MC

ROOT.gStyle.SetOptStat(0)

# Trigger object selection and matching as in WRemnants (wremnants/include/utils.hpp, 2016PostVFP)
ROOT.gInterpreter.Declare(
    """
    ROOT::VecOps::RVec<int> goodMuonTriggerCandidate(const ROOT::VecOps::RVec<int> &TrigObj_id, const ROOT::VecOps::RVec<int> &TrigObj_filterBits) {
        // muon trigger objects with filterBits 16 or 32 (HLT_IsoMu24 or HLT_IsoTkMu24)
        return (TrigObj_id == 13) && (((TrigObj_filterBits & 16) != 0) || ((TrigObj_filterBits & 32) != 0));
    }

    bool hasTriggerMatch(float eta, float phi, const ROOT::VecOps::RVec<float> &TrigObj_eta, const ROOT::VecOps::RVec<float> &TrigObj_phi) {
        for (size_t i = 0; i < TrigObj_eta.size(); i++) {
            float dEta = eta - TrigObj_eta[i];
            float dPhi = ROOT::VecOps::DeltaPhi(phi, TrigObj_phi[i]);
            if (dEta * dEta + dPhi * dPhi < 0.09) return true;
        }
        return false;
    }
    """
)

# Golden JSON lumi mask as in WRemnants (datasetDict_2016PostVFP.py lumijson, applied by narf's JsonHelper),
# copied from WRemnants/wremnants-data/data/ next to this script
GOLDEN_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt")
# Recorded luminosity per lumi section from brilcalc, as WRemnants (datasetDict_2016PostVFP.py lumicsv), copied next to this script
LUMI_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bylsoutput.csv")

ROOT.gInterpreter.Declare(
    """
    namespace goldenjson {
        std::unordered_map<unsigned int, std::vector<std::pair<unsigned int, unsigned int>>> lumis;

        void add(unsigned int run, unsigned int first, unsigned int last) {
            lumis[run].emplace_back(first, last);
        }

        bool isGood(unsigned int run, unsigned int lumi) {
            auto it = lumis.find(run);
            if (it == lumis.end()) return false;
            for (const auto &range : it->second)
                if (lumi >= range.first && lumi <= range.second) return true;
            return false;
        }
    }
    """
)

MUON_MASS = 0.1056583745

# Weights saved in the output, as in WRemnants (nominal_weight = weight * central_pdf_weight * theory_corr_weight * exp_weight)
WEIGHT_COLUMNS = {
    "SingleMuon": ["nominal_weight"],
    "MinBias": ["nominal_weight"],
    "MCDY": ["genWeight", "genWeight_sign", "weight_pu", "weight_vtx", "weight_newMuonPrefiringSF", "L1PreFiringWeight_ECAL_Nom",
             "weight_fullMuonSF_withTrackingReco", "exp_weight", "central_pdf_weight", "theory_corr_weight", "nominal_weight"],
    "MCZtautau": ["genWeight", "genWeight_sign", "weight_pu", "weight_vtx", "weight_newMuonPrefiringSF", "L1PreFiringWeight_ECAL_Nom",
                  "weight_fullMuonSF_withTrackingReco", "exp_weight", "central_pdf_weight", "theory_corr_weight", "nominal_weight"],
    "MCTTbar": ["genWeight", "genWeight_sign", "weight_pu", "weight_vtx", "weight_newMuonPrefiringSF", "L1PreFiringWeight_ECAL_Nom",
                "weight_fullMuonSF_withTrackingReco", "exp_weight", "central_pdf_weight", "theory_corr_weight", "nominal_weight"],
    "MCMinBias": ["genWeight", "genWeight_sign", "weight_newMuonPrefiringSF", "L1PreFiringWeight_ECAL_Nom", "nominal_weight"],
}
WEIGHT_COLUMNS.update({name: WEIGHT_COLUMNS["MCTTbar"] for name in OTHER_MC_SAMPLES})


# WRemnants helpers, built once and only for the samples that need them, as at the top of mz_dilepton.py
@functools.cache
def CalibrationHelpers():
    mc_jpsi_helper, data_jpsi_helper = muon_calibration.make_jpsi_crctn_helpers(WREM_ARGS, common.calib_filepaths)
    mc_cvh_helper, data_cvh_helper, _ = muon_calibration.make_muon_calibration_helpers(WREM_ARGS, era=ERA)
    smearing_helper = None if WREM_ARGS.noSmearing else muon_calibration.make_muon_smearing_helpers()[0]
    return {
        "data": (data_cvh_helper, data_jpsi_helper),
        "mc": (mc_cvh_helper, mc_jpsi_helper),
        "smearing": smearing_helper,
        "bias": muon_calibration.make_muon_bias_helpers(WREM_ARGS),
    }


@functools.cache
def MuonPrefiringHelper():
    return muon_prefiring.make_muon_prefiring_helpers(era=ERA)[0]


@functools.cache
def DYWeightHelpers(trigger_selection):
    # only the helpers of the nominal weight (central PDF and first theory correction), not those of the uncertainty variations
    analysis_type = ROOT.wrem.AnalysisType.Dilepton if trigger_selection == "dilepton" else ROOT.wrem.AnalysisType.Wlike
    return {
        "pileup": pileup.make_pileup_helper(era=ERA),
        "vertex": vertex.make_vertex_helper(era=ERA),
        "muon_efficiency": muon_efficiencies_smooth.make_muon_efficiency_helpers_smooth(
            filename=WREM_ARGS.sfFile,
            era=ERA,
            max_pt=WREM_ARGS.pt[2],
            what_analysis=analysis_type,
            isoEfficiencySmoothing=WREM_ARGS.isoEfficiencySmoothing,
            smooth3D=WREM_ARGS.smooth3dsf,
            isoDefinition=WREM_ARGS.isolationDefinition,
        )[0],
        "theory": theory_corrections.make_theory_helpers(WREM_ARGS.pdfs, WREM_ARGS.theoryCorr, procs=["Z"], corrs=["pdf_central"])["Z"],
        # the Z correction file (..._CorrZ.pkl.lz4) for both Z samples, as WRemnants (load_corr_helpers takes the boson from the name)
        "theory_corr": theory_corrections.load_corr_helpers([WREM_DATASETS[name].name for name in sorted(Z_MC)], WREM_ARGS.theoryCorr[:1]),
    }


FILE_NAMES_SINGLEMUON = glob.glob("/pnfs/psi.ch/cms/trivcat/store/user/zoghafoo/crabsubmission_files/SingleMuon/NanoV9Run2016*DataPostVFP*/*/*/*.root")
print(f"\nNumber of SingleMuon files: {len(FILE_NAMES_SINGLEMUON)}\n")

FILE_NAMES_ZEROBIAS = glob.glob("/pnfs/psi.ch/cms/trivcat/store/user/zoghafoo/crabsubmission_files/ZeroBias/NanoV9Run2016*DataPostVFP_MinBias*/*/*/*.root")
print(f"Number of ZeroBias files: {len(FILE_NAMES_ZEROBIAS)}\n")



FILE_NAMES_MCDY = glob.glob("/pnfs/psi.ch/cms/trivcat/store/user/zoghafoo/crabsubmission_files/DYJetsToMuMu_H2ErratumFix_TuneCP5_13TeV-powhegMiNNLO-pythia8-photos/NanoV9MCPostVFP_DY_18052026/260518_072416/*/*.root")
print(f"Number of MC_DYJets files: {len(FILE_NAMES_MCDY)}\n")

FILE_NAMES_MCZTAUTAU = glob.glob("/pnfs/psi.ch/cms/trivcat/store/user/zoghafoo/crabsubmission_files/DYJetsToTauTau_M-50_AtLeastOneEorMuDecay_H2ErratumFix_TuneCP5_13TeV-powhegMiNNLO-pythia8-photos/NanoV9MCPostVFP_DYTauTau_06112026/*/*/*.root")
print(f"Number of MC_Ztautau files: {len(FILE_NAMES_MCZTAUTAU)}\n")

FILE_NAMES_MCTTBAR = glob.glob("/pnfs/psi.ch/cms/trivcat/store/user/zoghafoo/crabsubmission_files/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/NanoV9MCPostVFP_TTTo2L2Nu_06112026/*/*/*.root")
print(f"Number of MC_TTbar files: {len(FILE_NAMES_MCTTBAR)}\n")

FILE_NAMES_MCOTHER = {name: glob.glob(f"/pnfs/psi.ch/cms/trivcat/store/user/zoghafoo/crabsubmission_files/{production}/*/*/*.root")
                      for name, (_, production) in OTHER_MC_SAMPLES.items()}
for name, files in FILE_NAMES_MCOTHER.items():
    print(f"Number of {name} files: {len(files)}")
print()

FILE_NAMES_MCZEROBIAS = glob.glob("/pnfs/psi.ch/cms/trivcat/store/user/zoghafoo/crabsubmission_files/MinBias_TuneCP5_13TeV-pythia8/NanoV9MCPostVFP_ZeroBias_18052026/260518_072813/*/*.root")
print(f"Number of MC_ZeroBias files: {len(FILE_NAMES_MCZEROBIAS)}\n")


DATASET_FILES = {
    "SingleMuon": FILE_NAMES_SINGLEMUON,
    "MinBias": FILE_NAMES_ZEROBIAS,
    "MCDY": FILE_NAMES_MCDY,
    "MCZtautau": FILE_NAMES_MCZTAUTAU,
    "MCTTbar": FILE_NAMES_MCTTBAR,
    **FILE_NAMES_MCOTHER,
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
        if name in DIMUON_MC | {"MCMinBias"}:
            # only the sign of genWeight, defined before any selection as WRemnants "weight" (mz_dilepton.py, build_graph)
            dataframes[name] = dataframes[name].Define("genWeight_sign", "std::copysign(1.0, genWeight)")

    if maxevents is not None:
        print(f"Processing only the first {maxevents} Events from each selected dataset.")

    return dataframes


def PrintDatasetCounts(dataframes):
    counts = {}

    for dataset_name, dataframe in dataframes.items():

        # booked together, so all counts come from one pass over the files
        total_events_ptr = dataframe.Count()
        total_PFcands_ptr = dataframe.Sum("nPFCands")
        # sum of weights over all events before any selection, for the MC normalisation xsec * lumi / weight_sum,
        # as WRemnants weightsum = df.SumAndCount("weight") (mz_dilepton.py) stored as "weight_sum" by narf
        weight_sum_ptr = dataframe.Sum("genWeight_sign") if "genWeight_sign" in dataframe.GetColumnNames() else None

        total_events = total_events_ptr.GetValue()
        total_PFcands = total_PFcands_ptr.GetValue()

        print(f"\nTotal number of Events in {dataset_name} file: {total_events}")
        print(f"Total number of PFCands in {dataset_name} file: {total_PFcands}")

        counts[f"total_events_{dataset_name}"] = total_events
        counts[f"total_PFCands_{dataset_name}"] = total_PFcands

        if weight_sum_ptr is not None:
            weight_sum = weight_sum_ptr.GetValue()
            print(f"Sum of sign(genWeight) in {dataset_name} file: {weight_sum}")
            counts[f"weight_sum_{dataset_name}"] = weight_sum

        if dataset_name == "SingleMuon":
            lumi = IntegratedLuminosity(DATASET_FILES[dataset_name])
            print(f"Integrated luminosity of the certified lumi sections in {dataset_name} files: {lumi:.4f} /fb")
            counts[f"lumi_{dataset_name}"] = lumi

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
    weight_sum_row = "\t".join(["weight_sum"] + [str(counts_dict.get(f"weight_sum_{name}", "")) for name in dataset_names]) + "\n"
    lumi_row = "\t".join(["lumi"] + [str(counts_dict.get(f"lumi_{name}", "")) for name in dataset_names]) + "\n"

    with open(filepath, "w") as f:
        f.write(header)
        f.write(events_row)
        f.write(pfcands_row)
        f.write(weight_sum_row)
        f.write(lumi_row)

    print(f"Saved dataset counts (txt) to {filepath}\n")
    return filepath


def GoldenJSON(df):
    # data only: keep the lumi sections certified as good for physics
    if ROOT.goldenjson.lumis.empty():
        with open(GOLDEN_JSON) as f:
            for run, ranges in json.load(f).items():
                for first, last in ranges:
                    ROOT.goldenjson.add(int(run), first, last)
    df = df.Filter("goldenjson::isGood(run, luminosityBlock)", "Golden JSON")
    return df


def IntegratedLuminosity(files):
    # as narf (graph_builder.py): sum of the recorded luminosity over the certified lumi sections in the LuminosityBlocks tree, in /fb
    recorded = {}
    with open(LUMI_CSV) as f:
        next(f)  # skip the brilcalc header line
        for row in csv.DictReader(f):
            if row["#run:fill"][0] == "#":
                continue
            recorded[(int(row["#run:fill"].split(":")[0]), int(row["ls"].split(":")[0]))] = float(row["recorded(/fb)"])

    lumis = GoldenJSON(ROOT.RDataFrame("LuminosityBlocks", list(files))).AsNumpy(["run", "luminosityBlock"])
    return sum(recorded[(int(run), int(ls))] for run, ls in zip(lumis["run"], lumis["luminosityBlock"]))


def TriggerSelection(df):
    df = df.Filter("HLT_IsoTkMu24 || HLT_IsoMu24", "Trigger")
    return df


def EventFilters(df):
    df = df.Define("Electron_veto",
                   "Electron_pt > 10 && Electron_cutBased > 0 && abs(Electron_eta) < 2.4 && "
                   "abs(Electron_dxy) < 0.05 && abs(Electron_dz) < 0.2"
                   )
    df = df.Filter("ROOT::VecOps::Sum(Electron_veto) == 0", "Electron veto")
    df = df.Filter("Flag_globalSuperTightHalo2016Filter && Flag_EcalDeadCellTriggerPrimitiveFilter && Flag_goodVertices && "
                   "Flag_HBHENoiseIsoFilter && Flag_HBHENoiseFilter && Flag_BadPFMuonFilter",
                   "MET filters"
                   )
    return df


def CorrectedMuons(df, dataset_name):
    # muon momentum calibration as WRemnants (muon_calibration.define_corrected_muons), defines Muon_corrected{Pt,Eta,Phi,Charge}:
    # data: track refit (cvh) + layer-by-layer + J/psi mass fit corrections (muonCorrData "lbl_massfit"),
    # DY MC: ideal-geometry refit (cvhideal) + layer-by-layer truth corrections (muonCorrMC "idealMC_lbltruth") + resolution smearing,
    # MC that is not W/Z: uncorrected Muon_pt, eta, phi, charge
    helpers = CalibrationHelpers()
    dataset = WREM_DATASETS[dataset_name]
    cvh_helper, jpsi_helper = helpers["data"] if dataset.is_data else helpers["mc"]
    return muon_calibration.define_corrected_muons(df, cvh_helper, jpsi_helper, WREM_ARGS, dataset, helpers["smearing"], helpers["bias"])


def VetoMuons(df):
    # charge = -99 marks muons without a valid track refit
    df = df.Define("Muon_isGoodGlobal",
                   "Muon_isGlobal && Muon_highPurity && Muon_standalonePt > 15 && Muon_standaloneNumberOfValidHits >= 1 && "
                   "ROOT::VecOps::DeltaR2(Muon_standaloneEta, Muon_correctedEta, Muon_standalonePhi, Muon_correctedPhi) < 0.09"
                   )
    df = df.Define("Muon_veto",
                   "Muon_looseId && abs(Muon_dxybs) < 0.05 && Muon_correctedCharge != -99 && Muon_isGoodGlobal && "
                   "Muon_correctedPt > 15 && abs(Muon_correctedEta) < 2.4"
                   )
    return df


def GoodMuons(df, isolation_threshold=0.15):
    df = df.Filter("ROOT::VecOps::Sum(Muon_veto) == 2", "Two veto muons")
    # no pT cut beyond the 15 GeV of the veto muons: the pT of both muons is saved (SnapshotColumns), cut on it afterwards
    df = df.Define("Muon_good",
                   "Muon_veto && "
                   # "Muon_correctedPt > 26 && "
                   "Muon_isGlobal && Muon_highPurity && Muon_mediumId && "
                   f"Muon_vtxAgnPfRelIso04_all < {isolation_threshold}"
                   )
    df = df.Filter("ROOT::VecOps::Sum(Muon_good) == 2", "Two good muons")
    return df


def DiMuonSelection(df):
    df = df.Define("Muon_sel", "Muon_veto && Muon_good")
    df = df.Filter("ROOT::VecOps::Sum(Muon_sel && Muon_correctedCharge == -1) == 1 && "
                   "ROOT::VecOps::Sum(Muon_sel && Muon_correctedCharge == 1) == 1",
                   "Opposite charge"
                   )
    df = df.Define("Muon_idx", "ROOT::VecOps::Nonzero(Muon_sel)")
    df = df.Define("DiMuon_pt", "pow(pow(Muon_correctedPt[Muon_idx[0]] * cos(Muon_correctedPhi[Muon_idx[0]]) + Muon_correctedPt[Muon_idx[1]] * cos(Muon_correctedPhi[Muon_idx[1]]), 2) + pow(Muon_correctedPt[Muon_idx[0]] * sin(Muon_correctedPhi[Muon_idx[0]]) + Muon_correctedPt[Muon_idx[1]] * sin(Muon_correctedPhi[Muon_idx[1]]), 2), 0.5)")
    return df


def ZCandidateSelection(df, mass_window, ptll_cut):
    # no mass cut: DiMuon_Mass is saved, cut on it afterwards
    # df = df.Filter(f"DiMuon_Mass >= {mass_window}", "Mass window")
    df = df.Filter(f"DiMuon_Pt >= {ptll_cut}", "DiMuon pT cut")
    return df


def TriggerMatching(df, trigger_selection="wlike"):
    df = df.Define("TrigObj_good", "goodMuonTriggerCandidate(TrigObj_id, TrigObj_filterBits)")
    df = df.Define("Muon_passTrigger",
                   """
                   ROOT::VecOps::RVec<bool> res(Muon_idx.size());
                   for (size_t i = 0; i < Muon_idx.size(); i++) {
                       res[i] = hasTriggerMatch(Muon_correctedEta[Muon_idx[i]], Muon_correctedPhi[Muon_idx[i]], TrigObj_eta[TrigObj_good], TrigObj_phi[TrigObj_good]);
                   }
                   return res;
                   """
                   )
    if trigger_selection == "wlike":
        # W-like: the triggering muon is the mu- for even and the mu+ for odd event numbers
        df = df.Define("Muon_trigCharge", "event % 2 == 0 ? -1 : 1")
        df = df.Filter("Muon_correctedCharge[Muon_idx[0]] == Muon_trigCharge ? Muon_passTrigger[0] : Muon_passTrigger[1]", "Trigger matching")
    else:
        # dilepton: at least one of the two muons is matched
        df = df.Filter("Muon_passTrigger[0] || Muon_passTrigger[1]", "Trigger matching")
    return df


def TriggerMuons(df, dataset_name, trigger_selection="wlike", isolation_threshold=0.15):
    # triggering (trigMuons) and other muon (nonTrigMuons) as WRemnants (muon_selections.define_trigger_muons, select_standalone_muons),
    # needed for the muon scale factors. W-like: trigMuons is the mu- for even and the mu+ for odd event numbers;
    # dilepton: trigMuons is the mu-, nonTrigMuons the mu+
    dilepton = trigger_selection == "dilepton"
    iso_branch = muon_selections.getIsoBranch(WREM_ARGS.isolationDefinition)
    df = df.Alias("goodMuons", "Muon_good")
    df = df.Define("isEvenEvent", "event % 2 == 0")
    df = muon_selections.define_trigger_muons(df, dilepton=dilepton)
    for muons in ["trigMuons", "nonTrigMuons"]:
        df = muon_selections.select_standalone_muons(df, WREM_DATASETS[dataset_name], WREM_ARGS.trackerMuons, muons)
        df = df.Define(f"{muons}_passIso0", f"{iso_branch}[{muons}][0] < {isolation_threshold}")
        if dilepton:
            df = df.Define(f"{muons}_passTrigger0", f"hasTriggerMatch({muons}_eta0, {muons}_phi0, TrigObj_eta[TrigObj_good], TrigObj_phi[TrigObj_good])")
    return df


def MuonScaleFactors(df, efficiency_helper, trigger_selection="wlike", is_w_or_z=True):
    # reco, tracking, ID+IP, trigger and isolation scale factors as WRemnants (mz_dilepton.py), smooth in pt, eta and uT;
    # uT relative to the gen boson for W/Z samples, to the sum of all prompt gen leptons, photons and neutrinos otherwise
    for muons in ["trigMuons", "nonTrigMuons"]:
        df = muon_selections.define_muon_uT_variable(df, is_w_or_z, smooth3dsf=WREM_ARGS.smooth3dsf, colNamePrefix=muons)
        # corrected muon kinematics, as WRemnants without --useTnpMuonVarForSF
        for tnp_var, var in [("tnpPt0", "pt0"), ("tnpEta0", "eta0"), ("tnpCharge0", "charge0"), ("tnpUT0", "uT0")]:
            df = df.Alias(f"{muons}_{tnp_var}", f"{muons}_{var}")

    sf_vars = ["tnpPt0", "tnpEta0", "SApt0", "SAeta0", "tnpUT0", "tnpCharge0", "passIso0"]
    if trigger_selection == "dilepton":
        sf_vars.append("passTrigger0")
    if not WREM_ARGS.smooth3dsf:
        sf_vars.remove("tnpUT0")
    # first all variables of the triggering muon, then those of the other one
    columns = [f"{muons}_{var}" for muons in ["trigMuons", "nonTrigMuons"] for var in sf_vars]
    return df.Define("weight_fullMuonSF_withTrackingReco", efficiency_helper, columns)


def EventWeights(df, dataset_name, trigger_selection="wlike"):
    # genWeight_sign is defined in MakeDataframes, before any selection
    prefiring_columns = ["Muon_correctedEta", "Muon_correctedPt", "Muon_correctedPhi", "Muon_correctedCharge", "Muon_looseId"]
    if dataset_name in DIMUON_MC:
        helpers = DYWeightHelpers(trigger_selection)
        # experimental weights as WRemnants (mz_dilepton.py): pileup, vertex z, muon prefiring (WRemnants 2016 parametrisation),
        # ECAL prefiring and muon scale factors
        df = df.Define("weight_pu", helpers["pileup"], ["Pileup_nTrueInt"])
        df = df.Define("weight_vtx", helpers["vertex"], ["GenVtx_z", "Pileup_nTrueInt"])
        df = df.Define("weight_newMuonPrefiringSF", MuonPrefiringHelper(), prefiring_columns)
        df = MuonScaleFactors(df, helpers["muon_efficiency"], trigger_selection, is_w_or_z=dataset_name in Z_MC)
        df = df.Define("exp_weight", "weight_pu*weight_newMuonPrefiringSF*L1PreFiringWeight_ECAL_Nom*weight_vtx*weight_fullMuonSF_withTrackingReco")
        # nominal_weight = weight * central_pdf_weight (CT18Z) * theory_corr_weight (SCETlib+DYTurbo) * exp_weight,
        # as WRemnants (theory_tools.define_theory_weights_and_corrs); ttbar has no theory helpers, both theory weights are 1
        df = df.Alias("weight", "genWeight_sign")
        theory_helpers = helpers["theory"] if dataset_name in Z_MC else {}
        df = theory_tools.define_theory_weights_and_corrs(df, WREM_DATASETS[dataset_name].name, helpers["theory_corr"], WREM_ARGS, theory_helpers=theory_helpers)
    elif dataset_name == "MCMinBias":
        # not a W/Z sample: WRemnants muon prefiring on the uncorrected muons; no pileup in this sample and no selected muons for scale factors
        df = CorrectedMuons(df, dataset_name)
        df = df.Define("weight_newMuonPrefiringSF", MuonPrefiringHelper(), prefiring_columns)
        df = df.Define("nominal_weight", "genWeight_sign * weight_newMuonPrefiringSF * L1PreFiringWeight_ECAL_Nom")
    else:
        df = df.Define("nominal_weight", "1.0")
    return df


def PVSelection(df, dataset_name):
    df = df.Define(
        "PFCands_vertexRefUnique",
        """
        std::set<int> sorted_unique(PFCands_vertexRef.begin(), PFCands_vertexRef.end());
        return ROOT::VecOps::RVec<int>(sorted_unique.begin(), sorted_unique.end());
        """,
    )

    if dataset_name in DIMUON_DATASETS:
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
    df = df.Define("PFCands_E", "sqrt(PFCands_mass * PFCands_mass + PFCands_pt * PFCands_pt * cosh(PFCands_eta) * cosh(PFCands_eta))")

    df = df.Define(
        "PF",
        f"""
        (abs(PFCands_charge) == {elec_charge}) &&
        (PFCands_vertexRef == PFCands_vertexRefRandom) &&
        ((PFCands_pvAssocQuality == 6) || (PFCands_pvAssocQuality == 7)) &&
        (abs(PFCands_pdgId) != 13) &&
        (PFCands_pt > 0.5)
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
    if dataset in DIMUON_DATASETS:

        print(f"Calculating DiMuon_4Vector for dataset {dataset}...")
        
        df = df.Define(
            "DiMuon_P",
            """
            TLorentzVector muon1, muon2;
            muon1.SetPtEtaPhiM(Muon_correctedPt[Muon_idx[0]], Muon_correctedEta[Muon_idx[0]], Muon_correctedPhi[Muon_idx[0]], {MUON_MASS});
            muon2.SetPtEtaPhiM(Muon_correctedPt[Muon_idx[1]], Muon_correctedEta[Muon_idx[1]], Muon_correctedPhi[Muon_idx[1]], {MUON_MASS});
            TLorentzVector diMuonSystem = muon1 + muon2;
            return diMuonSystem;
            """.format(MUON_MASS=MUON_MASS)
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
        print(f"Dataset {dataset} not in {sorted(DIMUON_DATASETS)}. Skipping DiMuon_4Vector calculation.")
    return df

def ObservablesCalculation(df):
    df = df.Define("PFSelection_PFCands_pt", "Take(PFCands_pt, PFSelection_idx)")
    df = df.Define("PFSelection_PFCands_eta", "Take(PFCands_eta, PFSelection_idx)")
    df = df.Define("PFSelection_PFCands_phi", "Take(PFCands_phi, PFSelection_idx)")
    df = df.Define("PFSelection_PFCands_pvAssocQuality", "Take(PFCands_pvAssocQuality, PFSelection_idx)")
    df = df.Define("PFSelection_PFCands_InvariantMass", "PFCands_InvariantMass")
    df = df.Define("PFSelection_nPFCands", "PFSelection_idx.size()")
    df = df.Define("PFSelection_PFCands_mass", "Take(PFCands_mass, PFSelection_idx)")
    df = df.Define("PFSelection_PFCands_E", "Take(PFCands_E, PFSelection_idx)")

    exprHt = "ROOT::VecOps::Sum(Take(PFCands_pt, PFSelection_idx))"
    df = df.Define("PFSelection_PFCands_Ht", exprHt)

    exprPt2sum = "ROOT::VecOps::Sum(Take(PFCands_pt * PFCands_pt, PFSelection_idx))"
    df = df.Define("PFSelection_PFCands_Pt2sum", exprPt2sum)

    exprPsum = "ROOT::VecOps::Sum(Take(PFCands_p, PFSelection_idx))"
    df = df.Define("PFSelection_PFCands_Psum", exprPsum)

    exprP2sum = "ROOT::VecOps::Sum(Take(PFCands_p * PFCands_p, PFSelection_idx))"
    df = df.Define("PFSelection_PFCands_P2sum", exprP2sum)

    return df


def SaveSelectedEvents(df_SingleMuon, df_MinBias, df_MCDY, df_MCZtautau, df_MCTTbar, df_MCMinBias, out_path="", output_suffix=""):
    df_SingleMuon.Snapshot("Events", f"{out_path}/Data_SingleMuon_SelectedEvents_{output_suffix}.root", SnapshotColumns("SingleMuon"))
    df_MinBias.Snapshot("Events", f"{out_path}/Data_MinBias_SelectedEvents_{output_suffix}.root", SnapshotColumns("MinBias"))
    df_MCDY.Snapshot("Events", f"{out_path}/MC_DY_SelectedEvents_{output_suffix}.root", SnapshotColumns("MCDY"))
    df_MCZtautau.Snapshot("Events", f"{out_path}/MC_Ztautau_SelectedEvents_{output_suffix}.root", SnapshotColumns("MCZtautau"))
    df_MCTTbar.Snapshot("Events", f"{out_path}/MC_TTbar_SelectedEvents_{output_suffix}.root", SnapshotColumns("MCTTbar"))
    df_MCMinBias.Snapshot("Events", f"{out_path}/MC_MinBias_SelectedEvents_{output_suffix}.root", SnapshotColumns("MCMinBias"))

def SaveRunsTree(dataset_name, output_file):
    # Gen-level sums live in Runs (one entry per run per input file); data has none.
    if dataset_name not in DIMUON_MC | {"MCMinBias"}:
        return
    opts = ROOT.RDF.RSnapshotOptions()
    opts.fMode = "UPDATE"
    ROOT.RDataFrame("Runs", DATASET_FILES[dataset_name]).Snapshot("Runs", output_file, ["run", "genEventCount_", "genEventSumw_", "genEventSumw2_"], opts)


def SnapshotColumns(dataset_name):
    variables_list_minbias = [f"PFSelection_{var}" for var in VARIABLES.keys()] + WEIGHT_COLUMNS[dataset_name]
    if dataset_name in DIMUON_DATASETS:
        # corrected kinematics of the two selected muons (TriggerMuons), to cut on them afterwards
        muon_columns = [f"{muons}_{var}0" for muons in ["trigMuons", "nonTrigMuons"] for var in ["pt", "eta", "phi", "charge"]]
        return ["DiMuon_pt"] + variables_list_minbias + ["DiMuon_P", "DiMuon_Mass", "DiMuon_Rapidity", "DiMuon_xmaxll", "DiMuon_xminll", "DiMuon_Eta", "DiMuon_Pt", "DiMuon_Phi", "DiMuon_E"] + muon_columns
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
    parser.add_argument(
        "--mass-window",
        type=float,
        default=50,
        help="DiMuon mass window [min, max) in GeV (default: 50, as in WRemnants)",
    )
    parser.add_argument(
        "--ptll-cut",
        type=float,
        default=0,
        help="DiMuon pT range [min, max) in GeV (default: 0, as in WRemnants)",
    )
    parser.add_argument(
        "--isolation-threshold",
        type=float,
        default=0.15,
        help="Cut on Muon_vtxAgnPfRelIso04_all for both muons (default: 0.15)",
    )
    parser.add_argument(
        "--trigger-selection",
        choices=["wlike", "dilepton"],
        default="wlike",
        help="'wlike': match the muon whose charge is chosen by the event number (WRemnants default); 'dilepton': match either muon",
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
        if dataset_name in {"SingleMuon", "MinBias"}:
            dataframe = GoldenJSON(dataframe)
        if dataset_name in DIMUON_DATASETS:
            dataframe = TriggerSelection(dataframe)
            dataframe = EventFilters(dataframe)
            dataframe = CorrectedMuons(dataframe, dataset_name)
            dataframe = VetoMuons(dataframe)
            dataframe = GoodMuons(dataframe, args.isolation_threshold)
            dataframe = DiMuonSelection(dataframe)
            dataframe = addDiMuon4Vector(dataframe, dataset_name)
            dataframe = ZCandidateSelection(dataframe, args.mass_window, args.ptll_cut)
            dataframe = TriggerMatching(dataframe, args.trigger_selection)
            dataframe = TriggerMuons(dataframe, dataset_name, args.trigger_selection, args.isolation_threshold)

        dataframe = EventWeights(dataframe, dataset_name, args.trigger_selection)
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
            processed_dataframes["MCZtautau"],
            processed_dataframes["MCTTbar"],
            processed_dataframes["MCMinBias"],
            out_path=args.output_dir,
            output_suffix=args.output_suffix,
        )
        for dataset_name in OTHER_MC_SAMPLES:
            processed_dataframes[dataset_name].Snapshot("Events", f"{args.output_dir}/MC_{dataset_name[2:]}_SelectedEvents_{args.output_suffix}.root", SnapshotColumns(dataset_name))
    else:
        dataset_name = args.dataset
        output_file = os.path.join(args.output_dir, f"{dataset_name}_SelectedEvents_{args.output_suffix}.root")
        processed_dataframes[dataset_name].Snapshot("Events", output_file, SnapshotColumns(dataset_name))
        SaveRunsTree(dataset_name, output_file)


if __name__ == "__main__":
    main()
