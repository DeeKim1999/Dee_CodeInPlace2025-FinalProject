#
# Dee's Flappy Bird Game: Data Analytics Dashboard (CiP2025 version 1.0)
#
# My code here is an integral part of Dee's Flappy Bird project that serves as the
# dedicated data analytics and visualization component. It reads the game performance
# data logged by `dee_main.py` and generates insightful graphical representations.
#
# Purpose:
# - To provide a visual overview of player performance trends over time.
# - To analyze the distribution of game durations to help understand typical game lengths.
#
# How it Works:
# 1. It locates and loads the `game_log.csv` file that contains records of
#    each game played (timestamp, score, duration).
# 2. It uses the pandas library to efficiently process and clean this data.
# 3. It leverages Matplotlib to create two types of plots:
#    - A line plot showing how scores have changed across different game sessions.
#    - A histogram illustrating the frequency distribution of game durations.
# 4. The plots are displayed in separate windows for easy viewing and analysis.
#
# Libraries Used:
# - pandas: For robust data loading, cleaning, and manipulation (especially with CSVs).
# - matplotlib.pyplot: For creating high-quality static, interactive, and animated visualizations.
# - os: For navigating file paths to locate the game log.
#
# To Run:
# This script is typically launched automatically from `dee_main.py` when the
# "View Graphs" button is clicked or the 'G' key is pressed on the statistics screen.
# It can also be run independently for direct data analysis: `python dee_dashboard.py`

import pandas as pd         
import matplotlib.pyplot as plt 
import os                   

# --- Constants for File Paths ---
# Determine the base directory of the project.
# os.path.dirname(__file__) gets the directory of the current script (dee_dashboard.py).
# os.path.dirname(os.path.dirname(__file__)) goes up two levels to the project root
# (dee_dashboard.py is in Dee_FinalProject/dee_analysis/).
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dee_data")
GAME_LOG_FILE = os.path.join(DATA_PATH, "game_log.csv") # Full path to the game log CSV file

def load_game_data():
    """
    Loads game data from the CSV log file into a pandas DataFrame.
    Performs data cleaning and type conversion.
    Returns an empty DataFrame if the file doesn't exist or data is invalid.
    """
    if not os.path.exists(GAME_LOG_FILE):
        print(f"Error: Game log file not found at {GAME_LOG_FILE}")
        return pd.DataFrame() # Return empty DataFrame if file is missing

    try:
        # Read the CSV file into a DataFrame
        # 'parse_dates' converts the 'timestamp' column to datetime objects
        df = pd.read_csv(GAME_LOG_FILE, parse_dates=['timestamp'])
        
        # Convert 'score' and 'duration_seconds' columns to numeric.
        # 'errors="coerce"' will turn any non-numeric values into NaN (Not a Number).
        df['score'] = pd.to_numeric(df['score'], errors='coerce')
        df['duration_seconds'] = pd.to_numeric(df['duration_seconds'], errors='coerce')
        
        # Drop rows where 'score' or 'duration_seconds' are NaN (i.e., invalid entries)
        df.dropna(subset=['score', 'duration_seconds'], inplace=True)
        
        return df # Return the cleaned DataFrame
    
    except pd.errors.EmptyDataError:
        print("Game log is empty, no data to plot.")
        return pd.DataFrame() # Return empty DataFrame if CSV is empty
    except Exception as e:
        print(f"Error loading game data for dashboard: {e}")
        return pd.DataFrame() # Return empty DataFrame for other loading errors

def plot_game_statistics():
    """
    Generates and displays various statistical plots based on the game log data.
    Includes: Scores Over Time (line plot) and Game Duration Distribution (histogram).
    """
    df = load_game_data() # Load the game data

    if df.empty:
        print("No data available to generate plots.")
        return # Exit if no valid data was loaded

    # --- Plot 1: Scores Over Time ---
    # Create the first figure and an axes object for the plot.
    # Set the window title for this specific figure using the 'num' argument.
    fig1 = plt.figure("Dee's Flappy Bird: Scores Over Time", figsize=(10, 6))
    ax1 = fig1.add_subplot(111) # 1x1 grid, first subplot

    # Plot scores against timestamp
    ax1.plot(df['timestamp'], df['score'], marker='o', linestyle='-', color='skyblue')
    
    # Set plot title and labels
    ax1.set_title('Game Scores Trend Over Time', fontsize=14)
    ax1.set_xlabel('Date and Time Played', fontsize=12)
    ax1.set_ylabel('Score', fontsize=12)
    
    # Add a grid for readability
    # Automatically format x-axis labels for dates (rotate them -- dee)
    ax1.grid(True, linestyle='--', alpha=0.7) 
    fig1.autofmt_xdate() 
    
    # Notes to self -- dee
    # You can explicitly set the window title after creation if needed (to change it dynamically)
    # like this as an example: fig1.canvas.manager.set_window_title("Detailed Score History")

    # --- Plot 2: Game Duration Distribution (Histogram) ---
    # Create the second figure and an axes object.
    # Set the window title for this figure.
    fig2 = plt.figure("Dee's Flappy Bird: Game Duration Distribution", figsize=(10, 6))
    ax2 = fig2.add_subplot(111) # 1x1 grid, first subplot

    # Plot a histogram of game durations
    # 'bins' defines the number of bars, 'edgecolor' for bar borders, 'alpha' for transparency
    ax2.hist(df['duration_seconds'], bins=10, edgecolor='black', alpha=0.7, color='lightcoral')
    
    # Set plot title and labels
    ax2.set_title('Distribution of Game Durations (Seconds)', fontsize=14)
    ax2.set_xlabel('Duration (Seconds)', fontsize=12)
    ax2.set_ylabel('Number of Games', fontsize=12)
    
    # Add a grid for readability
    ax2.grid(True, linestyle='--', alpha=0.7) 

    # --- Display Plots ---
    plt.tight_layout()
    plt.show()

# --- Main execution block ---
# This confirms that plot_game_statistics() is called only when the script is executed directly,
# not when it's imported as a module.
if __name__ == "__main__":
    plot_game_statistics()