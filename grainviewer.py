# %%
import cv2
import shutil
import numpy as np
from pathlib import Path


# %%
class GrainArrayImport:
    def __init__(self, arr_dir: str, destination_dir: str, working_dir: str = ".") -> None:
        self.path_array_dir = Path(working_dir, arr_dir)
        self.destination_dir = Path(destination_dir)

        self.array_selection = []
        self.classified_arrays = np.array([])

        self.idx_of_array_in_memory = 0
        self.array_in_memory = np.empty((1, 1, 1))

    def select_arrays(self, selection_size: int):
        # list with all array names in "grain_arrays"
        arrays_in_arr_dir = [arr.name for arr in self.path_array_dir.iterdir() if arr.name.startswith("arr")]

        # look for array with names of already classifed arrays, load into self.classified_arrays
        # update "arrays_in_arr_dir" to only include uncalssified arrays
        if Path(self.destination_dir, "classified_arrays.npy").exists() is True:
            self.classified_arrays = np.load(Path(self.destination_dir, "classified_arrays.npy"))
            arrays_in_arr_dir = [arr for arr in arrays_in_arr_dir if arr not in self.classified_arrays]
            Path(self.destination_dir, "classified_arrays.npy").unlink()

        # check for valid selection size
        while selection_size > len(arrays_in_arr_dir):
            selection_size = selection_size - 1
            print("Chosen selction size parameter was too big. Reduced to the maximal possible size of {}".format(selection_size))

        # rnd generator for choosing a selection of grains to classify
        rangen = np.random.default_rng()
        self.array_selection = rangen.choice(arrays_in_arr_dir, size=selection_size, replace=False)

    def load_array_into_memory(self, arr_name):
        self.arr_name = arr_name
        self.path_to_array = Path(self.path_array_dir, self.arr_name)
        self.array_in_memory = np.load(self.path_to_array)

    def update_array_in_memory(self):
        self.arr_name = self.array_selection[self.idx_of_array_in_memory]
        self.path_to_array = Path(self.path_array_dir, self.arr_name)
        self.array_in_memory = np.load(self.path_to_array)
        # increment idx by 1
        self.idx_of_array_in_memory += 1


class GrainArrayVisualiser:
    def __init__(self, grain_array: np.ndarray) -> None:
        self.grain_array = GrainArrayVisualiser.adjust_gray_values(grain_array)
        self.frame_idx = 0
        self.frame = self.grain_array[self.frame_idx]

        self.max_frame = np.shape(self.grain_array)[0]

    def increment_frame(self):
        if self.frame_idx < self.max_frame-1:
            self.frame_idx = self.frame_idx + 1
            self.frame = self.grain_array[self.frame_idx]

    def decrement_frame(self):
        if self.frame_idx > 0:
            self.frame_idx -= 1
            self.frame = self.grain_array[self.frame_idx]

    @staticmethod
    def adjust_gray_values(grain_array: np.ndarray):
        return (grain_array * 254) + 1


def main():
    # arr_dir = input("path to arr_dir")

    # check for dataset dir structur OR create it
    destination = Path("test_dest_dir")
    destination_atoll = destination / "atoll"
    destination_intact = destination / "intact"
    destination_notGarnet = destination / "notGarnet"

    if not destination.exists():
        destination.mkdir()
    if not destination_atoll.exists():
        destination_atoll.mkdir()
    if not destination_intact.exists():
        destination_intact.mkdir()
    if not destination_notGarnet.exists():
        destination_notGarnet.mkdir()

    grain_array = GrainArrayImport(arr_dir="grain_arrays", destination_dir="test_dest_dir")
    grain_array.select_arrays(selection_size=5)

    for arr_name in grain_array.array_selection:
        grain_array.load_array_into_memory(arr_name)

        frame_displayed = GrainArrayVisualiser(grain_array.array_in_memory)

        while True:
            cv2.imshow("frame", frame_displayed.frame)
            key = cv2.waitKey(1)

            if key == ord("w"):
                frame_displayed.increment_frame()

            elif key == ord("s"):
                frame_displayed.decrement_frame()

            elif key == ord("a"):
                check = input("Do you want to classify this grain as atoll? [y/n]")
                if check == "y":
                    shutil.copyfile(src=grain_array.path_to_array,
                                    dst=Path(grain_array.destination_dir, "atoll", grain_array.arr_name))
                    print("grain classified")
                    # add grain ID to the classifed grains array
                    grain_array.classified_arrays = np.append(grain_array.classified_arrays, grain_array.arr_name)
                    break
                else:
                    print("Continue...")

            elif key == ord("i"):
                check = input("Do you want to classify this grain as intact? [y/n]")
                if check == "y":
                    shutil.copyfile(src=grain_array.path_to_array,
                                    dst=Path(grain_array.destination_dir, "intact", grain_array.arr_name))
                    print("grain classified")
                    # add grain ID to the classifed grains array
                    grain_array.classified_arrays = np.append(grain_array.classified_arrays, grain_array.arr_name)
                    break
                else:
                    print("Continue...")

            elif key == ord("n"):
                check = input("Do you want to classify this grain as notGarnet? [y/n]")
                if check == "y":
                    shutil.copyfile(src=grain_array.path_to_array,
                                    dst=Path(grain_array.destination_dir, "notGarnet", grain_array.arr_name))
                    print("grain classified")
                    # add grain ID to the classifed grains array
                    grain_array.classified_arrays = np.append(grain_array.classified_arrays, grain_array.arr_name)
                    break
                else:
                    print("Continue...")

            elif key == ord("o"):
                other_class = input("Specify another class [str]")
                check = input("Do you want to classify this grain as {oc}? [y/n]".format(oc=other_class))
                if check == "y":
                    if not Path.exists(Path(grain_array.destination_dir, other_class)):
                        Path.mkdir(Path(grain_array.destination_dir, other_class))
                    shutil.copyfile(src=grain_array.path_to_array,
                                    dst=Path(grain_array.destination_dir, other_class, grain_array.arr_name))
                    print("grain classified")
                    # add grain ID to the classifed grains array
                    grain_array.classified_arrays = np.append(grain_array.classified_arrays, grain_array.arr_name)
                    break
                else:
                    print("Continue...")

            elif key == ord("e"):
                print("exiting")
                break

        cv2.destroyAllWindows

    print(grain_array.classified_arrays)
    np.save(grain_array.destination_dir / "classified_arrays.npy", grain_array.classified_arrays)


if __name__ == "__main__":
    main()
