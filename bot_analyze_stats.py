import os
import numpy as np
import math
import matplotlib.pyplot as plt
from collections import defaultdict
import CampaignMapEditor
from matplotlib.colors import ListedColormap, BoundaryNorm


def distance_stats(points):
    # Parse 'x;y' strings into float tuples
    coords = [tuple(map(float, p.split(';'))) for p in points]
    n = len(coords)
    if n < 2:
        return 0.0, 0.0, 0.0  # avg, min, max

    dists = []
    for i in range(n):
        x1, y1 = coords[i]
        for j in range(i + 1, n):
            x2, y2 = coords[j]
            dists.append(math.hypot(x2 - x1, y2 - y1))

    return np.mean(dists), np.min(dists), np.max(dists)

# === Main ===
if __name__ == "__main__":
    path = r'C:\Users\joshu\OneDrive\Desktop\Gen'
    folders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]

    per_map_averages = []

    for map_dir in folders:
        try:
            map_file = fr'{path}\{map_dir}\{map_dir}.sav'
            password = fr'{path}\{map_dir}\{map_dir}.pass'
            map_data = CampaignMapEditor.CustomMap(
                r"D:\Steam\steamapps\common\They Are Billions",
                map_file,
                r"C:\Program Files\7-Zip\7z.exe",
                password
            )

            # Collect all mutant/giant locations for this map
            locations = []
            for entity in map_data.entities:
                template = map_data.entities[entity]['template'][0]
                if 'Mutant' in template or "Giant" in template:
                    locations.append(map_data.entities[entity]['Position'])

            # Compute distance stats for this map
            avg, min_d, max_d = distance_stats(locations)
            print(f"{map_dir}: Avg={avg:.2f}, Min={min_d:.2f}, Max={max_d:.2f}")

            if avg > 0:
                per_map_averages.append(avg)

        except Exception as e:
            print(f"Skipping {map_dir}: {e}")

    # === Compute overall mean and stddev across maps ===
    if per_map_averages:
        overall_mean = np.mean(per_map_averages)
        overall_stddev = np.std(per_map_averages)
        print("\n=== Summary Across All Maps ===")
        print(f"Mean of map averages: {overall_mean:.2f}")
        print(f"Standard deviation:  {overall_stddev:.2f}")
    else:
        print("No valid maps found.")
    

