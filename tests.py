import numpy as np
from grainviewer import GrainArrayImport

def test_GrainArrayImport():
    grain_importer = GrainArrayImport(arr_dir="test_data", destination_dir="not definded yet")
    grain_importer.select_arrays(selection_size=3)
    
    # test arrays in memory against known test arrays
    arr1 = np.ones((5,5,5))
    arr2 = np.ones((5,5,5)) * 200
    arr3 = np.ones((5,5,5)) * 0.5

    print(grain_importer.array_in_memory)
    assert np.array_equal(grain_importer.array_in_memory, arr1), "Something in GrainArrayImport initialisation or select_array swent wrong"
    
if __name__ == "__main__":
    test_GrainArrayImport()