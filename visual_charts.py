# ==============================================================================
# visual_charts.py - Advanced Data Visualizations for Groundwater Analytics
# Supports both Light (Scientific Lab) and Dark (Instrument Panel) Themes
# Includes: HPI Gauge, Metal Radar Chart, SHAP Waterfall & Summary Plots
# ==============================================================================

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import shap

def get_chart_theme(theme_mode: str = "Dark"):
    if theme_mode.lower() == "light":
        return {
            "bg": "#FFFFFF",
            "card_bg": "#F8FAFB",
            "text": "#0F1F27",
            "text_muted": "#536A77",
            "border": "#D0DEE5",
            "accent": "#147A6E",
            "safe": "#2E7D52",
            "moderate": "#A86F12",
            "danger": "#B83A14"
        }
    else:
        return {
            "bg": "#13242C",
            "card_bg": "#0A1418",
            "text": "#E8EEF0",
            "text_muted": "#8AA0AD",
            "border": "#234049",
            "accent": "#2A9D8F",
            "safe": "#5FA37A",
            "moderate": "#C99A44",
            "danger": "#C4602F"
        }

def render_hpi_gauge(hpi_value: float, theme_mode: str = "Dark"):
    """
    Renders an analog gauge / speedometer for HPI pollution index.
    Zones: Safe (0 - 30), Moderate (30 - 70), Critical Hazard (70 - 100+)
    """
    theme = get_chart_theme(theme_mode)
    
    fig, ax = plt.subplots(figsize=(5.5, 3.0), subplot_kw={'projection': 'polar'})
    fig.patch.set_facecolor(theme["bg"])
    ax.set_facecolor(theme["bg"])

    # Gauge background arcs
    ax.bar(x=np.pi*5/6, height=0.4, width=np.pi/3, bottom=0.6, color=theme["safe"], alpha=0.85, edgecolor=theme["bg"], linewidth=2)
    ax.bar(x=np.pi/2,   height=0.4, width=np.pi/3, bottom=0.6, color=theme["moderate"], alpha=0.85, edgecolor=theme["bg"], linewidth=2)
    ax.bar(x=np.pi/6,   height=0.4, width=np.pi/3, bottom=0.6, color=theme["danger"], alpha=0.85, edgecolor=theme["bg"], linewidth=2)

    # Clamped HPI for needle angle
    clamped_hpi = max(0.0, min(100.0, hpi_value))
    needle_angle = np.pi - (clamped_hpi / 100.0) * np.pi

    # Needle
    ax.annotate('', xytext=(0, 0), xy=(needle_angle, 0.92),
                arrowprops=dict(arrowstyle="->", color=theme["text"], lw=3.2))
    
    # Center circle hub
    hub = patches.Circle((0, 0), 0.15, transform=ax.transData._b, color=theme["accent"], zorder=10)
    ax.add_patch(hub)

    ax.set_theta_zero_location('E')
    ax.set_theta_direction(-1)
    ax.set_thetamin(0)
    ax.set_thetamax(180)
    ax.set_yticklabels([])
    ax.set_xticks([np.pi, np.pi*2/3, np.pi/3, 0])
    ax.set_xticklabels(['0 (Safe)', '30 (Mod)', '70 (Alert)', '100+ (Crit)'], color=theme["text_muted"], fontsize=8, fontweight="bold")
    ax.grid(False)
    ax.spines['polar'].set_visible(False)

    # Text overlay
    ax.text(np.pi/2, 0.25, f"HPI {hpi_value:.1f}", color=theme["text"], fontsize=15, fontweight="bold", ha='center', va='center')
    
    plt.tight_layout(pad=0.2)
    return fig

def render_metal_radar_chart(metals: dict, standards: dict, theme_mode: str = "Dark"):
    """
    Renders a Spider / Radar chart comparing measured heavy metal concentrations
    normalized against BIS IS 10500 permissible standard limits (Si = 1.0 threshold line).
    """
    theme = get_chart_theme(theme_mode)
    
    categories = [m for m in ["Cd", "Pb", "Fe", "Mn", "Cu", "Zn", "Ni"] if m in metals and m in standards]
    if len(categories) < 3:
        return None
        
    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    
    ratios = [min(3.5, metals[m] / standards[m]["Si"]) for m in categories]
    ratios += ratios[:1]
    threshold_line = [1.0] * (N + 1)
    
    fig, ax = plt.subplots(figsize=(4.8, 3.8), subplot_kw={'projection': 'polar'})
    fig.patch.set_facecolor(theme["bg"])
    ax.set_facecolor(theme["bg"])
    
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    
    plt.xticks(angles[:-1], categories, color=theme["text"], fontsize=9, fontweight="bold")
    ax.tick_params(colors=theme["text_muted"])
    
    # Draw BIS standard threshold circle
    ax.plot(angles, threshold_line, color=theme["safe"], linewidth=1.8, linestyle='--', label="BIS IS 10500 Limit (1.0x)")
    ax.fill(angles, threshold_line, color=theme["safe"], alpha=0.08)
    
    # Draw Sample Polygon
    ax.plot(angles, ratios, color=theme["accent"], linewidth=2.2, label="Sample Ratio")
    ax.fill(angles, ratios, color=theme["accent"], alpha=0.35)
    
    ax.set_rlabel_position(0)
    plt.yticks([0.5, 1.0, 2.0, 3.0], ["0.5x", "1.0x (Limit)", "2.0x", "3.0x+"], color=theme["text_muted"], fontsize=7)
    plt.ylim(0, 3.5)
    
    ax.spines['polar'].set_color(theme["border"])
    ax.grid(color=theme["border"], linestyle=':')
    
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), facecolor=theme["bg"], edgecolor=theme["border"], labelcolor=theme["text"], fontsize=7.5)
    plt.tight_layout(pad=0.2)
    return fig

# Cached TreeExplainer instance
_explainer_cache = {}

def _get_tree_explainer(model):
    m_id = id(model)
    if m_id not in _explainer_cache:
        _explainer_cache[m_id] = shap.TreeExplainer(model)
    return _explainer_cache[m_id]

def render_shap_waterfall_chart(model, X_sample, theme_mode: str = "Dark"):
    """
    Renders an authentic SHAP Waterfall Plot explaining local feature contributions
    (pH, TDS, EC, Season) for a given groundwater sample prediction.
    """
    try:
        theme = get_chart_theme(theme_mode)
        explainer = _get_tree_explainer(model)
        shap_values = explainer(X_sample)
        
        fig, ax = plt.subplots(figsize=(6.8, 3.2))
        fig.patch.set_facecolor(theme["bg"])
        ax.set_facecolor(theme["bg"])
        
        # Use shap waterfall plot
        shap.plots.waterfall(shap_values[0], show=False)
        curr_ax = plt.gca()
        curr_ax.set_facecolor(theme["bg"])
        
        for text in curr_ax.texts:
            text.set_color(theme["text"])
        curr_ax.tick_params(colors=theme["text_muted"])
        for spine in curr_ax.spines.values():
            spine.set_color(theme["border"])
            
        plt.tight_layout(pad=0.2)
        return fig
    except Exception as e:
        print(f"SHAP waterfall rendering error: {e}")
        return None

def render_shap_summary_chart(model, df_background, theme_mode: str = "Dark"):
    """
    Renders global feature impact using SHAP mean absolute values across the dataset.
    """
    try:
        theme = get_chart_theme(theme_mode)
        explainer = _get_tree_explainer(model)
        shap_values = explainer(df_background)
        
        mean_abs_shap = np.abs(shap_values.values).mean(axis=0)
        feature_names = df_background.columns.tolist()
        order = np.argsort(mean_abs_shap)
        
        fig, ax = plt.subplots(figsize=(7.2, 2.8))
        fig.patch.set_facecolor(theme["bg"])
        ax.set_facecolor(theme["bg"])
        
        ax.barh(
            [feature_names[i] for i in order],
            [mean_abs_shap[i] for i in order],
            color=theme["accent"],
            edgecolor=theme["border"]
        )
        ax.set_xlabel("Mean |SHAP value| (Average feature impact on HPI output)", color=theme["text"], fontsize=8.5)
        ax.tick_params(colors=theme["text_muted"])
        for spine in ax.spines.values():
            spine.set_color(theme["border"])
            
        plt.tight_layout(pad=0.2)
        return fig
    except Exception as e:
        print(f"SHAP summary rendering error: {e}")
        return None
