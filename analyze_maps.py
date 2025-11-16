import os
import numpy as np
from collections import defaultdict
import CampaignMapEditor

# === Layer definitions ===
LayerTerrain = {
    0: "None",
    1: "Water",
    2: "Grass",
    3: "Sky",
    4: "Abyse"
}

LayerRoads = {
    0: "None",
    1: "Nothing?",
    2: "Unknown2",
}

LayerObjects = {
    0: "None",
    1: "Mountain",
    2: "Wood",
    3: "Gold",
    4: "Stone",
    5: "Iron"
}

LayerZombies = {
    0: "ZombieNone",
    1: "Weak1",
    2: "Weak2",
    3: "Weak3",
    4: "Runners1",
    5: "Runners2",
    6: "Runners3",
    7: "Medium1",
    8: "Medium2",
    9: "Medium3",
    10: "Strong1",
    11: "Strong2",
    12: "Strong3",
    13: "Powerful1",
    14: "Powerful2",
    15: "Ultra1",  # Giant
    16: "Harpies1",
    17: "Harpies2",
    18: "Harpies3",
    19: "Venoms1",
    20: "Venoms2",
    21: "Venoms3",
    22: "Chubbies1",
    23: "Chubbies2",
    24: "Chubbies3"
}

LayerFortress = {
    0: "None",
    1: "tall_barrier",
    2: "tall_barrier_spiked",
    3: "short_barrier_spiked",
    4: "pylon",
    5: "pylon_light1",
    6: "door",
    7: "pylon_light2",
    8: "rubble",
}

LayerPipes = {
    0: "None",
    1: "tube",
    2: "tubew/vent",
    3: "right_elbow",
    4: "y_top",
    5: "vent",
    6: "blower1",
    7: "blower2",
}

LayerBelts = {
    0: "None",
    1: "belt",
    2: "beltendpoint",
}

# === Ordered Layer Map with names ===
layer_map = {
    0: ("Terrain", LayerTerrain),
    1: ("Objects", LayerObjects),
    3: ("Zombies", LayerZombies),
}

def convert_numpy_dict(d):
    """Convert numpy scalar keys/values in a dictionary to Python ints."""
    return {int(k): int(v) for k, v in d.items()}

def get_maps(directory):
    maps = []
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.startswith("gendata") and filename.endswith(".zxsav"):
                maps.append(os.path.join(root, filename))
    return maps

if __name__ == "__main__":
    maps = get_maps(r"C:\Users\joshu\OneDrive\Documents\My Games\They Are Billions\Saves")
    sevenzip_executable = r"C:\Program Files\7-Zip\7z.exe"
    directory = r"D:\Steam\steamapps\common\They Are Billions"

    total_maps = len(maps)
    print(f"Number of maps processed: {total_maps}")

    # Storage for all map summaries
    summary_stats = {
        layer_name: defaultdict(list)
        for layer_name, _ in layer_map.values()
    }

    # Collect data from all maps
    for map_file in maps:
        map = CampaignMapEditor.CustomMap(
            directory, map_file, sevenzip_executable,
            r"D:\Steam\steamapps\common\They Are Billions\passwords.txt"
        )

        for i, layer in enumerate(map.layers):
            if i not in layer_map:
                continue  # skip unwanted layers

            layer_name, layer_dict = layer_map[i]
            unique, counts = np.unique(layer, return_counts=True)
            convert_data = convert_numpy_dict(dict(zip(unique, counts)))

            # Replace numeric IDs with readable names
            for key, value in convert_data.items():
                key_name = layer_dict.get(key, f"Unknown({key})")
                summary_stats[layer_name][key_name].append(value)

    # === Summarize across all maps ===
    print("\n========== SUMMARY (All Maps) ==========\n")
    for layer_name, values in summary_stats.items():
        print(f"\n=== {layer_name} ===")
        header = f"{'Tile':15} {'Min':>8} {'Max':>8} {'Mean':>8} {'Median':>8} {'StdDev':>10}"
        print(header)
        print("-"*len(header))

        for key_name, counts in values.items():
            if not counts:
                continue
            counts_array = np.array(counts)
            min_val = int(np.min(counts_array))
            max_val = int(np.max(counts_array))
            mean_val = float(np.mean(counts_array))
            median_val = float(np.median(counts_array))
            std_val = float(np.std(counts_array))

            print(f"{key_name:15} {min_val:8} {max_val:8} {mean_val:8.2f} {median_val:8.2f} {std_val:10.2f}")