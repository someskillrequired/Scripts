import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from scipy.ndimage import gaussian_filter

# === Zombie type dictionary ===
LayerZombies = {
    0: "ZombieNone", 1: "walker1", 2: "walker2", 3: "walker3", 4: "runner1",
    5: "runner2", 6: "runner3", 7: "medium1", 8: "medium2", 9: "medium3",
    10: "Strong1", 11: "Strong2", 12: "Strong3", 13: "Powerful1", 14: "Powerful2",
    15: "Ultra", 16: "Harpies1", 17: "Harpies2", 18: "Harpies3",
    19: "Venoms1", 20: "Venoms2", 21: "Venoms3", 22: "Chubbies1",
    23: "Chubbies2", 24: "Chubbies3"
}

def get_maps(directory):
    maps = []
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.startswith("gendata") and filename.endswith(".zxsav"):
                maps.append(os.path.join(root, filename))
    return maps

def summarize_layer(matrix, layer_dict):
    """Compute counts of each zombie type."""
    unique, counts = np.unique(matrix, return_counts=True)
    stats = {}
    for k, c in zip(unique, counts):
        key_name = layer_dict.get(int(k), f"Unknown({k})")
        stats[key_name] = c
    return stats

def build_zombie_heatmap(layers, skip_zero=True, smooth=True, sigma=3):
    """
    Combine multiple zombie layers into a single aggregated heatmap.
    Each layer is assumed to be a 2D numpy array.
    """
    # Ensure same shape
    base_shape = layers[0].shape
    stacked = np.zeros(base_shape, dtype=float)

    for layer in layers:
        if layer.shape != base_shape:
            print(f"Skipping map with shape {layer.shape}, doesn't match {base_shape}")
            continue
        if skip_zero:
            mask = layer > 0
            stacked[mask] += 1
        else:
            stacked += layer

    if smooth:
        stacked = gaussian_filter(stacked, sigma=sigma)

    return stacked

def plot_zombie_heatmap(heatmap, title="Combined Zombie Heatmap"):
    plt.figure(figsize=(8, 8))
    plt.imshow(heatmap, cmap="inferno", norm=Normalize(vmin=0, vmax=np.max(heatmap)))
    plt.title(title)
    plt.colorbar(label="Zombie Presence Frequency")
    plt.tight_layout()
    plt.show()

# === Main ===
if __name__ == "__main__":
    from CampaignMapEditor import CustomMap  # ensure your module is imported correctly

    saves_dir = r"C:\Users\joshu\OneDrive\Documents\My Games\They Are Billions\Saves"
    game_dir = r"D:\Steam\steamapps\common\They Are Billions"
    sevenzip_exe = r"C:\Program Files\7-Zip\7z.exe"
    passwords = r"D:\Steam\steamapps\common\They Are Billions\passwords.txt"

    maps = get_maps(saves_dir)
    print(f"Number of maps found: {len(maps)}")

    zombie_layers = []
    all_stats = []

    for map_path in maps:
        print(f"Processing: {os.path.basename(map_path)}")

        try:
            map_data = CustomMap(game_dir, map_path, sevenzip_exe, passwords)
            zombie_layer = map_data.layers[3]  # 3 = LayerZombies
            zombie_layers.append(zombie_layer)

            stats = summarize_layer(zombie_layer, LayerZombies)
            all_stats.append(stats)
        except Exception as e:
            print(f"Failed to process {map_path}: {e}")

    if not zombie_layers:
        print("No valid maps found.")
    else:
        print(f"Building combined heatmap from {len(zombie_layers)} maps...")
        heatmap = build_zombie_heatmap(zombie_layers, skip_zero=True, smooth=True, sigma=4)
        plot_zombie_heatmap(heatmap, "Combined Zombie Heatmap (All Maps)")

        # Optional: show combined counts summary
        combined_counts = {}
        for stats in all_stats:
            for k, v in stats.items():
                combined_counts[k] = combined_counts.get(k, 0) + v

        print("\n=== Combined Zombie Type Totals ===")
        for name, count in sorted(combined_counts.items(), key=lambda x: -x[1]):
            print(f"{name:20} {count:10d}")
