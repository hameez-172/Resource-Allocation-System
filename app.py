import streamlit as st
import networkx as nx
import pandas as pd
import plotly.express as px

# --- Core Algorithm Logic (Discrete Math) ---
def task_scheduler(tasks_data, resources):
    G = nx.DiGraph()
    # Directed Acyclic Graph (DAG) banana 
    for t_id, info in tasks_data.items():
        G.add_node(t_id, duration=info['duration'])
        for dep in info['dependencies']:
            if dep in tasks_data:
                G.add_edge(dep, t_id)

    resource_free_time = {r: 0 for r in resources}
    task_finish_time = {}
    schedule = []
    completed_tasks = set()

    # Loop jab tak saare tasks complete na ho jayein [cite: 14]
    while len(completed_tasks) < len(tasks_data):
        # Ready tasks identify karna [cite: 15]
        ready_tasks = [
            n for n in G.nodes() 
            if n not in completed_tasks and all(d in completed_tasks for d in G.predecessors(n))
        ]
        
        if not ready_tasks: break
        
        # Priority Rule: Shortest Job First [cite: 16]
        ready_tasks.sort(key=lambda x: tasks_data[x]['duration'])

        for task_id in ready_tasks:
            # Available resource assign karna [cite: 17]
            best_resource = min(resource_free_time, key=resource_free_time.get)
            
            # Start time calculation (Dependency check) 
            dep_finish_times = [task_finish_time[d] for d in G.predecessors(task_id)]
            start_time = max([resource_free_time[best_resource]] + dep_finish_times)
            
            end_time = start_time + tasks_data[task_id]['duration']
            
            # Update status [cite: 18]
            resource_free_time[best_resource] = end_time
            task_finish_time[task_id] = end_time
            completed_tasks.add(task_id)
            
            schedule.append({
                "Resource": best_resource,
                "Task": task_id,
                "Start": start_time,
                "Finish": end_time
            })
    return schedule

# --- Streamlit UI --- 
st.set_page_config(page_title="Resource Allocation System", layout="wide")
st.title("⚙️ Optimal Task Scheduler")
st.markdown("Yeh system **Discrete Mathematics** ke concepts (Graph Theory aur Combinatorics) par mabni hai. [cite: 1, 7]")

# Sidebar inputs
st.sidebar.header("Settings")
res_input = st.sidebar.text_input("Resources (Machine names comma se separate karein)", "Machine_A, Machine_B")
resources = [r.strip() for r in res_input.split(",") if r.strip()]

# Task Input
st.subheader("1. Tasks Detail")
num_tasks = st.number_input("Total kitne tasks hain?", min_value=1, max_value=20, value=4)

tasks_input = {}
cols = st.columns(2)
for i in range(num_tasks):
    t_id = f"T{i+1}"
    with cols[i % 2]:
        with st.expander(f"Task {t_id} Settings", expanded=True):
            dur = st.number_input(f"Duration (Hours)", min_value=1, key=f"d_{t_id}", value=2)
            deps = st.text_input(f"Dependencies (e.g., T1, T2)", key=f"p_{t_id}")
            dep_list = [d.strip() for d in deps.split(",")] if deps else []
            tasks_input[t_id] = {'duration': dur, 'dependencies': dep_list}

# Process
if st.button("Generate Schedule"):
    result = task_scheduler(tasks_input, resources)
    df = pd.DataFrame(result)
    
    if not df.empty:
        st.subheader("2. Final Schedule (Table)")
        st.table(df)

        st.subheader("3. Gantt Chart (Timeline)")
        # Plotly for visualization 
        fig = px.timeline(df, x_start="Start", x_end="Finish", y="Resource", color="Task", text="Task")
        fig.layout.xaxis.type = 'linear'
        for i, d in enumerate(fig.data):
            d.x = df[df['Task'] == d.name]['Finish'] - df[df['Task'] == d.name]['Start']
            d.base = df[df['Task'] == d.name]['Start']
        
        st.plotly_chart(fig, use_container_width=True)
    else:

        st.error("Schedule generate nahi ho saka. Baraye maharbani dependencies check karein.")
