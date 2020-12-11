import json
import networkx as nx
import matplotlib.pyplot as plt
from prettytable import PrettyTable
from datetime import datetime
from webweb import Web


# Take all the raw data and connections from the graph, then build a network out of it. Cool!
def build_graph(all_bands, weighted=False):
    G = nx.DiGraph()

    for band_id in all_bands:
        # Check if it's a duplicate
        if all_bands[band_id]["is_dup"]:
            continue

        # If the band is a loser, still add them to the graph
        if (not all_bands[band_id]["in_conns"]) and (not all_bands[band_id]["out_conns"]):
            G.add_node(band_id)
            continue

        # TODO: Implement weights

        # Create a working set of incoming edges from other nodes, then add them
        working_set = list(set(all_bands[band_id]["in_conns"]))
        for node in working_set:
            if all_bands[node]["is_dup"]:
                add_node = all_bands[node]["link_to"]
            else:
                add_node = node
            G.add_edge(add_node, band_id)
            # G.add_edge(band_id, add_node)

    return G


def find_degree_cent(G):
    ret = []
    for i in G.nodes:
        ret.append((i, G.degree[i]))

    ret.sort(key=lambda x: x[1], reverse=True)
    return ret


def find_harmonic_cent(G):
    centralities = nx.harmonic_centrality(G)
    ret = [(i, centralities[i]/(G.number_of_nodes()-1)) for i in G.nodes]

    ret.sort(key=lambda x: x[1], reverse=True)
    return ret


def find_eigen_cent(G):
    centralities = nx.eigenvector_centrality(G)
    ret = [(i, centralities[i]) for i in G.nodes]

    ret.sort(key=lambda x: x[1], reverse=True)
    return ret


def find_between_cent(G):
    centralities = nx.betweenness_centrality(G)
    ret = [(i, centralities[i]) for i in G.nodes]

    ret.sort(key=lambda x: x[1], reverse=True)
    return ret


# This is where I can expect to see my really nice results from the data
def print_results(all_bands):
    # First get a lists of lists. Easier for rankings than a dict of dicts
    final_list = []
    for band in all_bands:
        if all_bands[band]["is_dup"]:
            continue
        final_list.append([
            all_bands[band]["title"],
            all_bands[band]["in_degree"],
            all_bands[band]["rs_rankings"],
            all_bands[band]["eigen_rank"],
            all_bands[band]["harm_rank"],
            all_bands[band]["between_rank"],
            all_bands[band]["out_degree"],
        ])

    # Sort by the in degree
    final_list.sort(key=lambda x: x[1], reverse=True)

    x = PrettyTable()
    x.field_names = "Rank", "Band Name", "In Degree", "Out Degree", "Eigen Cent", "Harmonic Cent", "Between Cent", "RS overall", "RS country", "RS metal"

    print('='*130)
    print("Rank     Band name               In Degree   Eigen Cent      Harmonic Cent   Between Cent    RS rankings (overall, country, metal)")
    print('='*130)

    for i, band in enumerate(final_list[:100]):
        x.add_row([str(i+1)+')', band[0], band[1], band[6], str(round(band[3], 4)), str(round(band[4], 4)), str(round(band[5], 4)), band[2][0], band[2][1], band[2][2]])
        print(str(i+1)+')  \t', band[0], ' '*(22-len(band[0])), band[1], '\t\t', str(round(band[3], 4)), '  \t\t', str(round(band[4], 4)), '  \t\t',str(round(band[5], 4)), '  \t\t', band[2])

    with open("centralities.html", 'w') as writer:
        writer.write(x.get_html_string())


# Take the data from the Rolling Stones' 100 Greatest Artists of All Time,
# 100 Greatest Country Artists, and Top 10 Metal Artists saved in text files
# Then append this data to
def add_rs_rankings(all_data):
    # Zero out/add a place to put rankings for all nodes
    for node_id in all_data:
        if all_data[node_id]["is_dup"]:
            continue
        all_data[node_id]["rs_rankings"] = ['-', '-', '-']

    # Iterate through each file. Entries separated by newlines, data separated by tab
    for i, file in enumerate(["100", "100_Country", "10_Metal"]):
        with open("data/RS_Top_{}.txt".format(file)) as reader:
            top_100 = reader.read()
        top_100 = top_100.split('\n')
        top_100 = [x.split('\t') for x in top_100]
        for band in top_100:
            for key in all_data:
                if all_data[key]["is_dup"]:
                    continue

                # For each top 10(0) band, if the titles are equal, update the ranking
                if band[1] == all_data[key]["title"]:
                    all_data[key]["rs_rankings"][i] = band[0]
                    break


# Plot a histogram of the in-degrees
def in_deg_dist(all_bands):
    degs = []

    for band_id in all_bands:
        if all_bands[band_id]["is_dup"]:
            continue
        degs.append(all_bands[band_id]["in_degree"])

    # degs.sort(reverse=True)  # TODO: Comment out and delete
    # print(degs)

    # Remove all 0s from the degree distribution. Remove for now
    # degs = [deg for deg in degs if deg>10]

    plt.hist(degs, bins=50)
    plt.title("Histogram of In Degrees in Nodes")
    plt.xlabel("In Degree of Node")
    plt.ylabel("# Nodes with In Degree")
    plt.ylim(0, 100)
    # plt.show()
    plt.savefig("histTail.png")


# Show a webweb graph of all the nodes, hopefully so that we can see some interesting information
def visual_graph(all_bands):
    edge_list = []

    b = []
    i = 0
    for band_id in all_bands:
        i +=1
        # if i > 100:
        #     break
        if all_bands[band_id]["is_dup"]:
            continue
        for to in all_bands[band_id]["in_conns"]:
            if all_bands[to]["is_dup"]:
                to = all_bands[to]["link_to"]
            edge_list.append([band_id, to])
            edge_list.append([to, band_id])
        if set(all_bands[band_id]["genres"]) == {"rock"}:
            group = 'R'
        elif set(all_bands[band_id]["genres"]) == {"country"}:
            group = 'C'
        elif set(all_bands[band_id]["genres"]) == {"metal"}:
            group = "M"
        elif set(all_bands[band_id]["genres"]) == {"rock", "country"}:
            group = "R+C"
        elif set(all_bands[band_id]["genres"]) == {"rock", "metal"}:
            group = "R+M"
        elif set(all_bands[band_id]["genres"]) == {"country", "metal"}:
            group = "C+M"
        elif set(all_bands[band_id]["genres"]) == {"rock", "country", "metal"}:
            group = "R+C+M"
        else:
            raise Exception("Band with unspecified group")
        b.append([band_id, group])

    web = Web(title='sbm_demo',
              # assign its edgelist
              adjacency=edge_list,
              # give it the community metadata
              nodes={i: {'Genre': g} for i, g in b},
              # display={"metadata": {'Genre': {'values': ["R", "C", "M", "R+C", "R+M", "C+M", "R+C+M"]}}}
    )
    web.display.colorBy = 'Genre'
    web.show()


# Return basic information about the graph
def get_basic_stats(G):
    pass


def main():
    # all_bands["id"]["out_conns"] is broken. You'll regret using it
    with open('data/cleaned.txt', 'r') as reader:
        all_bands = reader.read()
    all_bands = json.loads(all_bands)
    add_rs_rankings(all_bands)

    G = build_graph(all_bands)

    # Find the various means of ranking a graph
    # In degree
    ranks = G.in_degree
    for rank in ranks:
        all_bands[rank[0]]["in_degree"] = rank[1]

    # Out degree
    ranks = G.out_degree
    for rank in ranks:
        all_bands[rank[0]]["out_degree"] = rank[1]

    eigens = find_eigen_cent(G)
    for eigen in eigens:
        all_bands[eigen[0]]["eigen_rank"] = eigen[1]

    print("harms")
    # harms = find_harmonic_cent(G)
    harms = find_eigen_cent(G)
    for harm in harms:
        all_bands[harm[0]]["harm_rank"] = harm[1]

    print("betweens")
    # betweens = find_between_cent(G)
    betweens = find_eigen_cent(G)
    for between in betweens:
        all_bands[between[0]]["between_rank"] = between[1]

    # Final analysis
    # in_deg_dist(all_bands)
    # print_results(all_bands)
    # visual_graph(all_bands)


if __name__ in "__main__":
    main()
