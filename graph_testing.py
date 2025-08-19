import plotly.graph_objects as go
mic_ticks = [0.016, 0.032, 0.064, 0.125, 0.25, 0.5, 1, 2, 4, 8, 16, 32,64,128]
def create_base_graph():
    """Create an empty graph with proper labels"""
    fig1 = go.Figure()
    
    
    # Add basic layout
    fig1.update_layout(
        title="Antibiotic Breakpoints",
        xaxis_title="Concentration (µg/mL)",
        yaxis=dict(showticklabels=False),
        xaxis=dict(type= "log",
                   tickmode='array',
                   tickvals=mic_ticks,
                   ticktext=["0.016", "0.032", "0.064", "0.125","0.25","0.5","1","2","4","8","16","32"],
                   range=[-2.1, 2.1]  # controls zoom: log10 scale (-1=0.1, 2=100)
),
        height=300)
    return fig1


def add_zones(fig1, s_val, r_val,test_type):
        test_type == "mic"
        fig1.add_vrect(x0=mic_ticks[0], x1=s_val, fillcolor="green", opacity=0.2, name="Sensitive")
        fig1.add_vrect(x0=s_val, x1=r_val, fillcolor="yellow", opacity=0.2, name="Intermediate")
        fig1.add_vrect(x0=r_val, x1=mic_ticks[13], fillcolor="red", opacity=0.2, name="Resisitant")

        return fig1

def adding_user_results(fig1, user_val):
    fig1.add_trace(go.Scatter(
        x=[user_val], 
        y=[0],
        mode='markers + text',
        marker=dict(size=20, color='black'),
        text=[f"Your value: {user_val}"],
        textposition='top center',
        name='Your Result',
    ))
    fig1.add_vline(x=user_val, line=dict(color="grey", width=1))
    return fig1

def complete_graph(ab_name,s_val,r_val,test_type,user_val):
    fig1 = create_base_graph()
    #update title to include antibiotic name
    fig1.update_layout(title=f"{ab_name} Breakpoints")
    #add interperetation zones
    fig1 = add_zones(fig1, s_val, r_val, test_type)
    #add breakpoint lines
    fig1.add_vline(x=s_val, line_dash="dash", line_color="green", annotation_text="S")
    fig1.add_vline(x=r_val, line_dash="dash", line_color="red", annotation_text="R")

    #add user result
    fig1 = adding_user_results(fig1, user_val)

    #adjusting x-axis title based on test type
    x_title = "MIC (µg/mL)" if test_type == "mic" else "Zone Diameter (mm)"
    fig1.update_layout(xaxis_title=x_title)
    
    return fig1


def create_circular_zones(ab_name2, s_val2, r_val2, user_val2):
    fig = go.Figure()
    max_range = 60 #this will ensure a large enough chart
    
    # 1. Sensitive Zone (Outer Green Circle)
    fig.add_trace(go.Scatterpolar(
        r=[max_range]*360,  # 360 points at S value radius
        theta=list(range(360)),
        fill='toself',
        fillcolor='rgba(0,255,0,0.5)',
        line=dict(color='green', width=2),
        name=f'Sensitive (≥{s_val2}mm)'
    ))
    
    # 2. Intermediate Zone (Middle Orange Ring)
    fig.add_trace(go.Scatterpolar(
        r=[(s_val2)]*360,  # 360 points at intermediate radius
        theta=list(range(360)),
        fill='tonext',  # Fills between this and previous trace
        fillcolor='rgba(255,165,0,0.5)',
        line=dict(color='orange', width=2),
        name=f'Intermediate ({r_val2}-{s_val2}mm)'
    ))
    
    # 3. Resistant Zone (Inner Red Circle)
    fig.add_trace(go.Scatterpolar(
        r=[r_val2]*360,
        theta=list(range(360)),
        fill='toself',
        fillcolor='rgba(255,0,0,0.1)',
        line=dict(color='red', width=2),
        name=f'Resistant (≤{r_val2}mm)'
    ))
    
    # 4. Antibiotic Disc (6mm White Center)
    fig.add_trace(go.Scatterpolar(
        r=[3]*360,  # 6mm diameter disc
        theta=list(range(360)),
        fill='toself',
        fillcolor='white',
        line=dict(color='black', width=1),
        name=f"{ab_name2} disk"
    ))
    
    # 5. Measurement Line (User's Result)
    fig.add_trace(go.Scatterpolar(
        r=[0, user_val2],
        theta=[0, 90],  # Vertical measurement line
        mode='lines',
        line=dict(color='blue', width=3),
        name=f'Measurement ({user_val2}mm)'
    ))
    
    # Layout Configuration
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, max(s_val2+5, 30)]),
            angularaxis=dict(rotation=90, direction='clockwise')
        ),
        title=f"{ab_name2} Disk Diffusion Test",
        showlegend=True,
        legend=dict(orientation="h", y=1.1)
    )
    
    return fig