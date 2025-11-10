.. _isaacsim_sensors_rtx_IsaacComputeRTXRadarPointCloud_1:

.. _isaacsim_sensors_rtx_IsaacComputeRTXRadarPointCloud:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Isaac Compute RTX Radar Point Cloud Node
    :keywords: lang-en omnigraph node isaacSensor rtx isaac-compute-r-t-x-radar-point-cloud


Isaac Compute RTX Radar Point Cloud Node
========================================

.. <description>

This node reads from the an RTX Radar sensor and holds point cloud data buffers

.. </description>


Installation
------------

To use this node enable :ref:`isaacsim.sensors.rtx<ext_isaacsim_sensors_rtx>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Radar Render Results (*inputs:dataPtr*)", "``uint64``", "Pointer to Radar render result.", "0"
    "Exec (*inputs:exec*)", "``execution``", "The input execution port", "None"
    "Render Product Path (*inputs:renderProductPath*)", "``token``", "Path of the renderProduct to wait for being rendered", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Azimuth (*outputs:azimuth*)", "``float[]``", "Azimuth angle (degrees)", "[]"
    "Buffer Size (*outputs:bufferSize*)", "``uint64``", "Size (in bytes) of the buffer (0 if the input is a texture)", "None"
    "Cuda Device Index (*outputs:cudaDeviceIndex*)", "``int``", "Index of the device where the data lives (-1 for host data)", "-1"
    "Cycle Cnt (*outputs:cycleCnt*)", "``uint64``", "Scan cycle count", "None"
    "Point Cloud Data (*outputs:dataPtr*)", "``uint64``", "Buffer of 3d points containing point cloud data in Radar coordinates", "None"
    "Elevation (*outputs:elevation*)", "``float[]``", "Angle of elevation (degrees)", "[]"
    "Exec (*outputs:exec*)", "``execution``", "Output execution triggers when Radar sensor has data", "None"
    "Height (*outputs:height*)", "``uint``", "Height of point cloud buffer, will always return 1", "1"
    "Material Id (*outputs:materialId*)", "``uint[]``", "material ID - DEPRECATED, no longer provided.", "[]"
    "Max Az Rad (*outputs:maxAzRad*)", "``float``", "The max unambiguous azimuth for the scan", "None"
    "Max El Rad (*outputs:maxElRad*)", "``float``", "The max unambiguous elevation for the scan", "None"
    "Max Range M (*outputs:maxRangeM*)", "``float``", "The max unambiguous range for the scan", "None"
    "Max Vel Mps (*outputs:maxVelMps*)", "``float``", "The max unambiguous velocity for the scan", "None"
    "Min Az Rad (*outputs:minAzRad*)", "``float``", "The min unambiguous azimuth for the scan", "None"
    "Min El Rad (*outputs:minElRad*)", "``float``", "The min unambiguous elevation for the scan", "None"
    "Min Vel Mps (*outputs:minVelMps*)", "``float``", "The min unambiguous velocity for the scan", "None"
    "Num Detections (*outputs:numDetections*)", "``uint``", "The number of valid detections in the array", "None"
    "Object Id (*outputs:objectId*)", "``uint[]``", "object ID - DEPRECATED, no longer provided.", "[]"
    "Radial Distance (*outputs:radialDistance*)", "``float[]``", "Radial distance (m)", "[]"
    "Radial Velocity (*outputs:radialVelocity*)", "``float[]``", "Radial velocity (m/s)", "[]"
    "Rcs (*outputs:rcs*)", "``float[]``", "Radar cross section in decibels referenced to a square meter (dBsm)", "[]"
    "Scan Idx (*outputs:scanIdx*)", "``uchar``", "Scan index for sensors with multi scan support", "None"
    "Semantic Id (*outputs:semanticId*)", "``uint[]``", "semantic ID - DEPRECATED, no longer provided.", "[]"
    "Sensor ID (*outputs:sensorID*)", "``uchar``", "Sensor Id for sensor that generated the scan", "None"
    "Time Stamp NS (*outputs:timeStampNS*)", "``uint64``", "Scan timestamp in nanoseconds", "None"
    "Transform (*outputs:transform*)", "``matrixd[4]``", "The input matrix transformed from Radar to World", "None"
    "Width (*outputs:width*)", "``uint``", "3 x Width or number of points in point cloud buffer", "0"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.sensors.rtx.IsaacComputeRTXRadarPointCloud"
    "Version", "1"
    "Extension", "isaacsim.sensors.rtx"
    "Icon", "ogn/icons/isaacsim.sensors.rtx.IsaacComputeRTXRadarPointCloud.svg"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Isaac Compute RTX Radar Point Cloud Node"
    "Categories", "isaacSensor"
    "Generated Class Name", "OgnIsaacComputeRTXRadarPointCloudDatabase"
    "Python Module", "isaacsim.sensors.rtx"

