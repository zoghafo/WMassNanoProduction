from CRABClient.UserUtilities import config
config = config()

config.General.requestName = 'ZeroBias_Run2016F-UL2016_MiniAODv2-v1_02052026'
config.General.workArea = 'crab_projects'
config.General.transferOutputs = True
config.General.transferLogs = True

config.JobType.numCores = 1
config.JobType.maxMemoryMB = 2000
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = '/home/z/zoghafoo/CMSSW_10_6_26/src/Configuration/WMassNanoProduction/configs/NanoV9DataPostVFP_MINBIAS_cfg.py'
config.JobType.allowUndistributedCMSSW = True

config.Data.inputDataset = '/ZeroBias/Run2016F-UL2016_MiniAODv2-v1/MINIAOD'

config.Data.splitting = 'LumiBased'
config.Data.unitsPerJob = 10
config.Data.outLFNDirBase = '/store/user/zoghafoo/crabsubmission_files'
config.Data.publication = True
config.Data.outputDatasetTag = 'NanoV9Run2016FDataPostVFP_MinBias_02052026'
config.Data.inputDBS = 'global'
config.Data.useParent = False

config.Site.storageSite = 'T3_CH_PSI'
