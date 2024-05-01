# Blender importer/exporter for elu and ani files (RaiderZ)

This project contains scripts that can be used to load .elu models and .ani animations inside blender and to export them as fbx files either individually or in mass.

* Compatible with all RaiderZ's .elu versions
* Compatible with all RaiderZ's .ani versions
* **Not** compatible with vertex animations (less than 0.5% of .ani files contain vertex animations).
* ~~All exported fbx animations contain root motion~~ Root motion disabled. You can re-enable root motion in
extracted animations by enabling the code below `# Root Motion` comment in [blenderfunctions.py](/elu-ani-importer/EluLibrary/blenderfunctions.py) 

# Requirements

* ~~Blender 2.78 or 2.79. It won't work on 2.8 and above versions because of the Blender's API changes.~~
* I have now updated the main branch scripts and tested them on Blender 4.1, so they should work on Blender 4.1 and above. 

# Using the script

* Clone or download the repo as zip
* Open [BlenderEluLoader.blend](/elu-ani-importer/Blender)
* Set `MODEL_FOLDER_TO_EXPORT` to the type of folder you want to export models from
* Set `EXPORT_TYPE` to selective or mass export
* Set `SELECTIVE_EXPORT_KEYSTRING` if you selected selective export in previous step
* Set `SourceDir` to point to path of `datadump/data` directory
* Set `DestinationDir` to point to path where you would like to export fbx files
* Since mass export takes time and there is a possibility that it may fail or might need to be cancelled, a file [RecordFile.txt](/elu-ani-importer/Blender/Logs/RecordFile.txt) has been added that keeps a record of all files that have already been exported. Restarting mass export will skip all the files listed inside RecordFile.txt. Delete RecordFile.txt before each re-export if file skip feature is not required. This is not applicable for SelectiveExport.

![Elu model inside blender](https://i.imgur.com/bvzEMzi.png)
![Elu model imported inside UE4](https://i.imgur.com/9WEnR90.png)

# Warnings

Remove/delete test .elu files from MapObject folder before starting mass export operation to avoid spending hours loading and exporting for each of these "special-case" files. Exported fbx file may exceed over 5-10 GB, and may overflow your RAM while export operation is in progress.
These test .elu files are named similar to `test_50call_50node_300000face.elu`. Avoid all of these.
