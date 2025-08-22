import streamlit as st
import subprocess
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import tempfile
import os
import re

def parse_timeline(lines, processes):
    """Parse timeline output into structured data"""
    timeline_data = []
    
    # Find the timeline section
    timeline_started = False
    process_lines = []
    
    for line in lines:
        if '----' in line and not timeline_started:
            timeline_started = True
        elif '----' in line and timeline_started:
            break
        elif timeline_started and line.strip() and not line.startswith('0 1 2'):
            process_lines.append(line)
    
    if not process_lines:
        return None
    
    # Parse each process timeline
    for line in process_lines:
        if '|' in line:
            parts = line.split('|')
            if len(parts) >= 2:
                process_name = parts[0].strip()
                timeline = ''.join(parts[1:-1])  # Exclude last empty part
                
                # Extract execution periods
                start_time = None
                for i, char in enumerate(timeline):
                    if char == '*' and start_time is None:
                        start_time = i
                    elif char != '*' and start_time is not None:
                        timeline_data.append({
                            'Process': process_name,
                            'Start': start_time,
                            'Finish': i,
                            'Duration': i - start_time,
                            'Status': 'Running'
                        })
                        start_time = None
                
                # Handle case where process runs until the end
                if start_time is not None:
                    timeline_data.append({
                        'Process': process_name,
                        'Start': start_time,
                        'Finish': len(timeline),
                        'Duration': len(timeline) - start_time,
                        'Status': 'Running'
                    })
    
    return timeline_data

def create_gantt_chart(timeline_data, algorithm_name):
    """Create a Gantt chart from timeline data"""
    fig = go.Figure()
    
    colors = px.colors.qualitative.Set3
    process_colors = {}
    
    for i, item in enumerate(timeline_data):
        process = item['Process']
        if process not in process_colors:
            process_colors[process] = colors[len(process_colors) % len(colors)]
        
        fig.add_trace(go.Bar(
            name=process,
            x=[item['Duration']],
            y=[process],
            base=[item['Start']],
            orientation='h',
            marker_color=process_colors[process],
            text=f"{process}<br>{item['Start']}-{item['Finish']}",
            textposition="middle center",
            showlegend=process not in [trace.name for trace in fig.data]
        ))
    
    fig.update_layout(
        title=f"Timeline for {algorithm_name}",
        xaxis_title="Time Units",
        yaxis_title="Processes",
        barmode='overlay',
        height=300 + len(set(item['Process'] for item in timeline_data)) * 50
    )
    
    return fig

def parse_statistics(section, algorithm_name):
    """Parse statistics output into structured data"""
    lines = section.strip().split('\n')
    
    if len(lines) < 6:
        return None
    
    try:
        # Extract data from each line
        processes = lines[1].split('|')[1:-1]  # Skip first and last empty elements
        processes = [p.strip() for p in processes]
        
        arrivals = [int(x.strip()) for x in lines[2].split('|')[1:-1]]
        services = [int(x.strip()) for x in lines[3].split('|')[1:-2]]  # Exclude 'Mean' column
        finishes = [int(x.strip()) for x in lines[4].split('|')[1:-2]]  # Exclude separator
        
        # Parse turnaround times and mean
        turnaround_parts = lines[5].split('|')[1:]
        turnarounds = [int(x.strip()) for x in turnaround_parts[:-1]]
        mean_turnaround = float(turnaround_parts[-1].strip())
        
        # Parse normalized turnaround times and mean
        normturn_parts = lines[6].split('|')[1:]
        norm_turnarounds = [float(x.strip()) for x in normturn_parts[:-1]]
        mean_normalized = float(normturn_parts[-1].strip())
        
        # Create DataFrame
        stats_df = pd.DataFrame({
            'Process': processes,
            'Arrival Time': arrivals,
            'Service Time': services,
            'Finish Time': finishes,
            'Turnaround Time': turnarounds,
            'Normalized Turnaround': norm_turnarounds
        })
        
        return {
            'algorithm': algorithm_name,
            'table': stats_df,
            'mean_turnaround': mean_turnaround,
            'mean_normalized': mean_normalized,
            'finish_times': finishes
        }
        
    except Exception as e:
        st.error(f"Error parsing statistics for {algorithm_name}: {str(e)}")
        return None

def display_trace_results(output, selected_algorithms, processes):
    """Display trace results with timeline visualization"""
    st.header("📊 Timeline Visualization")
    
    # Split output by algorithms
    sections = output.strip().split('\n\n')
    
    for i, section in enumerate(sections):
        if i < len(selected_algorithms):
            alg_id = selected_algorithms[i]
            alg_name = ALGORITHM_NAMES[alg_id]
            
            if alg_id == '2':
                # Extract quantum from section header
                first_line = section.split('\n')[0]
                if 'RR-' in first_line:
                    quantum_match = re.search(r'RR-(\d+)', first_line)
                    if quantum_match:
                        alg_name += f" (Quantum: {quantum_match.group(1)})"
            
            st.subheader(f"🔄 {alg_name}")
            
            # Parse timeline
            lines = section.strip().split('\n')
            timeline_data = parse_timeline(lines, processes)
            
            if timeline_data:
                # Create Gantt chart
                fig = create_gantt_chart(timeline_data, alg_name)
                st.plotly_chart(fig, use_container_width=True)
                
                # Show raw timeline
                with st.expander("📋 View Raw Timeline"):
                    st.code(section, language="text")

def display_stats_results(output, selected_algorithms, processes):
    """Display statistical results with charts and tables"""
    st.header("📈 Statistical Analysis")
    
    # Split output by algorithms
    sections = output.strip().split('\n\n')
    
    all_stats = []
    
    for i, section in enumerate(sections):
        if i < len(selected_algorithms):
            alg_id = selected_algorithms[i]
            alg_name = ALGORITHM_NAMES[alg_id]
            
            st.subheader(f"📊 {alg_name}")
            
            # Parse statistics
            stats_data = parse_statistics(section, alg_name)
            
            if stats_data:
                all_stats.append(stats_data)
                
                # Display statistics table
                st.dataframe(stats_data['table'], use_container_width=True)
                
                # Show key metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Mean Turnaround Time", f"{stats_data['mean_turnaround']:.2f}")
                with col2:
                    st.metric("Mean Normalized Turnaround", f"{stats_data['mean_normalized']:.2f}")
                with col3:
                    st.metric("Total Completion Time", f"{max(stats_data['finish_times'])}")
    
    # Comparison charts if multiple algorithms
    if len(all_stats) > 1:
        st.header("🔍 Algorithm Comparison")
        create_comparison_charts(all_stats)

def create_comparison_charts(all_stats):
    """Create comparison charts for multiple algorithms"""
    
    # Prepare data for comparison
    comparison_data = []
    for stats in all_stats:
        comparison_data.append({
            'Algorithm': stats['algorithm'],
            'Mean Turnaround Time': stats['mean_turnaround'],
            'Mean Normalized Turnaround': stats['mean_normalized'],
            'Total Completion Time': max(stats['finish_times'])
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    
    # Create comparison charts
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = px.bar(
            comparison_df, 
            x='Algorithm', 
            y='Mean Turnaround Time',
            title="Mean Turnaround Time Comparison",
            color='Algorithm'
        )
        fig1.update_layout(showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = px.bar(
            comparison_df, 
            x='Algorithm', 
            y='Mean Normalized Turnaround',
            title="Mean Normalized Turnaround Comparison",
            color='Algorithm'
        )
        fig2.update_layout(showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Summary table
    st.subheader("📋 Summary Comparison")
    st.dataframe(comparison_df.set_index('Algorithm'), use_container_width=True)
    
    # Performance insights
    st.subheader("💡 Performance Insights")
    best_turnaround = comparison_df.loc[comparison_df['Mean Turnaround Time'].idxmin()]
    best_normalized = comparison_df.loc[comparison_df['Mean Normalized Turnaround'].idxmin()]
    
    col1, col2 = st.columns(2)
    with col1:
        st.success(f"🏆 **Best Mean Turnaround Time:**\n{best_turnaround['Algorithm']} ({best_turnaround['Mean Turnaround Time']:.2f})")
    with col2:
        st.success(f"🎯 **Best Normalized Turnaround:**\n{best_normalized['Algorithm']} ({best_normalized['Mean Normalized Turnaround']:.2f})")

# Page configuration
st.set_page_config(
    page_title="CPU Scheduling Algorithms Visualizer",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("⚙️ CPU Scheduling Algorithms Visualizer")
st.markdown("### Interactive tool to visualize and analyze CPU scheduling algorithms")

# Algorithm mappings
ALGORITHM_NAMES = {
    '1': 'FCFS (First Come First Serve)',
    '2': 'RR (Round Robin)',
    '3': 'SPN (Shortest Process Next)',
    '4': 'SRT (Shortest Remaining Time)',
    '5': 'HRRN (Highest Response Ratio Next)',
    '6': 'FB-1 (Feedback Queue 1)',
    '7': 'FB-2i (Feedback Queue 2i)',
    '8': 'AGING (Aging Algorithm)'
}

# Sidebar for input configuration
st.sidebar.header("📋 Configuration")

# Operation mode selection
operation_mode = st.sidebar.selectbox(
    "Select Operation Mode:",
    ("trace", "stats"),
    help="Trace: Shows timeline visualization, Stats: Shows statistical analysis"
)

# Algorithm selection
st.sidebar.subheader("Algorithm Selection")
selected_algorithms = []
algorithm_quantums = {}

for alg_id, alg_name in ALGORITHM_NAMES.items():
    col1, col2 = st.sidebar.columns([3, 1])
    
    with col1:
        if st.checkbox(alg_name, key=f"alg_{alg_id}"):
            selected_algorithms.append(alg_id)
    
    with col2:
        if alg_id == '2':  # Round Robin needs quantum
            quantum = st.number_input("Q", min_value=1, value=4, key=f"quantum_{alg_id}")
            algorithm_quantums[alg_id] = quantum

# Process input
st.sidebar.subheader("Process Configuration")
last_instant = st.sidebar.number_input("Last Instant (Timeline Length)", min_value=10, max_value=100, value=20)
process_count = st.sidebar.number_input("Number of Processes", min_value=1, max_value=10, value=5)

# Dynamic process input
st.sidebar.subheader("Process Details")
processes = []
for i in range(process_count):
    st.sidebar.write(f"**Process {chr(65+i)}:**")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        arrival = st.number_input(f"Arrival Time", min_value=0, value=i*2, key=f"arrival_{i}")
    with col2:
        service = st.number_input(f"Service Time", min_value=1, value=3+(i%3), key=f"service_{i}")
    
    processes.append({
        'name': chr(65+i),
        'arrival': arrival,
        'service': service
    })

# Generate algorithm string
algorithm_string = ""
if selected_algorithms:
    alg_parts = []
    for alg in selected_algorithms:
        if alg == '2' and alg in algorithm_quantums:
            alg_parts.append(f"{alg}-{algorithm_quantums[alg]}")
        else:
            alg_parts.append(alg)
    algorithm_string = ",".join(alg_parts)

# Main content area
if algorithm_string and st.sidebar.button("🚀 Run Simulation", type="primary"):
    # Create input string for C++ program
    input_lines = [
        operation_mode,
        algorithm_string,
        str(last_instant),
        str(process_count)
    ]
    
    for process in processes:
        input_lines.append(f"{process['name']},{process['arrival']},{process['service']}")
    
    input_data = "\n".join(input_lines) + "\n"
    
    # Write input to temporary file and run C++ program
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
            temp_file.write(input_data)
            temp_file_path = temp_file.name
        
        # Run the C++ executable
        result = subprocess.run(
            ['lab4.exe'],
            input=input_data,
            text=True,
            capture_output=True,
            cwd=r"c:\Users\ashwi\OneDrive - iitkgp.ac.in\Desktop\Placement Projects All files\Operating System\CPU-Scheduling-Algorithms"
        )
        
        if result.returncode == 0:
            output = result.stdout
            
            if operation_mode == "trace":
                st.success("✅ Simulation completed successfully!")
                display_trace_results(output, selected_algorithms, processes)
            else:
                st.success("✅ Statistical analysis completed!")
                display_stats_results(output, selected_algorithms, processes)
        else:
            st.error(f"❌ Error running simulation: {result.stderr}")
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
    finally:
        # Clean up temporary file
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass

else:
    # Show input preview
    if selected_algorithms:
        st.info("📋 Input Preview")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Selected Algorithms:**")
            for alg in selected_algorithms:
                if alg == '2' and alg in algorithm_quantums:
                    st.write(f"• {ALGORITHM_NAMES[alg]} (Quantum: {algorithm_quantums[alg]})")
                else:
                    st.write(f"• {ALGORITHM_NAMES[alg]}")
        
        with col2:
            st.write("**Process Details:**")
            process_df = pd.DataFrame(processes)
            if not process_df.empty:
                process_df.columns = ['Process', 'Arrival Time', 'Service Time']
                st.dataframe(process_df, use_container_width=True)
    else:
        st.warning("⚠️ Please select at least one algorithm to run the simulation.")

# Footer
st.markdown("---")
st.markdown("### 📚 About CPU Scheduling Algorithms")

with st.expander("ℹ️ Algorithm Descriptions"):
    st.markdown("""
    **FCFS (First Come First Serve):** Processes are executed in the order they arrive.
    
    **RR (Round Robin):** Each process gets a fixed time quantum before being preempted.
    
    **SPN (Shortest Process Next):** Non-preemptive algorithm that selects the process with the shortest service time.
    
    **SRT (Shortest Remaining Time):** Preemptive version of SPN that switches to the process with the shortest remaining time.
    
    **HRRN (Highest Response Ratio Next):** Selects the process with the highest response ratio (waiting time + service time) / service time.
    
    **FB-1 (Feedback Queue 1):** Multi-level feedback queue with quantum of 1.
    
    **FB-2i (Feedback Queue 2^i):** Multi-level feedback queue with exponentially increasing quantum.
    
    **AGING:** Prevents starvation by gradually increasing the priority of waiting processes.
    """)

st.markdown("*Created with ❤️ using Streamlit*")
