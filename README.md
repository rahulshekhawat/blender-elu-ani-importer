# Blender importer/exporter for elu and ani files

This project contains scripts that can be used to load .elu models inside blender along with .ani animations and individual or batch export them as fbx.

* Compatible with all .elu versions
* Compatible with all .ani versions
* **Not** compatible with vertex animations (less than 0.5% of .ani files contain vertex animations).
* All exported fbx animations contain root motion

# Requirements

* Blender 2.78 or above (haven't tested on lower versions but it should work on any blender version that uses the new python 3 API)

# Using the script

* Clone or download the repo as zip
* Open [BlenderEluLoader.blend](/elu-ani-importer/Blender)
* Set `MODEL_FOLDER_TO_EXPORT` to the type of folder you want to export models from
* Set `EXPORT_TYPE` to selective or mass export
* Set `SELECTIVE_EXPORT_KEYSTRING` if you selected selective export in previous step
* Set `SourceDir` to point to path of `datadump/data` directory
* Set `DestinationDir` to point to path where you would like to export fbx files
* Since mass export takes time and there is a possibility that it may fail or you made need to stop the process, I have created a [RecordFile.txt](/elu-ani-importer/Blender/Logs/RecordFile.txt) file that keeps a record of all files that have already been exported. So if you cancel mass export operation in the middle of export and start it later, the export script will skip all the files mentioned in RecordFile. If you would like to load/re-export all those files again, simply delete RecordFile.txt. This is only applicable for MassExport, not SelectiveExport

# Warnings

Remove/delete test .elu files from MapObject folder before starting mass export operation to avoid spending hours loading and exporting for each of these "special-case" files. Exported fbx file may exceed over 5-10 GB, and may overflow your RAM while export operation is in progress.
These test .elu files are named similar to `test_50call_50node_300000face.elu`. Avoid all of these.
