# Auto generated configuration file
# using: 
# Revision: 1.19 
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options: RECO --conditions 106X_dataRun2_v35 --customise Configuration/DataProcessing/Utils.addMonitoring --datatier NANOAOD --era Run2_2016,run2_nanoAOD_106Xv2 --eventcontent NANOAOD --filein dbs:/ZeroBias/Run2016F-UL2016_MiniAODv2-v1/MINIAOD --fileout file:NanoV9DataPostVFP.root --nThreads 1 --no_exec --number 1000 --python_filename configs/NanoV9DataPostVFP_cfg.py --scenario pp --step NANO --data
import FWCore.ParameterSet.Config as cms

from Configuration.Eras.Era_Run2_2016_cff import Run2_2016
from Configuration.Eras.Modifier_run2_nanoAOD_106Xv2_cff import run2_nanoAOD_106Xv2

process = cms.Process('NANO',Run2_2016,run2_nanoAOD_106Xv2)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.Geometry.GeometrySimDB_cff')
process.load('Configuration.StandardSequences.MagneticField_AutoFromDBCurrent_cff')
process.load('PhysicsTools.NanoAOD.nanoPF_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(1000)
)

# Input source
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
        '/store/data/Run2016F/ZeroBias/MINIAOD/UL2016_MiniAODv2-v1/2530000/21A8E24C-0E4D-C149-85F3-F4AF29ED01D2.root', 
        '/store/data/Run2016F/ZeroBias/MINIAOD/UL2016_MiniAODv2-v1/2530000/4713EE94-56BB-9C4C-89C2-04BC434CBF49.root', 
        '/store/data/Run2016F/ZeroBias/MINIAOD/UL2016_MiniAODv2-v1/2530000/4B862432-BB6E-E043-BBDF-1C951087C375.root', 
        '/store/data/Run2016F/ZeroBias/MINIAOD/UL2016_MiniAODv2-v1/2530000/6B8CE043-7AD9-1843-9DA9-E4CE11043949.root', 
        '/store/data/Run2016F/ZeroBias/MINIAOD/UL2016_MiniAODv2-v1/2530000/AED71A88-9F2A-0844-B479-A18A2A480B6D.root', 
        '/store/data/Run2016F/ZeroBias/MINIAOD/UL2016_MiniAODv2-v1/2530000/C0DA6C2E-7303-4445-99E1-D860F0E1C73B.root', 
        '/store/data/Run2016F/ZeroBias/MINIAOD/UL2016_MiniAODv2-v1/2530000/C2BE5DEF-A0C8-1141-8383-75A7CECDB4FF.root', 
        '/store/data/Run2016F/ZeroBias/MINIAOD/UL2016_MiniAODv2-v1/2530000/D85BF493-18C9-1A4E-B5FF-D468204DDC15.root'
    ),
    secondaryFileNames = cms.untracked.vstring()
)

process.options = cms.untracked.PSet(

)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('RECO nevts:1000'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition

process.NANOAODoutput = cms.OutputModule("NanoAODOutputModule",
    compressionAlgorithm = cms.untracked.string('LZMA'),
    compressionLevel = cms.untracked.int32(9),
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('NANOAOD'),
        filterName = cms.untracked.string('')
    ),
    fileName = cms.untracked.string('file:NanoV9DataPostVFP_PF_ZeroBias.root'),
    outputCommands = process.NANOAODEventContent.outputCommands
)

# Additional output definition

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '106X_dataRun2_v35', '')

# Path and EndPath definitions
process.nanoAOD_step = cms.Path(process.nanoSequence)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.NANOAODoutput_step = cms.EndPath(process.NANOAODoutput)

# Schedule definition
process.schedule = cms.Schedule(process.nanoAOD_step,process.endjob_step,process.NANOAODoutput_step)
from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

# customisation of the process.

# Automatic addition of the customisation function from PhysicsTools.NanoAOD.nanoPF_cff
from PhysicsTools.NanoAOD.nanoPF_cff import nanoAOD_customizeData 

#call to customisation function nanoAOD_customizeData imported from PhysicsTools.NanoAOD.nanoPF_cff
process = nanoAOD_customizeData(process)

# Automatic addition of the customisation function from Configuration.DataProcessing.Utils
from Configuration.DataProcessing.Utils import addMonitoring 

#call to customisation function addMonitoring imported from Configuration.DataProcessing.Utils
process = addMonitoring(process)

# End of customisation functions

# Customisation from command line

# Add early deletion of temporary data products to reduce peak memory need
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
# End adding early deletion
