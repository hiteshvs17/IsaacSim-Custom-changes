.. _isaacsim_sensors_rtx_IsaacComputeRTXLidarPointCloud_1:

.. _isaacsim_sensors_rtx_IsaacComputeRTXLidarPointCloud:

.. ================================================================================
.. THIS PAGE IS AUTO-GENERATED. DO NOT MANUALLY EDIT.
.. ================================================================================

:orphan:

.. meta::
    :title: Isaac Compute RTX Lidar Point Cloud Node
    :keywords: lang-en omnigraph node isaacSensor rtx isaac-compute-r-t-x-lidar-point-cloud


Isaac Compute RTX Lidar Point Cloud Node
========================================

.. <description>

This node reads from the an RTX Lidar sensor and holds point cloud data buffers

.. </description>


Installation
------------

To use this node enable :ref:`isaacsim.sensors.rtx<ext_isaacsim_sensors_rtx>` in the Extension Manager.


Inputs
------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Error Azimuth (*inputs:accuracyErrorAzimuthDeg*)", "``float``", "Accuracy error of azimuth in degrees applied to all points equally", "0.0"
    "Error Elevation (*inputs:accuracyErrorElevationDeg*)", "``float``", "Accuracy error of elevation in degrees applied to all points equally", "0.0"
    "Error Position (*inputs:accuracyErrorPosition*)", "``float[3]``", "Position offset applied to all points equally", "[0.0, 0.0, 0.0]"
    "LiDAR render result (*inputs:dataPtr*)", "``uint64``", "Pointer to LiDAR render result", "0"
    "Exec (*inputs:exec*)", "``execution``", "The input execution port", "None"
    "Keep Only Positive Distance (*inputs:keepOnlyPositiveDistance*)", "``bool``", "Keep points only if the return distance is > 0", "True"
    "Render Product Path (*inputs:renderProductPath*)", "``token``", "Path of the renderProduct to wait for being rendered", ""


Outputs
-------
.. csv-table::
    :header: "Name", "Type", "Descripton", "Default"
    :widths: 20, 20, 50, 10

    "Azimuth (*outputs:azimuth*)", "``float[]``", "azimuth in deg [-180, 180)", "[]"
    "Buffer Size (*outputs:bufferSize*)", "``uint64``", "Size (in bytes) of the buffer (0 if the input is a texture)", "None"
    "Cuda Device Index (*outputs:cudaDeviceIndex*)", "``int``", "Index of the device where the data lives (-1 for host data)", "-1"
    "Point Cloud Data (*outputs:dataPtr*)", "``uint64``", "Buffer of points containing point cloud data in Lidar coordinates", "None"
    "Elevation (*outputs:elevation*)", "``float[]``", "elevation in deg [-90, 90]", "[]"
    "Exec (*outputs:exec*)", "``execution``", "Output execution triggers when lidar sensor has data", "None"
    "Height (*outputs:height*)", "``uint``", "Height of point cloud buffer, will always return 1", "1"
    "Intensity (*outputs:intensity*)", "``float[]``", "intensity [0,1]", "[]"
    "Range (*outputs:range*)", "``float[]``", "range in m", "[]"
    "Transform (*outputs:transform*)", "``matrixd[4]``", "The transform matrix from lidar to world coordinates", "None"
    "Width (*outputs:width*)", "``uint``", "3 x Width or number of points in point cloud buffer", "0"


Metadata
--------
.. csv-table::
    :header: "Name", "Value"
    :widths: 30,70

    "Unique ID", "isaacsim.sensors.rtx.IsaacComputeRTXLidarPointCloud"
    "Version", "1"
    "Extension", "isaacsim.sensors.rtx"
    "Icon", "ogn/icons/isaacsim.sensors.rtx.IsaacComputeRTXLidarPointCloud.svg"
    "Has State?", "True"
    "Implementation Language", "C++"
    "Default Memory Type", "cpu"
    "Generated Code Exclusions", "None"
    "uiName", "Isaac Compute RTX Lidar Point Cloud Node"
    "Categories", "isaacSensor"
    "Generated Class Name", "OgnIsaacComputeRTXLidarPointCloudDatabase"
    "Python Module", "isaacsim.sensors.rtx"

