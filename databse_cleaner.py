import pandas as pd

# Load the original CSV
input_file = 'AnimeList.csv'       # Replace with your actual filename
output_file = 'CleanedAnimeList.csv'

# Read the CSV into a DataFrame
df = pd.read_csv(input_file)

# Convert necessary columns to numeric, coercing errors into NaN
df['episodes'] = pd.to_numeric(df['episodes'], errors='coerce')
df['rank'] = pd.to_numeric(df['rank'], errors='coerce')
df['score'] = pd.to_numeric(df['score'], errors='coerce')
df['scored_by'] = pd.to_numeric(df['scored_by'], errors='coerce')

# Apply filters
filtered_df = df[
    (df['episodes'] >= 1) &
    (df['rank'] >= 1) &
    (df['score'] > 0) &
    (df['scored_by'] > 0) &
    (~df['genre'].str.lower().str.contains('ecchi', na=False)) &
    (df['image_url'].notna()) &
    (df['image_url'].str.strip() != '')
]

# Save to new CSV
filtered_df.to_csv(output_file, index=False)

print(f"Filtered dataset saved to {output_file}")
