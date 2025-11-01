import os
from fetch_citation_info import get_citation_data_by_orcid
from create_citation_map import create_citation_map

# --- 1. Configuration ---
# !!! REPLACE WITH YOUR OWN INFORMATION !!!
YOUR_ORCID = "0000-0002-XXXX-XXXX"
YOUR_EMAIL = "your_email@example.com"
CSV_FILENAME = "citation_info.csv"

# --- 2. Fetch Data (Optional) ---
# Uncomment the lines below if the CSV file doesn't exist or you want to refresh it.
# get_citation_data_by_orcid(
#     orcid=YOUR_ORCID, 
#     output_csv=CSV_FILENAME, 
#     email=YOUR_EMAIL
# )

# --- 3. Run Map Examples ---
if not os.path.exists(CSV_FILENAME):
    print(f"Error: '{CSV_FILENAME}' not found.")
    print("Please run the 'Fetch Data' step above to create this file.")
else:
    print(f"Loading data from '{CSV_FILENAME}' to generate maps...")

    # --- Example: Simple Mode (Green) with Scaled Pins ---
    print("Running Example: Simple Green with Pins...")
    create_citation_map(
        CSV_FILENAME,
        output_filename='figs/map_ex_simple_green_with_pin.png',
        scale='log_rank', # Use rank scale for pins
        fill_mode='simple',
        fill_alpha=0.7,
        fill_color='#B5E48C', # Light green fill
        show_pins=True,
        pin_cmap='YlGn',     # Use a green heatmap for pins
        pin_scale_color=True,  # Scale pin color
        pin_scale_size=True,   # Scale pin size
        pin_scale_alpha=False,  # Use static alpha for pins
        pin_size_range=(30, 250),
        show_legend=True,
    )

    # --- Example 1: Simple Mode (Blue) ---
    print("Running Example 1: Simple Blue...")
    create_citation_map(
        CSV_FILENAME,
        output_filename='figs/map_ex1_simple_blue.png',
        fill_mode='simple',
        fill_color='#0077B6', # Use a blue fill
        show_legend=True,
    )

    # --- Example 2: Heatmap Mode (Red) with Pins ---
    print("Running Example 2: Heatmap with Red Pins...")
    create_citation_map(
        CSV_FILENAME,
        output_filename='figs/map_ex2_heatmap_with_Reds_cmap_with_pin.png',
        scale='log_rank',
        fill_mode='heatmap',
        fill_cmap='Reds',
        show_pins=True,
        pin_color='#333333',   # Dark grey pins
        pin_scale_alpha=False,   # Use Static alpha
        show_legend=True,
    )

    # --- Example 3: Heatmap Mode (Blue) with Labels ---
    print("Running Example 3: Heatmap with Labels...")
    create_citation_map(
        CSV_FILENAME,
        output_filename='figs/map_ex3_heatmap_with_label.png',
        scale='log_rank',
        fill_mode='heatmap',
        fill_cmap='Blues',
        show_labels=True,
        show_legend=True,
    )
    
    print("\nAll map examples generated!")