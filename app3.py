import streamlit as st
import nltk
from nltk.tokenize import word_tokenize
import re
import json
from datetime import datetime

# Ensure NLTK tokenizer is available
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# --- Enhanced Intent Parsing ---
def parse_natural_language(query, table_list, schema_info=None):
    """Enhanced parser with better pattern matching and context awareness"""
    query = query.lower().strip()
    
    # Enhanced pattern matching with regex
    patterns = {
        "show_all": [
            r"(?:show|display|list|get|select)\s+all\s+(\w+)",
            r"(?:show|display|list|get|select)\s+(\w+)\s+(?:table|records)",
            r"(?:all|entire)\s+(\w+)\s+(?:table|data)"
        ],
        "count_records": [
            r"(?:count|how many)\s+(\w+)",
            r"(?:number of|total number of)\s+(\w+)",
            r"(\w+)\s+count"
        ],
        "filter_by_column": [
            r"(?:show|get|find)\s+(\w+)\s+(?:where|with)\s+(\w+)\s+(?:is|=|equals?)\s+['\"]?(\w+)['\"]?",
            r"(\w+)\s+(?:in|from)\s+(\w+)\s+(?:city|state|country|region)",
            r"(\w+)\s+(?:where|with)\s+(\w+)\s+['\"]?(\w+)['\"]?"
        ],
        "calculate_sum": [
            r"(?:total|sum of?)\s+(\w+)",
            r"(?:add up|calculate)\s+(?:all\s+)?(\w+)",
            r"(\w+)\s+(?:total|sum)"
        ],
        "calculate_avg": [
            r"(?:average|avg|mean)\s+(\w+)",
            r"(\w+)\s+(?:average|avg|mean)"
        ],
        "calculate_max": [
            r"(?:maximum|max|highest)\s+(\w+)",
            r"(\w+)\s+(?:maximum|max|highest)"
        ],
        "calculate_min": [
            r"(?:minimum|min|lowest)\s+(\w+)",
            r"(\w+)\s+(?:minimum|min|lowest)"
        ],
        "order_by": [
            r"(?:sort|order)\s+(\w+)\s+by\s+(\w+)",
            r"(\w+)\s+(?:sorted|ordered)\s+by\s+(\w+)"
        ],
        "limit": [
            r"(?:top|first)\s+(\d+)\s+(\w+)",
            r"(\d+)\s+(?:first|top)\s+(\w+)"
        ]
    }
    
    # Check each pattern type
    for intent, pattern_list in patterns.items():
        for pattern in pattern_list:
            match = re.search(pattern, query)
            if match:
                groups = match.groups()
                
                # Determine table from context
                table = None
                for t in table_list:
                    if t in query:
                        table = t
                        break
                
                if intent == "show_all":
                    return {"intent": "show_all", "table": groups[0] if groups[0] in table_list else table or groups[0]}
                elif intent == "count_records":
                    return {"intent": "count_records", "table": groups[0] if groups[0] in table_list else table or groups[0]}
                elif intent == "filter_by_column":
                    if len(groups) >= 3:
                        return {"intent": "filter_by_column", "table": groups[0], "column": groups[1], "value": groups[2]}
                elif intent in ["calculate_sum", "calculate_avg", "calculate_max", "calculate_min"]:
                    return {"intent": intent, "column": groups[0], "table": table or infer_table_from_column(groups[0], table_list)}
                elif intent == "order_by":
                    return {"intent": "order_by", "table": groups[0], "column": groups[1]}
                elif intent == "limit":
                    return {"intent": "limit", "limit": groups[0], "table": groups[1]}
    
    # Fallback to original logic for specific cases
    if "customers in" in query:
        if "new york" in query:
            return {"intent": "filter_by_city", "table": "customers", "city": "New York"}
        elif "london" in query:
            return {"intent": "filter_by_city", "table": "customers", "city": "London"}
    
    return {"intent": "unknown", "query": query}

def infer_table_from_column(column, table_list):
    """Infer table name based on column name"""
    column_table_mapping = {
        "amount": "sales",
        "price": "products",
        "order_value": "orders",
        "salary": "employees",
        "age": "customers"
    }
    return column_table_mapping.get(column, table_list[0] if table_list else "table")

# --- Enhanced SQL Generator ---
def generate_sql(parsed):
    """Generate SQL with better formatting and validation"""
    intent = parsed.get("intent")
    table = parsed.get("table")
    column = parsed.get("column")
    city = parsed.get("city")
    value = parsed.get("value")
    limit = parsed.get("limit")

    if intent == "show_all":
        return f"SELECT *\nFROM {table};"
    elif intent == "calculate_sum":
        return f"SELECT SUM({column}) as total_{column}\nFROM {table};"
    elif intent == "count_records":
        return f"SELECT COUNT(*) as record_count\nFROM {table};"
    elif intent == "filter_by_city":
        return f"SELECT *\nFROM {table}\nWHERE city = '{city}';"
    elif intent == "filter_by_column":
        return f"SELECT *\nFROM {table}\nWHERE {column} = '{value}';"
    elif intent == "calculate_avg":
        return f"SELECT AVG({column}) as avg_{column}\nFROM {table};"
    elif intent == "calculate_max":
        return f"SELECT MAX({column}) as max_{column}\nFROM {table};"
    elif intent == "calculate_min":
        return f"SELECT MIN({column}) as min_{column}\nFROM {table};"
    elif intent == "order_by":
        return f"SELECT *\nFROM {table}\nORDER BY {column};"
    elif intent == "limit":
        return f"SELECT *\nFROM {table}\nLIMIT {limit};"

    return "-- Unable to generate SQL. Please refine your query."

# --- Enhanced Explanation Generator ---
def explain_sql(parsed):
    """Generate detailed explanations with context"""
    intent = parsed.get("intent")
    table = parsed.get("table")
    column = parsed.get("column")
    city = parsed.get("city")
    value = parsed.get("value")
    limit = parsed.get("limit")

    explanations = {
        "show_all": f"📊 **Retrieves all records** from the `{table}` table, displaying every column and row.",
        "calculate_sum": f"➕ **Calculates the total sum** of all values in the `{column}` column from the `{table}` table.",
        "count_records": f"🔢 **Counts the total number of records** in the `{table}` table.",
        "filter_by_city": f"🏙️ **Filters records** from the `{table}` table to show only entries where the city is `{city}`.",
        "filter_by_column": f"🔍 **Filters records** from the `{table}` table where `{column}` equals `{value}`.",
        "calculate_avg": f"📈 **Calculates the average value** of the `{column}` column from the `{table}` table.",
        "calculate_max": f"⬆️ **Finds the maximum value** in the `{column}` column from the `{table}` table.",
        "calculate_min": f"⬇️ **Finds the minimum value** in the `{column}` column from the `{table}` table.",
        "order_by": f"🔄 **Sorts all records** from the `{table}` table by the `{column}` column in ascending order.",
        "limit": f"🔝 **Retrieves the first {limit} records** from the `{table}` table."
    }
    
    return explanations.get(intent, "❓ Could not explain this query.")

# --- Query Suggestions ---
def get_query_suggestions(table_list):
    """Generate context-aware query suggestions"""
    suggestions = []
    for table in table_list:
        suggestions.extend([
            f"Show all {table}",
            f"Count {table}",
            f"Top 10 {table}",
            f"Average amount from {table}" if table in ["sales", "orders"] else f"Show {table} data"
        ])
    return suggestions

# --- Streamlit UI with Enhanced Design ---
st.set_page_config(
    page_title="DataGenie - Natural Language to SQL",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: white;
        margin: 0;
        text-align: center;
    }
    .stats-container {
        display: flex;
        justify-content: space-around;
        margin: 1rem 0;
    }
    .stat-box {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        min-width: 150px;
    }
    .query-history {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🧠 SQLtOK: Your SQL Assistant </h1>
    <p style="color: white; text-align: center; margin: 0;">Transform your questions into powerful SQL queries instantly!</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if "query_history" not in st.session_state:
    st.session_state.query_history = []
if "schema_info" not in st.session_state:
    st.session_state.schema_info = {}

# Sidebar Configuration
with st.sidebar:
    st.header("🔧 Configuration")
    
    # Table Configuration
    st.subheader("📊 Database Tables")
    table_input = st.text_input(
        "Available Tables (comma-separated)", 
        "products,users,orders,customers,sales,employees",
        help="Enter the names of tables in your database"
    )
    table_list = [t.strip().lower() for t in table_input.split(",")]
    
    # Schema Information (Optional)
    st.subheader("️ Schema Information")
    schema_expander = st.expander("Add Column Information (Optional)")
    with schema_expander:
        selected_table = st.selectbox("Select Table", table_list)
        columns = st.text_input(f"Columns for {selected_table}", "id,name,email,created_at")
        if st.button("Save Schema"):
            st.session_state.schema_info[selected_table] = [col.strip() for col in columns.split(",")]
            st.success(f"Schema saved for {selected_table}")
    
    st.markdown("---")
    
    # Query Examples
    st.subheader("💡 Query Examples")
    examples = get_query_suggestions(table_list[:3])  # Limit to first 3 tables
    selected_example = st.selectbox("Choose a sample query:", ["None"] + examples)
    
    if selected_example != "None":
        st.session_state["query"] = selected_example
    
  

# Main Interface
col1, col2 = st.columns([3, 1])

with col1:
    user_query = st.text_input(
        "Ask your question in plain english:",
        value=st.session_state.get("query", ""),
        placeholder="e.g., show all users, total sales this month, customers in New York...",
        help="Type your question naturally - DataGenie will understand!"
    )

with col2:
    st.write("")  # Space for alignment
    generate = st.button("Generate SQL", type="primary", use_container_width=True)

# Query Processing
if generate and user_query:
    with st.spinner("🔄 Processing your query..."):
        parsed = parse_natural_language(user_query, table_list, st.session_state.schema_info)
        sql = generate_sql(parsed)
        explanation = explain_sql(parsed)
        
        # Determine success
        success = parsed["intent"] != "unknown"
        
        # Store in history
        st.session_state.query_history.append({
            "query": user_query,
            "sql": sql,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "success": success
        })
        
        if success:
            st.success("✅Query processed successfully!")
            
            # Display results in columns
            result_col1, result_col2 = st.columns([2, 1])
            
            with result_col1:
                st.subheader("🔍 Generated SQL")
                st.code(sql, language="sql")
                
                # Copy button simulation
                st.caption(" Tip: You can copy this SQL and run it in your database!")
                
            with result_col2:
                st.subheader(" Explanation")
                st.markdown(explanation)
                
                # Query details
                st.subheader("🔧 Query Details")
                st.json({
                    "Intent": parsed["intent"],
                    "Table": parsed.get("table", "N/A"),
                    "Column": parsed.get("column", "N/A"),
                    "Filter": parsed.get("value", parsed.get("city", "N/A"))
                })
        else:
            st.error("❌ Could not understand your query")
            st.markdown("""
            **Suggestions:**
            - Try simpler phrases like "show all products" or "count users"
            - Make sure table names match your configuration
            - Use keywords like: show, count, total, average, maximum, minimum
            """)

# Query History
if st.session_state.query_history:
    st.markdown("---")
    st.subheader("📚 Query History")
    
    # Display recent queries
    for i, query_data in enumerate(reversed(st.session_state.query_history[-5:])):  # Show last 5
        with st.expander(f"🕐 {query_data['timestamp']} - {query_data['query'][:50]}..." if len(query_data['query']) > 50 else f"🕐 {query_data['timestamp']} - {query_data['query']}"):
            st.code(query_data['sql'], language="sql")
            if st.button(f"Reuse Query {i}", key=f"reuse_{i}"):
                st.session_state["query"] = query_data['query']
                st.experimental_rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p> Made for <strong>FutureHack! 404BRAIN 2025</strong> — Problem 4</p>
    <p>Powered by Natural Language Processing & Pattern Recognition</p>
</div>
""", unsafe_allow_html=True)
