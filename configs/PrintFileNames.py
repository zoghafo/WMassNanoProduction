import subprocess
import sys

trigger = sys.argv[1]

if trigger == "SingleMuon":
    dirs = [
        "/eos/cms/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/260000/",
        "/eos/cms/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/",
        "/eos/cms/store/data/Run2016G/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/260000/",
        "/eos/cms/store/data/Run2016G/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/",
    ]
elif trigger == "ZeroBias":
    dirs = [
        "/eos/cms/store/data/Run2016G/ZeroBias/MINIAOD/UL2016_MiniAODv2-v1/2530000/",
    ]
else:
    print(f"Unknown trigger {trigger}")
    sys.exit(1)

output_file = f"configs/file_list_{trigger}.txt"

with open(output_file, "w") as out:
    for d in dirs:
        # Remove /eos/cms prefix
        clean_dir = d.replace("/eos/cms", "")

        # Run eos ls
        result = subprocess.run(
            ["eos", "ls", d],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            print(f"Error accessing {d}:\n{result.stderr}")
            continue

        for fname in result.stdout.splitlines():
            full_path = f"{clean_dir}{fname}"
            out.write(f"'{full_path}',\n")

print(f"File list saved to {output_file}")