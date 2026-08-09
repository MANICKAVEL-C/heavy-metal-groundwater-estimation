# ============================================================
# folium_map.py - Interactive contamination map with Folium
# Project: AI-Driven Assessment of Heavy Metal Pollution Indices
# ============================================================
#
# WHAT THIS MODULE DOES:
# Replaces/complements the static Matplotlib Kriging plot with a
# real interactive map (zoom, pan, click). It:
#   1. Loads the 44 sample locations (with real lat/long + HPI)
#   2. Re-runs Ordinary Kriging to build a contamination-risk grid
#      AND a prediction-uncertainty grid
#   3. Renders both grids as semi-transparent image overlays on
#      an OpenStreetMap base layer, with a toggle to switch between
#      them (folium.LayerControl)
#   4. Adds a clickable marker per sample location with a popup
#      showing that location's historical reading (HPI, category,
#      season, key metals) - the "historical testing data" feature
# ============================================================

import numpy as np
import pandas as pd
import folium
from folium.raster_layers import ImageOverlay
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from pykrige.ok import OrdinaryKriging
from io import BytesIO
import base64
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "tamilnadu_groundwater_WITH_INDICES.csv")

CATEGORY_COLOR = {"Safe": "#5FA37A", "Moderate": "#C99A44", "Highly Polluted": "#C4602F"}


def _fig_to_overlay_png(fig):
    """Convert a matplotlib figure (transparent bg) to a base64 PNG data URI."""
    buf = BytesIO()
    fig.savefig(buf, format="png", transparent=True, dpi=110, bbox_inches=None, pad_inches=0)
    plt.close(fig)
    buf.seek(0)
    return "data:image/png;base64," + base64.b64encode(buf.read()).decode()


def build_kriging_grids(df_season):
    """Runs Ordinary Kriging and returns (risk_grid, uncertainty_grid, bounds)."""
    lons = df_season["Longitude"].values
    lats = df_season["Latitude"].values
    hpi = df_season["HPI"].values

    grid_lon = np.linspace(lons.min() - 0.03, lons.max() + 0.03, 120)
    grid_lat = np.linspace(lats.min() - 0.03, lats.max() + 0.03, 120)

    ok_model = OrdinaryKriging(lons, lats, hpi, variogram_model="spherical",
                                 verbose=False, enable_plotting=False)
    z_grid, ss_grid = ok_model.execute("grid", grid_lon, grid_lat)

    bounds = [[grid_lat.min(), grid_lon.min()], [grid_lat.max(), grid_lon.max()]]
    return grid_lon, grid_lat, z_grid, ss_grid, bounds


def render_risk_overlay(grid_lon, grid_lat, z_grid):
    fig, ax = plt.subplots(figsize=(6, 6))
    fig.patch.set_alpha(0)
    ax.axis("off")
    ax.set_position([0, 0, 1, 1])
    cmap = mcolors.LinearSegmentedColormap.from_list("risk", ["#5FA37A", "#C99A44", "#C4602F"])
    ax.contourf(grid_lon, grid_lat, z_grid, levels=20, cmap=cmap, alpha=0.55)
    return _fig_to_overlay_png(fig)


def render_uncertainty_overlay(grid_lon, grid_lat, ss_grid):
    fig, ax = plt.subplots(figsize=(6, 6))
    fig.patch.set_alpha(0)
    ax.axis("off")
    ax.set_position([0, 0, 1, 1])
    ax.contourf(grid_lon, grid_lat, np.sqrt(ss_grid), levels=20, cmap="Blues", alpha=0.55)
    return _fig_to_overlay_png(fig)


def build_interactive_map(season="Post-Monsoon"):
    """
    Main entry point - builds and returns a Folium Map object with:
    - OpenStreetMap base layer
    - Contamination risk overlay (toggleable)
    - Prediction uncertainty overlay (toggleable)
    - One marker per sample location with a historical-data popup
    """
    df = pd.read_csv(DATA_PATH)
    df_season = df[df["Season"] == season].reset_index(drop=True)

    grid_lon, grid_lat, z_grid, ss_grid, bounds = build_kriging_grids(df_season)
    risk_png = render_risk_overlay(grid_lon, grid_lat, z_grid)
    unc_png = render_uncertainty_overlay(grid_lon, grid_lat, ss_grid)

    center_lat = df_season["Latitude"].mean()
    center_lon = df_season["Longitude"].mean()

    fmap = folium.Map(location=[center_lat, center_lon], zoom_start=12,
                        tiles="OpenStreetMap", control_scale=True)

    folium.TileLayer("Esri.WorldImagery", name="Satellite View").add_to(fmap)

    ImageOverlay(
        image=risk_png, bounds=bounds, opacity=0.65,
        name="Contamination Risk Heatmap", overlay=True, control=True,
    ).add_to(fmap)

    ImageOverlay(
        image=unc_png, bounds=bounds, opacity=0.65,
        name="Prediction Uncertainty Map", overlay=True, control=True, show=False,
    ).add_to(fmap)

    # Clickable markers with historical-data popup per location
    for _, row in df_season.iterrows():
        color = CATEGORY_COLOR.get(row["Safety_Category"], "#2A9D8F")
        popup_html = f"""
        <div style="font-family: sans-serif; font-size: 13px; min-width:200px;">
            <b>{row['Location']}</b><br>
            <b>Season:</b> {row['Season']}<br>
            <b>HPI:</b> {row['HPI']:.1f}<br>
            <b>Category:</b> <span style="color:{color}; font-weight:bold;">{row['Safety_Category']}</span><br>
            <hr style="margin:4px 0;">
            <b>Cd:</b> {row['Cd']:.4f} mg/L &nbsp; <b>Pb:</b> {row['Pb']:.4f} mg/L<br>
            <b>Fe:</b> {row['Fe']:.3f} mg/L &nbsp; <b>Mn:</b> {row['Mn']:.3f} mg/L<br>
            <b>pH:</b> {row['pH']:.2f} &nbsp; <b>TDS:</b> {row['TDS']:.0f} mg/L
        </div>
        """
        folium.CircleMarker(
            location=[row["Latitude"], row["Longitude"]],
            radius=7, color="#0A1418", weight=1.5,
            fill=True, fill_color=color, fill_opacity=0.9,
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=f"{row['Location']} ({row['Safety_Category']})",
        ).add_to(fmap)

    folium.LayerControl(collapsed=False).add_to(fmap)
    return fmap
