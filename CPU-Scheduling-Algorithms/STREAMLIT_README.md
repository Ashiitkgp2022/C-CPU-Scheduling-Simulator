# CPU Scheduling Algorithms Visualizer

A comprehensive Streamlit web application for visualizing and analyzing CPU scheduling algorithms.

## Features

### 🎯 **Supported Algorithms**
- **FCFS** (First Come First Serve)
- **RR** (Round Robin) with configurable quantum
- **SPN** (Shortest Process Next)
- **SRT** (Shortest Remaining Time)
- **HRRN** (Highest Response Ratio Next)
- **FB-1** (Feedback Queue 1)
- **FB-2i** (Feedback Queue 2^i)
- **AGING** (Aging Algorithm)

### 📊 **Visualization Modes**
1. **Timeline Trace**: Interactive Gantt charts showing process execution timeline
2. **Statistical Analysis**: Comprehensive performance metrics and comparisons

### 🔧 **Interactive Features**
- Configure process arrival and service times
- Select multiple algorithms for comparison
- Adjustable timeline length
- Real-time visualization updates
- Performance metrics calculation

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- Windows operating system (due to executable dependency)

### Quick Setup
1. **Run the installer** (recommended):
   ```bash
   double-click install_requirements.bat
   ```

2. **Manual installation**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Starting the Application
1. **Easy launch** (recommended):
   ```bash
   double-click run_app.bat
   ```

2. **Manual launch**:
   ```bash
   streamlit run streamlit_app.py
   ```

### Using the Interface

#### 1. Configuration (Sidebar)
- **Operation Mode**: Choose between "trace" (timeline) or "stats" (statistics)
- **Algorithm Selection**: Check the algorithms you want to run
- **Process Configuration**: Set the number of processes and timeline length
- **Process Details**: Configure arrival and service times for each process

#### 2. Running Simulation
- Click the "🚀 Run Simulation" button
- Results will appear in the main area

#### 3. Viewing Results

**Timeline Mode (`trace`):**
- Interactive Gantt charts showing when each process runs
- Color-coded process execution
- Expandable raw timeline view

**Statistics Mode (`stats`):**
- Detailed performance tables
- Key metrics (mean turnaround time, normalized turnaround)
- Algorithm comparison charts (when multiple algorithms selected)

## Key Metrics Explained

- **Arrival Time**: When the process enters the system
- **Service Time**: Total CPU time required by the process
- **Finish Time**: When the process completes execution
- **Turnaround Time**: Total time from arrival to completion
- **Normalized Turnaround**: Turnaround time divided by service time

## Example Usage

### Basic FCFS Analysis
1. Select "FCFS" algorithm
2. Choose "stats" mode
3. Configure 3-5 processes with different arrival times
4. Run simulation to see performance metrics

### Algorithm Comparison
1. Select multiple algorithms (e.g., FCFS, RR, SPN)
2. Set Round Robin quantum if selected
3. Choose "stats" mode
4. Run simulation to see comparison charts

### Timeline Visualization
1. Select any algorithm
2. Choose "trace" mode
3. Run simulation to see Gantt chart timeline

## Technical Details

### Architecture
- **Frontend**: Streamlit web interface
- **Backend**: C++ executable (`lab4.exe`) for algorithm implementation
- **Visualization**: Plotly charts for interactive graphics
- **Data Processing**: Pandas for statistical analysis

### File Structure
```
├── streamlit_app.py          # Main Streamlit application
├── lab4.exe                  # C++ scheduling algorithms executable
├── main.cpp                  # C++ source code
├── parser.h                  # Input parsing header
├── requirements.txt          # Python dependencies
├── install_requirements.bat  # Installation script
├── run_app.bat              # Launch script
└── testcases/               # Sample input/output files
```

## Troubleshooting

### Common Issues

**"Streamlit not found" error:**
- Run `install_requirements.bat` to install dependencies
- Ensure Python is installed and in PATH

**"lab4.exe not found" error:**
- Ensure you're running from the correct directory
- The executable should be in the same folder as the Python script

**Input parsing errors:**
- Check that arrival times are non-negative
- Ensure service times are positive integers
- Verify process count matches the number of configured processes

### Performance Tips
- Use reasonable timeline lengths (10-50 units) for better visualization
- Limit number of processes (1-10) for clearer charts
- Compare 2-4 algorithms at once for optimal readability

## Advanced Features

### Custom Process Configurations
- Configure up to 10 processes (A through J)
- Set individual arrival and service times
- Preview input before running simulation

### Algorithm-Specific Settings
- **Round Robin**: Configure quantum value (1-20)
- **Feedback Queues**: Automatic quantum management
- **Aging**: Built-in priority adjustment

### Export Options
- Save Plotly charts as images
- Copy statistical data from tables
- Export raw timeline data

## Contributing

This visualizer interfaces with existing C++ scheduling algorithm implementations. To modify algorithms:

1. Edit `main.cpp` for algorithm logic
2. Recompile to generate new `lab4.exe`
3. Update algorithm mappings in `streamlit_app.py` if needed

## License

This project builds upon existing CPU scheduling algorithm implementations and adds a modern web-based visualization layer.

---

**Happy Scheduling! 🚀**
