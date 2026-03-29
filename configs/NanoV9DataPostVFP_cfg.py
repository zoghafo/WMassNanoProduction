# Auto generated configuration file
# using: 
# Revision: 1.19 
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options: RECO --conditions 106X_dataRun2_v35 --customise Configuration/DataProcessing/Utils.addMonitoring --datatier NANOAOD --era Run2_2016,run2_nanoAOD_106Xv2 --eventcontent NANOAOD --filein dbs:/SingleMuon/Run2016F-21Feb2020_UL2016_WMass_MiniAODv2-v1/MINIAOD --fileout file:NanoV9DataPostVFP.root --nThreads 1 --no_exec --number 1000 --python_filename configs/NanoV9DataPostVFP_cfg.py --scenario pp --step NANO --data
import FWCore.ParameterSet.Config as cms

from Configuration.Eras.Era_Run2_2016_cff import Run2_2016
from Configuration.Eras.Modifier_run2_nanoAOD_106Xv2_cff import run2_nanoAOD_106Xv2
import sys

trigger = sys.argv[2]


process = cms.Process('NANO',Run2_2016,run2_nanoAOD_106Xv2)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.Geometry.GeometrySimDB_cff')
process.load('Configuration.StandardSequences.MagneticField_AutoFromDBCurrent_cff')
# process.load('PhysicsTools.NanoAOD.nano_cff')
process.load('PhysicsTools.NanoAOD.nanoPF_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(100000)
)

# Input source
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/260000/013231DB-EFDC-7746-9D8B-5AB400673820.root',
        # '/store/data/Run2016F/ZeroBias/MINIAOD/UL2016_MiniAODv2-v1/2530000/21A8E24C-0E4D-C149-85F3-F4AF29ED01D2.root',
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/260000/554769CF-1261-AD45-BB6C-ED15BD2AF415.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/260000/627342B6-FEED-A542-B003-DD52F8D53416.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/260000/74E17230-DDA0-DC4C-87F4-17163B86FB95.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/260000/76080D38-C422-1D4F-963F-AC8BAEECD5A7.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/260000/9A0EF94F-B486-6B46-9BCB-5127B5972097.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/260000/C69440D4-AA1F-7040-9E56-A2AC6679A808.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/260000/C9484C06-0FFB-074F-B622-77BB065AFFCF.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/13D15018-7A47-4742-8F06-96020BD8F54A.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/1A1BD39E-909B-D04D-AAE6-87213DA3B2F9.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/1FED9950-1EB6-2B4C-8158-7960590EC8FE.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/200C5457-293F-5C40-9BBC-3EC4086A133B.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/272266B1-48B5-9641-845F-F5B3C739E9D9.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/29FBA859-F12D-ED4B-BF0B-6F88A0B9F9AA.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/2A6F693E-02C3-F94F-AD1B-B76ABA7E8D8F.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/2DC55D5F-61C6-7746-817D-9C3652C3BC91.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/31411DD5-C2BC-D74B-B104-CFE9B2B7B740.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/32BE4EA6-AA05-0D46-979E-8CB4AC9C8185.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/38A2071C-8E43-104E-BE6A-F57BF59AC434.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/395D6357-1AFC-674D-9BE2-A022317042BB.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/3B60A19B-54D4-2F44-A832-60A9652CE1C0.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/3B7BF022-8F86-E941-A9CC-9259E206A516.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/41B298DA-CBAC-DE40-8F94-A743CFE7DC7A.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/42360A49-F799-8547-95CA-81DBE46A2954.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/4437C18E-C9F0-AC44-8EF8-CC5F77FCAEAD.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/474FB06B-80DB-4C4F-B92C-B96AA24EC3A6.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/5DA8E06B-82DE-4B41-A75B-E1CB833A9319.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/6196F66E-BF07-DB44-B350-448E8489466A.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/64BAAC7B-A2A2-0744-AF6A-01A3A3745367.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/72BF5AFE-FA14-A947-B12F-6B9C8EA2D47C.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/73D8D271-1C0B-B24F-9DBD-9A152701595D.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/77286F28-4FC0-1645-83DE-120888833D94.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/7CA3D1A3-5E2D-A547-9C70-903BCF22009D.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/7E1C35FF-3C1B-9D4C-B4DF-962113DCCA98.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/8104C86E-762C-644A-A1BC-9FCDED48033E.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/84D55866-F03A-F146-8A06-A8BEF8B2D021.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/883B6E1E-3044-A64F-8ABF-97E929601C53.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/8F618158-C580-8D49-A5F3-B16151B3E326.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/94D70A8D-FD95-9440-B0B4-B0F62D98D00F.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/971C41C8-82ED-564A-8DAC-51A4B76A3E4A.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/9A111519-EF61-6B40-95C8-B3C3EABF3F94.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/AAA5DB23-55EC-EA48-9D39-AD738AAC6E21.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/ACEAB8A7-2887-7640-BEAC-541D87F8C5FD.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/AF55F533-8EB8-AA4F-874B-CE92188FE4B6.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/B951514A-7EF7-D14D-9923-92A5944380FB.root', 
        '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/BC1D3E07-78F3-DF41-AE12-C4922FD157B9.root', 
        # '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/BCE73EB1-3000-D64A-93F4-2BA6919DE1CC.root', 
        # '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/BDF2CB59-8DD3-B843-97EE-FA04B1CA1DCA.root', 
        # '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/BE2058CD-D12C-7E49-A6E6-E63849648CD9.root', 
        # '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/BF87271D-1C92-974E-9D1E-CF968A862D11.root', 
        # '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/BFF87332-3689-7041-A570-52430B9E7FAB.root', 
        # '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/CBDD2DF9-99BF-2244-BC08-7060101F1F0F.root', 
        # '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/CC1ABB3B-7416-D548-AD09-ED7D2C04518C.root', 
        # '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/CCCA30D0-EBBA-A34C-9174-E687A623F573.root', 
        # '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/D68DD196-E30D-1540-A060-40F0579B060F.root', 
        # '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/D938AE96-4646-D64C-8FFC-E5CEF7457DCC.root', 
        # '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/D97A2E8A-CD89-384E-90AE-2C6142502D62.root', 
        # '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/DAA141ED-0CA9-D54D-8095-780D92B6FC3C.root', 
        # '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/F65FB131-AEA5-7743-A8AE-5995C6EE1E17.root', 
        # '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/FB11B3D3-24A7-3A4B-AB5A-B883D17BA680.root', 
        # '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/FD768EDE-4A8E-CF4A-87FB-CE67F48B610B.root', 
        # '/store/data/Run2016F/SingleMuon/MINIAOD/21Feb2020_UL2016_WMass_MiniAODv2-v1/270000/FDC70126-1E8C-134B-8670-E09B79922CBA.root'
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
    fileName = cms.untracked.string('file:NanoV9DataPostVFP_PF_{}_{}Events.root'.format(trigger, process.maxEvents.input.value())),
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
