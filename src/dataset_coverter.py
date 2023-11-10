# %%
import pandas as pd
# %%
df = pd.read_csv(
    "../data/dataset_rent_rome_kijiji.tsv",
    sep="\t",
    usecols=["Title", "Short Description", "Location"],
)
df.head()
# df.to_csv("../data/rent_rome_text.csv", index=False)
df.to_json("../data/rent_rome_text.json", orient="records")

# %%
df1 = pd.read_csv("../data/articles1.csv", usecols=["id", "title", "content"])
df2 = pd.read_csv("../data/articles2.csv", usecols=["id", "title", "content"])
df3 = pd.read_csv("../data/articles3.csv", usecols=["id", "title", "content"])

# append them together
df = df1.append(df2).append(df3)
df.info()
# %%
df.to_json("../data/news.json", orient="records")
# %%
