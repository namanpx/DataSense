import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Page configuration
st.set_page_config(
    page_title="DataSense",
    page_icon="📊",
    layout="wide"
)

# Title
st.title("📊 DataSense - AI-Powered Data Analysis")
st.markdown("Upload a CSV file to analyze your data with AI insights")

# Sidebar
st.sidebar.header("📁 Upload Data")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")

# Function to generate data insights
def generate_insights(df):
    """Generate simple data insights without AI API"""
    insights = []
    
    # 1. Data shape
    insights.append(f"📊 Your dataset has **{len(df)} rows** and **{len(df.columns)} columns**")
    
    # 2. Missing values
    missing = int(df.isnull().sum().sum())
    if missing > 0:
        insights.append(f"⚠️ Found **{missing} missing values** - consider cleaning data")
    else:
        insights.append(f"✅ No missing values - data is clean!")
    
    # 3. Numeric columns analysis
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    if numeric_cols:
        for col in numeric_cols[:3]:  # Show top 3
            max_val = df[col].max()
            min_val = df[col].min()
            avg_val = df[col].mean()
            insights.append(f"📈 **{col}**: Min={min_val:.2f}, Max={max_val:.2f}, Avg={avg_val:.2f}")
    
    # 4. Categorical columns analysis
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    if cat_cols:
        for col in cat_cols[:2]:  # Show top 2
            top_value = df[col].value_counts().idxmax()
            top_count = df[col].value_counts().max()
            insights.append(f"🏷️ **{col}**: Most common value is '{top_value}' (appears {top_count} times)")
    
    return insights

# Function to call Gemini API (Optional)
def get_ai_analysis(df, question):
    """Get AI-powered analysis using Gemini API"""
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "❌ Please set GEMINI_API_KEY environment variable to use AI chat"
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # Create context about the data
        context = f"""
        I have a dataset with {len(df)} rows and these columns: {', '.join(df.columns)}.
        
        Summary statistics:
        {df.describe().to_string()}
        
        Please answer this question about the data: {question}
        Keep the answer brief and actionable.
        """
        
        response = model.generate_content(context)
        return response.text
    except ImportError:
        return "⚠️ Install google-generativeai: `pip install google-generativeai`"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Main content
if uploaded_file is not None:
    # Read CSV
    df = pd.read_csv(uploaded_file)
    
    # Show statistics in sidebar
    st.sidebar.header("📊 Quick Stats")
    st.sidebar.metric("Rows", len(df))
    st.sidebar.metric("Columns", len(df.columns))
    st.sidebar.metric("Missing Values", int(df.isnull().sum().sum()))
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Data", "📊 Summary", "📈 Charts", "🔍 Filter", "🤖 AI Analysis"])
    
    # Tab 1: Data View
    with tab1:
        st.subheader("Raw Data")
        st.dataframe(df, use_container_width=True)
    
    # Tab 2: Summary Statistics
    with tab2:
        st.subheader("Summary Statistics")
        st.dataframe(df.describe(), use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Data Types")
            st.write(df.dtypes)
        
        with col2:
            st.subheader("Missing Values Count")
            missing_data = df.isnull().sum()
            st.write(missing_data[missing_data > 0] if missing_data.sum() > 0 else "No missing values!")
    
    # Tab 3: Charts
    with tab3:
        st.subheader("Create Charts")
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        all_cols = df.columns.tolist()
        
        chart_type = st.selectbox(
            "Select Chart Type",
            ["Bar Chart", "Line Chart", "Pie Chart", "Histogram", "Scatter Plot"]
        )
        
        if chart_type == "Bar Chart":
            x_col = st.selectbox("X-axis", all_cols, key="bar_x")
            y_col = st.selectbox("Y-axis", numeric_cols, key="bar_y")
            
            if x_col and y_col:
                fig = px.bar(
                    df.groupby(x_col)[y_col].sum().reset_index(),
                    x=x_col,
                    y=y_col,
                    title=f"{y_col} by {x_col}"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        elif chart_type == "Line Chart":
            if numeric_cols:
                x_col = st.selectbox("X-axis", all_cols, key="line_x")
                y_col = st.selectbox("Y-axis", numeric_cols, key="line_y")
                
                if x_col and y_col:
                    fig = px.line(
                        df,
                        x=x_col,
                        y=y_col,
                        title=f"{y_col} vs {x_col}",
                        markers=True
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        elif chart_type == "Pie Chart":
            cat_cols = df.select_dtypes(include=['object']).columns.tolist()
            if numeric_cols and cat_cols:
                cat_col = st.selectbox("Category", cat_cols, key="pie_cat")
                val_col = st.selectbox("Values", numeric_cols, key="pie_val")
                
                if cat_col and val_col:
                    fig = px.pie(
                        df.groupby(cat_col)[val_col].sum().reset_index(),
                        names=cat_col,
                        values=val_col,
                        title=f"{val_col} by {cat_col}"
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        elif chart_type == "Histogram":
            if numeric_cols:
                col = st.selectbox("Select Column", numeric_cols, key="hist_col")
                fig = px.histogram(
                    df,
                    x=col,
                    title=f"Distribution of {col}",
                    nbins=30
                )
                st.plotly_chart(fig, use_container_width=True)
        
        elif chart_type == "Scatter Plot":
            if len(numeric_cols) >= 2:
                x_col = st.selectbox("X-axis", numeric_cols, key="scatter_x")
                y_col = st.selectbox("Y-axis", numeric_cols, key="scatter_y")
                
                if x_col and y_col:
                    fig = px.scatter(
                        df,
                        x=x_col,
                        y=y_col,
                        title=f"{y_col} vs {x_col}"
                    )
                    st.plotly_chart(fig, use_container_width=True)
    
    # Tab 4: Filter Data
    with tab4:
        st.subheader("Filter Data")
        
        cat_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        if cat_cols:
            filter_col = st.selectbox("Select column to filter", cat_cols)
            filter_values = st.multiselect(
                "Select values",
                df[filter_col].unique()
            )
            
            if filter_values:
                filtered_df = df[df[filter_col].isin(filter_values)]
                st.write(f"Filtered Data ({len(filtered_df)} rows)")
                st.dataframe(filtered_df, use_container_width=True)
        else:
            st.info("No categorical columns found for filtering")
    
    # Tab 5: AI Analysis
    with tab5:
        st.subheader("🤖 AI-Powered Insights")
        
        # Automatic insights
        st.markdown("### 📊 Automatic Insights")
        insights = generate_insights(df)
        for insight in insights:
            st.markdown(f"- {insight}")
        
        st.divider()
        
        # AI Chat (Optional - requires API key)
        st.markdown("### 💬 Ask AI About Your Data")
        st.info("💡 To use AI chat, set your GEMINI_API_KEY environment variable")
        
        user_question = st.text_input("Ask a question about your data:")
        
        if user_question:
            with st.spinner("🤔 Thinking..."):
                response = get_ai_analysis(df, user_question)
                st.markdown(response)
        
        with st.expander("📖 How to enable AI chat:"):
            st.markdown("""
            1. Get a free API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
            2. Set environment variable:
               ```bash
               export GEMINI_API_KEY="your_api_key_here"
               ```
            3. Install Google AI library:
               ```bash
               pip install google-generativeai
               ```
            4. Restart the app
            """)

else:
    st.info("👈 Upload a CSV file from the sidebar to start analyzing")
    
    with st.expander("📋 How to use:"):
        st.markdown("""
        1. **Upload** - Click "Upload" in the left sidebar and select a CSV file
        2. **Data View** - See your raw data
        3. **Summary** - Check statistics and data types
        4. **Charts** - Create 5 types of visualizations
        5. **Filter** - Filter data by categories
        6. **AI Analysis** - Get automatic insights + optional AI chat
        """)
    
    st.success("✅ Try uploading the sample_data.csv file to see DataSense in action!")
