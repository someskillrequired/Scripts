import os
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import CampaignMapEditor
from matplotlib.colors import ListedColormap, BoundaryNorm

# === Layer definitions ===
LayerTerrain = {0: "None", 1: "Water", 2: "Grass", 3: "Sky", 4: "Abyse"}
LayerObjects = {0: "None", 1: "Mountain", 2: "Wood", 3: "Gold", 4: "Stone", 5: "Iron"}
LayerZombies = {
    0: "ZombieNone", 1: "walker1", 2: "walker2", 3: "walker3", 4: "runner1",
    5: "runner2", 6: "runner3", 7: "medium1", 8: "medium2", 9: "medium3",
    10: "Strong1", 11: "Strong2", 12: "Strong3", 13: "Powerful1", 14: "Powerful2",
    15: "Ultra", 16: "Harpies1", 17: "Harpies2", 18: "Harpies3",
    19: "Venoms1", 20: "Venoms2", 21: "Venoms3", 22: "Chubbies1",
    23: "Chubbies2", 24: "Chubbies3"
}

# === Ordered layer map (only layers we summarize) ===
layer_map = {
    0: ("LayerTerrain", LayerTerrain),
    1: ("LayerObjects", LayerObjects),
    3: ("LayerZombies", LayerZombies),
}

def convert_numpy_dict(d):
    return {int(k): int(v) for k, v in d.items()}

def get_maps(directory):
    maps = []
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.startswith("gendata") and filename.endswith(".zxsav"):
                maps.append(os.path.join(root, filename))
    return maps

def summarize_layer(matrix, layer_dict, include_distances=False):
    """Compute stats for each value in the matrix."""
    unique, counts = np.unique(matrix, return_counts=True)
    stats = {}
    center = np.array(matrix.shape) // 2
    y, x = np.indices(matrix.shape)
    distances = np.sqrt((y - center[0])**2 + (x - center[1])**2)

    for k, c in zip(unique, counts):
        key_name = layer_dict.get(k, f"Unknown({k})")
        mask = (matrix == k)

        entry = {
            "count": int(c),
            "min": int(c),
            "max": int(c),
            "mean": float(c),
            "median": float(c),
            "stddev": 0.0
        }

        if include_distances and k != 0 and np.any(mask):
            dists = distances[mask]
            entry.update({
                "avg_dist": float(np.mean(dists)),
                "min_dist": float(np.min(dists)),
                "max_dist": float(np.max(dists)),
                "std_dist": float(np.std(dists))
            })
        else:
            entry.update({
                "avg_dist": 0.0,
                "min_dist": 0.0,
                "max_dist": 0.0,
                "std_dist": 0.0
            })

        stats[key_name] = entry
    return stats

# === Main ===
if __name__ == "__main__":
    np.random.seed(0)
    maps = get_maps(r"C:\Users\joshu\OneDrive\Documents\My Games\They Are Billions\Saves")
    print(f"Number of maps processed: {len(maps)}")
    
    summary_stats = {layer_name: defaultdict(list) for layer_name, _ in layer_map.values()}
    
    for map_file in maps:
        map_data = CampaignMapEditor.CustomMap(
            r"D:\Steam\steamapps\common\They Are Billions",
            map_file,
            r"C:\Program Files\7-Zip\7z.exe",
            r"D:\Steam\steamapps\common\They Are Billions\passwords.txt"
        )

        for i, layer in enumerate(map_data.layers):
            if i not in layer_map:
                continue

            layer_name, layer_dict = layer_map[i]

            stats = summarize_layer(layer, layer_dict, include_distances=(layer_name == "LayerZombies"))
            for key, s in stats.items():
                summary_stats[layer_name][key].append(s)

    # Print summary
    for layer_name, values in summary_stats.items():
        print(f"\n=== {layer_name} ===")
        header = f"{'Tile':15} {'Min':>8} {'Max':>8} {'Mean':>8} {'Median':>8} {'StdDev':>10}"
        print(header)
        print("-" * len(header))
        for key_name, entries in values.items():
            counts = np.array([e["count"] for e in entries])
            print(f"{key_name:15} {counts.min():8.2f} {counts.max():8.2f} {counts.mean():8.2f} {np.median(counts):8.2f} {counts.std():10.2f}")
        if layer_name == "LayerZombies":
            header = f"{'ZombieType':15} {'DistMin':>10} {'DistMax':>10} {'DistMean':>10} {'DistStd':>10}"
            print("-" * len(header))
            print(header)
            print("-" * len(header))
            for key_name, entries in values.items():
                min_d = np.mean([e["min_dist"] for e in entries])
                max_d = np.mean([e["max_dist"] for e in entries])
                mean_d = np.mean([e["avg_dist"] for e in entries])
                std_d = np.mean([e["std_dist"] for e in entries])
                print(f"{key_name:15} {min_d:10.2f} {max_d:10.2f} {mean_d:10.2f} {std_d:10.2f}")
