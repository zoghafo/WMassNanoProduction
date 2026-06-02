from CRABClient.UserUtilities import config
config = config()

config.General.requestName = 'SingleMuon_Run2016H-21Feb2020_UL2016_WMass_MiniAODv2-v1_02062026'
config.General.workArea = 'crab_projects'
config.General.transferOutputs = True
config.General.transferLogs = True

config.JobType.numCores = 1
config.JobType.maxMemoryMB = 3000
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = '/home/z/zoghafoo/CMSSW_10_6_26/src/Configuration/WMassNanoProduction/configs/NanoV9DataPostVFP_cfgCRAB.py'
config.JobType.allowUndistributedCMSSW = True

config.Data.inputDataset = '/SingleMuon/Run2016H-21Feb2020_UL2016_WMass_MiniAODv2-v1/MINIAOD'

config.Data.splitting = 'LumiBased'
config.Data.unitsPerJob = 10
config.Data.outLFNDirBase = '/store/user/zoghafoo/crabsubmission_files'
config.Data.publication = True
config.Data.outputDatasetTag = 'NanoV9Run2016HDataPostVFP_02062026'
config.Data.inputDBS = 'global'
config.Data.useParent = False

config.Site.storageSite = 'T3_CH_PSI'
