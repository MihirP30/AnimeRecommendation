import pandas as pd

input_file = 'AnimeList.csv'
output_file = 'CleanedAnimeList.csv'

df = pd.read_csv(input_file)

df['episodes'] = pd.to_numeric(df['episodes'], errors='coerce')
df['rank'] = pd.to_numeric(df['rank'], errors='coerce')
df['score'] = pd.to_numeric(df['score'], errors='coerce')
df['scored_by'] = pd.to_numeric(df['scored_by'], errors='coerce')

filtered_df = df[
    (df['episodes'] >= 1) &
    (df['rank'] >= 1) &
    (df['score'] > 0) &
    (df['scored_by'] > 0) &
    (~df['genre'].str.lower().str.contains('ecchi', na=False)) &
    (~df['genre'].str.lower().str.contains('hentai', na=False)) &
    (df['image_url'].notna()) &
    (df['image_url'].str.strip() != '')
]

filtered_df.to_csv(output_file, index=False)
