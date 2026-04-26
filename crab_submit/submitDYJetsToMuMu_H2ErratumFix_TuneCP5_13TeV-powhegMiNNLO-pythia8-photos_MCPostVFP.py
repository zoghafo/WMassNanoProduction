from CRABClient.UserUtilities import config
config = config()

config.General.requestName = 'DYJetsToMuMu_H2ErratumFix_TuneCP5_13TeV-powhegMiNNLO-pythia8-photos_MCPostVFP_TrackFitV722_Nanoe5036'
config.General.workArea = 'crab_projects'
config.General.transferOutputs = True
config.General.transferLogs = True

config.JobType.numCores = 1
config.JobType.maxMemoryMB = 2000
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = '/home/z/zoghafoo/CMSSW_10_6_26/src/Configuration/WMassNanoProduction/configs/NanoV9MCPostVFP_cfg.py'
config.JobType.allowUndistributedCMSSW = True

config.Data.inputDataset = '/DYJetsToMuMu_H2ErratumFix_TuneCP5_13TeV-powhegMiNNLO-pythia8-photos/RunIISummer20UL16MiniAODv2-106X_mcRun2_asymptotic_v17-v2/MINIAODSIM'

config.Data.splitting = 'FileBased'
config.Data.unitsPerJob = 2
config.Data.outLFNDirBase = '/store/user/zoghafoo/crabsubmission_files'
config.Data.publication = True
config.Data.outputDatasetTag = 'NanoV9MCPostVFP_TrackFitV722_NanoProdv1_24042026'
config.Data.inputDBS = 'global'
config.Data.useParent = False

config.Site.storageSite = 'T3_CH_PSI'
