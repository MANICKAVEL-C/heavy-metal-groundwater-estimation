# ==============================================================================
# folium_map.py - Interactive Contamination & Kriging Geospatial Map
# Project: AI-Driven Assessment of Heavy Metal Pollution Indices
# ==============================================================================

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
CATEGORY_COLOR = {"Safe": "#5C9271", "Moderate": "#C99A44", "Highly Polluted": "#C4602F"}

def _fig_to_overlay_png(fig):
    """Convert a matplotlib figure to a base64 PNG data URI."""
    buf = BytesIO()
    fig.savefig(buf, format="png", transparent=True, dpi=110, bbox_inches=None, pad_inches=0)
    plt.close(fig)
    buf.seek(0)
    return "data:image/png;base64," + base64.b64encode(buf.read()).decode()

def build_kriging_grids(df_season):
    """Runs Ordinary Kriging and returns (grid_lon, grid_lat, z_grid, ss_grid, bounds)."""
    lons = df_season["Longitude"].values
    lats = df_season["Latitude"].values
    hpi = df_season["HPI"].values

    grid_lon = np.linspace(lons.min() - 0.03, lons.max() + 0.03, 120)
    grid_lat = np.linspace(lats.min() - 0.03, lats.max() + 0.03, 120)

    ok_model = OrdinaryKriging(
        lons, lats, hpi, variogram_model="spherical",
        verbose=False, enable_plotting=False
    )
    z_grid, ss_grid = ok_model.execute("grid", grid_lon, grid_lat)
    bounds = [[grid_lat.min(), grid_lon.min()], [grid_lat.max(), grid_lon.max()]]
    return grid_lon, grid_lat, z_grid, ss_grid, bounds

def render_risk_overlay(grid_lon, grid_lat, z_grid):
    fig, ax = plt.subplots(figsize=(6, 6))
    fig.patch.set_alpha(0)
    ax.axis("off")
    ax.set_position([0, 0, 1, 1])
    cmap = mcolors.LinearSegmentedColormap.from_list("risk", ["#5C9271", "#C99A44", "#C4602F"])
    ax.contourf(grid_lon, grid_lat, z_grid, levels=20, cmap=cmap, alpha=0.55)
    return _fig_to_overlay_png(fig)

def render_uncertainty_overlay(grid_lon, grid_lat, ss_grid):
    fig, ax = plt.subplots(figsize=(6, 6))
    fig.patch.set_alpha(0)
    ax.axis("off")
    ax.set_position([0, 0, 1, 1])
    ax.contourf(grid_lon, grid_lat, np.sqrt(ss_grid), levels=20, cmap="Blues", alpha=0.55)
    return _fig_to_overlay_png(fig)

def build_interactive_map(season: str = "Post-Monsoon", custom_df: pd.DataFrame = None):
    """
    Builds an interactive Folium Map supporting both historical baseline
    readings and dynamic batch uploaded survey locations.
    """
    df = pd.read_csv(DATA_PATH)
    df_season = df[df["Season"] == season].reset_index(drop=True)

    grid_lon, grid_lat, z_grid, ss_grid, bounds = build_kriging_grids(df_season)
    risk_png = render_risk_overlay(grid_lon, grid_lat, z_grid)
    unc_png = render_uncertainty_overlay(grid_lon, grid_lat, ss_grid)

    center_lat = df_season["Latitude"].mean()
    center_lon = df_season["Longitude"].mean()

    fmap = folium.Map(
        location=[center_lat, center_lon], zoom_start=12,
        tiles="OpenStreetMap", control_scale=True
    )

    folium.TileLayer("Esri.WorldImagery", name="Satellite View").add_to(fmap)

    # Kriging Contamination Overlay
    ImageOverlay(
        image=risk_png, bounds=bounds, opacity=0.65,
        name="Contamination Risk Heatmap (Kriging)", overlay=True, control=True
    ).add_to(fmap)

    # Uncertainty Layer
    ImageOverlay(
        image=unc_png, bounds=bounds, opacity=0.65,
        name="Prediction Uncertainty Map", overlay=True, control=True, show=False
    ).add_to(fmap)

    # Plot Historical Sample Markers
    for _, row in df_season.iterrows():
        color = CATEGORY_COLOR.get(row.get("Safety_Category", "Safe"), "#2A9D8F")
        popup_html = f"""
        <div style="font-family: sans-serif; font-size: 12px; min-width:200px;">
            <b style="font-size:13px;">{row.get('Location', 'Borewell')}</b><br>
            <b>Season:</b> {row.get('Season', 'N/A')}<br>
            <b>HPI Score:</b> {row.get('HPI', 0.0):.1f}<br>
            <b>Category:</b> <span style="color:{color}; font-weight:bold;">{row.get('Safety_Category', 'Safe')}</span><br>
            <hr style="margin:4px 0;">
            <b>Cd:</b> {row.get('Cd', 0.0):.4f} mg/L | <b>Pb:</b> {row.get('Pb', 0.0):.4f} mg/L<br>
            <b>Fe:</b> {row.get('Fe', 0.0):.3f} mg/L | <b>Mn:</b> {row.get('Mn', 0.0):.3f} mg/L<br>
            <b>pH:</b> {row.get('pH', 0.0):.2f} | <b>TDS:</b> {row.get('TDS', 0.0):.0f} mg/L
        </div>
        """
        folium.CircleMarker(
            location=[row["Latitude"], row["Longitude"]],
            radius=6.5, color="#0A1418", weight=1.5,
            fill=True, fill_color=color, fill_opacity=0.9,
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=f"{row.get('Location', 'Borewell')} ({row.get('Safety_Category', 'Safe')})"
        ).add_to(fmap)

    # Plot Custom Batch Uploaded Markers if present
    if custom_df is not None and not custom_df.empty:
        batch_group = folium.FeatureGroup(name="Batch Uploaded Survey Points")
        for idx, row in custom_df.iterrows():
            if "Latitude" in row and "Longitude" in row and pd.notnull(row["Latitude"]) and pd.notnull(row["Longitude"]):
                cat = row.get("Safety_Category", "Safe")
                c = CATEGORY_COLOR.get(cat, "#2A9D8F")
                hpi_val = row.get("HPI", row.get("Predicted_HPI", 0.0))
                popup_batch = f"""
                <div style="font-family: sans-serif; font-size: 12px; min-width:200px;">
                    <b style="font-size:13px; color:#2A9D8F;">[SURVEY] {row.get('Location', f'Sample #{idx+1}')}</b><br>
                    <b>Predicted HPI:</b> {hpi_val:.1f}<br>
                    <b>Category:</b> <span style="color:{c}; font-weight:bold;">{cat}</span><br>
                    <b>pH:</b> {row.get('pH', 'N/A')} | <b>TDS:</b> {row.get('TDS', 'N/A')} ppm
                </div>
                """
                folium.Marker(
                    location=[row["Latitude"], row["Longitude"]],
                    popup=folium.Popup(popup_batch, max_width=280),
                    tooltip=f"Survey: {row.get('Location', f'Point #{idx+1}')}",
                    icon=folium.Icon(color="red" if cat == "Highly Polluted" else ("orange" if cat == "Moderate" else "green"), icon="tint")
                ).add_to(batch_group)
        batch_group.add_to(fmap)

    folium.LayerControl(collapsed=False).add_to(fmap)
    return fmap
