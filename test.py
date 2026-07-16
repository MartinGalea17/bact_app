import pandas as pd
import matplotlib.pyplot as plt



data = {
    "sample_id": [
        "S001","S002","S003","S004","S005",
        "S006","S007","S008","S009","S010",
        "S011","S012","S013","S014","S015"
    ],

    "gene_expression": [
        12.4, 15.8, 10.1, 18.5, 22.3,
        16.7, 14.2, 20.9, 11.8, 19.4,
        13.6, 17.2, 21.5, 9.8, 23.1
    ],

    "protein_concentration": [
        45.2, 50.1, 41.8, 55.6, 60.2,
        52.7, 48.3, 58.9, 43.7, 56.8,
        46.9, 54.1, 61.5, 39.8, 63.2
    ],

    "cell_count": [
        120000, 135000, 110000, 145000, 160000,
        138000, 128000, 155000, 115000, 149000,
        125000, 142000, 162000, 108000, 168000
    ],

    "mutation_count": [
        2, 5, 1, 6, 8,
        4, 3, 7, 2, 6,
        3, 5, 9, 1, 10
    ],

    "gc_content": [
        42.5, 44.1, 41.8, 46.3, 48.2,
        45.6, 43.7, 47.9, 42.1, 46.8,
        43.4, 45.9, 48.6, 41.5, 49.2
    ],

    "sequence_length": [
        1200, 1450, 980, 1600, 1750,
        1500, 1350, 1700, 1100, 1650,
        1300, 1550, 1800, 950, 1850
    ],

    "ph": [
        7.2, 7.4, 6.9, 7.5, 7.8,
        7.3, 7.1, 7.6, 6.8, 7.5,
        7.2, 7.4, 7.9, 6.7, 8.0
    ],

    "temperature": [
        37.0, 36.8, 37.2, 38.0, 38.5,
        37.4, 36.9, 38.2, 37.1, 38.1,
        37.3, 37.8, 38.6, 36.7, 38.8
    ],

    "treatment": [
        "DrugA", "DrugB", "Control", "DrugA", "DrugC",
        "DrugB", "Control", "DrugA", "DrugC", "DrugB",
        "Control", "DrugA", "DrugC", "Control", "DrugB"
    ],

    "disease_status": [
        "Healthy", "Cancer", "Healthy", "Cancer", "Cancer",
        "Healthy", "Healthy", "Cancer", "Healthy", "Cancer",
        "Healthy", "Cancer", "Cancer", "Healthy", "Cancer"
    ]
}

#load data into a DataFrame object:
def load_data():
    df = pd.DataFrame(data)
    return df

def load_subdata(df,columns):
        return df[columns].copy()

def run_stats(df):
            head = df.head()
            shape = df.shape
            info = df.info()
            summary = df.describe()
            columns = df.columns
            types = df.dtypes
            sum = df.isnull().sum()
            return head,shape,summary, columns, types, sum


def plot_histogram(df,column,bins=10):
    plt.hist(df[column], bins=bins)
    plt.title(f"Distribution of {column}")
    plt.xlabel(column)
    plt.ylabel("Frequency")
    plt.show()


def plot_scatter(df,xcolumn,ycolumn):
    plt.scatter(df[xcolumn], df[ycolumn])
    plt.title(f"{ycolumn} vs {xcolumn}")
    plt.xlabel(xcolumn)
    plt.ylabel(ycolumn)
    plt.show()





#call load data
df = load_data()

#creating dataframes
gene_data = load_subdata(df, ["sample_id", "gene_expression"])
protein_data = load_subdata(df, ["sample_id", "protein_concentration"])
cellcount_data = load_subdata(df, ["sample_id", "cell_count"])

#call function to get subset data, add more combination later
datasets = {
    "Gene": gene_data,
    "Protein": protein_data,
    "Cell_count": cellcount_data}

for name, dataset in datasets.items():
    print(f"\n{name} Dataset")
    print(run_stats(dataset))
    head,shape,summary, columns, types, sum = run_stats(dataset)

#creating the plots 
plot_histogram(df, "gene_expression")
plot_histogram(df, "protein_concentration")
plot_histogram(df, "cell_count", bins=20)

#create scatter plots 
plot_scatter(df, "gene_expression", "protein_concentration")
plot_scatter(df, "cell_count", "mutation_count")


