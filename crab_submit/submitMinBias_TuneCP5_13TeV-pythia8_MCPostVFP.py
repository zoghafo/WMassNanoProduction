from CRABClient.UserUtilities import config
config = config()

config.General.requestName = 'MinBias_TuneCP5_13TeV-pythia8_MCPostVFP_17052026'
config.General.workArea = 'crab_projects'
config.General.transferOutputs = True
config.General.transferLogs = True

config.JobType.numCores = 1
config.JobType.maxMemoryMB = 2500
config.JobType.maxJobRuntimeMin = 480
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = '/home/z/zoghafoo/CMSSW_10_6_26/src/Configuration/WMassNanoProduction/configs/NanoV9MCPostVFP_ZeroBias_cfg.py'
config.JobType.allowUndistributedCMSSW = True

config.Data.inputDataset = '/MinBias_TuneCP5_13TeV-pythia8/RunIISummer20UL16MiniAODv2-NoPU_106X_mcRun2_asymptotic_v17-v2/MINIAODSIM'

config.Data.splitting = 'FileBased'
config.Data.unitsPerJob = 5
config.Data.outLFNDirBase = '/store/user/zoghafoo/crabsubmission_files'
config.Data.publication = True
config.Data.outputDatasetTag = 'NanoV9MCPostVFP_ZeroBias_17052026'
config.Data.inputDBS = 'global'
config.Data.useParent = False

config.Site.storageSite = 'T3_CH_PSI'
