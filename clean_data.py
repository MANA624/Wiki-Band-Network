import networkx
from DataFiles import DataFiles
import json


def main():
    file_manager = DataFiles()
    edge_data = file_manager.get_edge_data()
    edge_data = list(set(edge_data))
    file_manager.populate_cache()

    # We have a dictionary, where the key is the node number. The data follows
    # all_bands = {'nid': {"title": "Fleetwood Mac", "genres}}
    all_bands = {}

    for genre in file_manager.genres:
        for band in file_manager.cache[genre]:
            # If the band was already stored with a different genre. The ID is the same
            if band[0] in all_bands:
                all_bands[band[0]]["genres"].append(genre)
                continue

            all_bands[band[0]] = {}
            all_bands[band[0]]["title"] = band[1]
            all_bands[band[0]]["genres"] = [genre]
            all_bands[band[0]]["in_conns"] = []
            all_bands[band[0]]["out_conns"] = []
            all_bands[band[0]]["is_dup"] = False  # For later use
            all_bands[band[0]]["link_to"] = ""  # If it is a duplicate

    for edge in edge_data:
        for _ in range(int(edge[2])):
            all_bands[edge[0]]["out_conns"].append(edge[1])
            all_bands[edge[1]]["in_conns"].append(edge[0])

    # Disambiguation. Two bands with the same name, but different IDs

    # max_node = file_manager.max_node  # TODO: Fix and implement this instead
    max_node = max([int(key) for key in all_bands])

    for i in range(max_node+1):
        if str(i) not in all_bands:
            continue
        if all_bands[str(i)]["is_dup"]:
            continue
        for j in range(i+1, max_node+1):
            if str(j) not in all_bands or all_bands[str(j)]["is_dup"]:
                continue
            if all_bands[str(i)]["title"] == all_bands[str(j)]["title"]:
                if set(all_bands[str(i)]["out_conns"]) != set(all_bands[str(j)]["out_conns"]):
                    print("The out connections didn't match?!?!", i, j)

                all_bands[str(i)]["in_conns"] += all_bands[str(j)]["in_conns"]
                all_bands[str(i)]["genres"] = list(set(list(all_bands[str(i)]["genres"] + all_bands[str(j)]["genres"])))

                all_bands[str(j)] = {"is_dup": True, "link_to": str(i)}

    with open('data/cleaned.txt', 'w') as writer:
        writer.write(json.dumps(all_bands))

    # degrees = build_graph(data, weighted=True)

    # degrees_with_names = []
    #
    # file_manager.populate_cache()
    # for node in degrees:
    #     completed = False
    #     for genre in file_manager.genres:
    #         for band in file_manager.cache[genre]:
    #             if node[0] == band[0]:
    #                 degrees_with_names.append([band[1], node[1]])
    #                 completed = True
    #                 break
    #         if completed:
    #             break
    #
    # for i, band in enumerate(degrees_with_names):
    #     print(str(i) + ') ' + str(band))


if __name__ in "__main__":
    main()
