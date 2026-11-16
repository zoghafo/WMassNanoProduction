import argparse
import csv
import glob
import json
import os

import ROOT

ROOT.gErrorIgnoreLevel = ROOT.kError  # hides the "no dictionary for class edm::..." warnings from the NanoAOD metadata

# Luminosity, sum of weights and absolute MC normalisation scale of the DY MC, as WRemnants:
#   scale = xsec [pb] * lumi [/fb] * 1000 / weight_sum   (wremnants/datasets/datagroups.py, processScaleFactor)
# lumi:       recorded luminosity summed over the certified lumi sections in the LuminosityBlocks tree
#             of the SingleMuon files (narf/narf/graph_builder.py)
# weight_sum: sum of sign(genWeight) over all DY MC events, before any selection
#             (scripts/histmakers/mz_dilepton.py, weightsum = df.SumAndCount("weight"))
# Needs only ROOT, it runs outside the WRemnants container too.

XSEC_DY = 2001.9  # pb, DY -> mumu in WRemnants (utilities/common.py, xsec_DYJetsToLL)

# SingleMuon productions, the same as the glob NanoV9Run2016*DataPostVFP* of NanoAOD_EventSelection2.py (11 485 files):
# F, its resubmission, G and the 2016H v4 production of 6 Nov (the old 2016H production of 2 Jun, which missed lumi sections,
# is now in crabsubmission_files/ and no longer matched). Expected: 16.8071 /fb (F 0.4181, G 7.6508, H 8.7382), no lumi
# section in more than one file. Run 278770 (0.17 /fb) is pre-VFP and not in the post-VFP F dataset
SINGLEMUON_DIR = "/pnfs/psi.ch/cms/trivcat/store/user/zoghafoo/crabsubmission_files/SingleMuon"
FILES_SINGLEMUON = [
    f"{SINGLEMUON_DIR}/NanoV9Run2016FDataPostVFP_24042026/*/*/*.root",
    f"{SINGLEMUON_DIR}/NanoV9Run2016FDataPostVFP_24042026_Resubmission/*/*/*.root",
    f"{SINGLEMUON_DIR}/NanoV9Run2016GDataPostVFP_02062026/*/*/*.root",
    f"{SINGLEMUON_DIR}/NanoV9Run2016HDataPostVFP_v4_06112026/*/*/*.root",
]
# same files as DATASET_FILES in NanoAOD_EventSelection2.py
FILES_MCDY = ["/pnfs/psi.ch/cms/trivcat/store/user/zoghafoo/crabsubmission_files/DYJetsToMuMu_H2ErratumFix_TuneCP5_13TeV-powhegMiNNLO-pythia8-photos/NanoV9MCPostVFP_DY_18052026/260518_072416/*/*.root"]

# Golden JSON and brilcalc luminosity per lumi section, as WRemnants (datasetDict_2016PostVFP.py lumijson, lumicsv),
# copied from WRemnants/wremnants-data/data/ next to this script
GOLDEN_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt")
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


def LoadGoldenJSON():
    with open(GOLDEN_JSON) as f:
        for run, ranges in json.load(f).items():
            for first, last in ranges:
                ROOT.goldenjson.add(int(run), first, last)


def RecordedLuminosity():
    # recorded luminosity per (run, lumi section) in /fb, the column narf's make_lumihelper reads (lumitools.py)
    recorded = {}
    with open(LUMI_CSV) as f:
        next(f)  # skip the brilcalc header line
        for row in csv.DictReader(f):
            if row["#run:fill"][0] == "#":
                continue
            recorded[(int(row["#run:fill"].split(":")[0]), int(row["ls"].split(":")[0]))] = float(row["recorded(/fb)"])
    return recorded


def IntegratedLuminosity(files):
    # as narf (graph_builder.py): every entry of the LuminosityBlocks tree that passes the golden JSON, summed in /fb
    recorded = RecordedLuminosity()
    df = ROOT.RDataFrame("LuminosityBlocks", files).Filter("goldenjson::isGood(run, luminosityBlock)", "Golden JSON")
    lumis = df.AsNumpy(["run", "luminosityBlock"])
    lumi_sections = [(int(run), int(ls)) for run, ls in zip(lumis["run"], lumis["luminosityBlock"])]

    missing = [key for key in set(lumi_sections) if key not in recorded]
    if missing:
        # narf's BrilcalcHelper stops with "lumi not found" here as well
        raise RuntimeError(f"{len(missing)} certified lumi sections are not in {LUMI_CSV}, e.g. {sorted(missing)[:5]}")

    lumi = sum(recorded[key] for key in lumi_sections)
    # a lumi section split over several files appears more than once; narf counts it every time
    unique = set(lumi_sections)
    lumi_unique = sum(recorded[key] for key in unique)
    return lumi, len(lumi_sections), len(unique), lumi_unique


def WeightSum(files):
    # as WRemnants (mz_dilepton.py): weight = sign of genWeight, summed over all events before any selection
    df = ROOT.RDataFrame("Events", files).Define("weight", "std::copysign(1.0, genWeight)")
    weight_sum_ptr = df.Sum("weight")
    count_ptr = df.Count()
    return weight_sum_ptr.GetValue(), count_ptr.GetValue()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Luminosity, sum of weights and MC normalisation scale of the DY MC, as WRemnants"
    )
    parser.add_argument(
        "--nthreads",
        type=int,
        default=8,
        help="Number of threads for RDataFrame (default: 8)",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=None,
        help="Only the first N files of each sample, for tests (the scale is then meaningless)",
    )
    parser.add_argument(
        "--xsec",
        type=float,
        default=XSEC_DY,
        help=f"DY cross section in pb (default: {XSEC_DY}, as WRemnants)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.nthreads > 1:
        ROOT.ROOT.EnableImplicitMT(args.nthreads)

    files_singlemuon = sorted(f for pattern in FILES_SINGLEMUON for f in glob.glob(pattern))[:args.max_files]
    files_mcdy = sorted(f for pattern in FILES_MCDY for f in glob.glob(pattern))[:args.max_files]
    print(f"SingleMuon files: {len(files_singlemuon)}")
    print(f"MC DY files:      {len(files_mcdy)}\n")

    LoadGoldenJSON()
    lumi, n_lumi_sections, n_unique, lumi_unique = IntegratedLuminosity(files_singlemuon)
    print(f"Integrated luminosity: {lumi:.6f} /fb ({n_lumi_sections} certified lumi sections)")
    if n_unique != n_lumi_sections:
        print(f"  {n_lumi_sections - n_unique} lumi sections appear in more than one file and are counted every time, as in narf; "
              f"counted once: {lumi_unique:.6f} /fb")

    weight_sum, n_events = WeightSum(files_mcdy)
    print(f"Sum of weights:        {weight_sum:.1f} (sum of sign(genWeight) over {n_events} DY MC events)\n")

    scale = args.xsec * lumi * 1000 / weight_sum
    print(f"MC normalisation scale = xsec * lumi * 1000 / weight_sum = {args.xsec} pb * {lumi:.4f} /fb * 1000 / {weight_sum:.6g} = {scale:.6g}")


if __name__ == "__main__":
    main()
