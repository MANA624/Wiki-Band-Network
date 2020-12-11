import os

# This class is responsible for managing the text files for reading and writing
# Think of it as the 'M' in MVP


class DataFiles:
    active_genre = ""

    def __init__(self):
        self.data_dir = "data/"
        self.node_file = os.path.join(self.data_dir, "{0}_nodes.txt")
        self.edges_file = os.path.join(self.data_dir, "edges.txt")
        self.genres = ["rock", "country", "metal"]
        self.max_node = -1

        self.cache_populated = False
        self.cache = {}
        # These keep track of what URLs do and do not refer to qualified bands
        self.valid_urls = set()
        self.valid_lowers = set()
        self.invalid_urls = set()
        self.invalid_urls_file = os.path.join(self.data_dir, "invalid_urls.txt")

    # Takes a nice, clean dictionary with all the data, and writes it to a file


    # Write a edge to the edges file. Only updates. Never overwrites
    # Provide a weight option for number of times one referenced the other
    def write_edge(self, from_id, to_id, weight=1):
        with open(self.edges_file, 'a') as appender:
            appender.write(from_id + '\t' + to_id + '\t' + str(weight) + '\n')

    # This is a pretty dumb function. Just return a list of lists of all the data
    def get_edge_data(self):
        with open(self.edges_file, 'r') as reader:
            data = reader.read()

        data = data.split('\n')
        data = [tuple(x.split('\t')) for x in data if len(x) > 5]

        return data

    # Return a string of the node number corresponding with the URL (unique ID)
    def get_node_num(self, url):
        if not self.cache_populated:
            self.populate_cache()

        # Remove everything after a '#' - usually just a subsection of a page. Not helpful
        if url.find('#') != -1:
            url = url[:url.find("#")]

        for genre in self.genres:
            for i in range(len(self.cache[genre])):
                if url.lower() == self.cache[genre][i][2].lower():
                    return self.cache[genre][i][0]

        return -1

    # Test if the URL leads to a valid page or not
    # Return -1 for not valid, 1 for valid, and 0 for untested
    def test_valid_url(self, url):
        if not self.cache_populated:
            self.populate_cache()

        url = url.lower()

        # Remove everything after a '#' - usually just a subsection of a page. Not helpful
        if url.find('#') != -1:
            url = url[:url.find("#")]

        # Test if blank
        if not url:
            return -1

        # Test for known useless subgroups
        non_pages = ["/wiki/category:", "/wiki/wikipedia:", "template:", "/wiki/help:", "/wiki/file:", "/wiki/special:", "/wiki/book:", "/wiki/portal:",
                     "/w/index.php?", "#cite_ref", "#cite_note",
                     # Or a web page
                     "https://", "http://", ".com", ".org", "(identifier)",
                     # Or something that isn't helpful (Crude approximation)
                     "song", "album"
         ]
        for page in non_pages:
            if page in url:
                return -1

        if url in self.invalid_urls:
            return -1
        elif url in self.valid_lowers:
            return 1
        else:
            return 0

    # Writes an invalid URL to the invalid_urls.txt file
    def write_invalid_url(self, url):
        if not self.cache_populated:
            self.populate_cache()

        # Don't write if I don't need to
        if url.lower() in self.invalid_urls:
            return

        with open(self.invalid_urls_file, 'a') as appender:
            appender.write(url + '\n')

        self.invalid_urls.add(url)

    # Writes the header of the file of the active genre.
    # Overwrites all other data in the file
    def write_header(self, genre=None):
        if not genre:
            if not self.active_genre:
                raise Exception("You didn't specify or set the active genre!")
            genre = self.active_genre

        with open(self.node_file.format(genre), 'w') as writer:
            writer.write("# All the main nodes for {}\n".format(genre))
            writer.write("#Node ID\tBand Title\tLink\n")

        # Invalidate the cache
        self.cache_populated = False

    # Write one line of a new node to a file
    def write_band(self, title, url, genre=None):
        if not genre:
            if not self.active_genre:
                raise Exception("You didn't specify or set the active genre!")
            genre = self.active_genre
        elif genre not in self.genres:
            raise Exception("{} is not a valid genre!".format(genre))
        if not self.cache_populated:
            self.populate_cache()

        # Make sure we know what the max node is
        if self.max_node < 0:
            self.find_max_node()
        node_id = self.max_node

        # Check if the band is already in our current genre file
        for band in self.cache[genre]:
            if band[2] == url:
                return

        # Remove everything after a '#' - usually just a subsection of a page. Not helpful
        if url.find('#') != -1:
            url = url[:url.find("#")]

        # Check if the band already has a node ID in another file
        for key in self.cache:
            if key == genre:
                continue
            for band in self.cache[key]:
                if band[2] == url:
                    node_id = band[0]
                    break
            else:
                continue
            break

        # Append the new line to the data file
        with open(self.node_file.format(genre), 'a') as appender:
            if node_id == self.max_node:
                self.max_node += 1
            appender.write("{0}\t{1}\t{2}\n".format(node_id, title, url))

        # Update the cache with the new node
        self.cache[genre].append([node_id, title, url])
        self.valid_urls.add(url)
        self.valid_lowers.add(url.lower())

    # Returns a list of all URLs from all genres
    def get_all_urls(self):
        if not self.cache_populated:
            self.populate_cache()

        return list(self.valid_urls)

    #
    # ### This begins the subset of helper functions ###
    #

    def set_genre(self, genre):
        if genre not in self.genres:
            raise Exception("{} not a valid genre!".format(genre))
        self.active_genre = genre

    # Find the max node from all the data files
    # TODO: Pretty sure this is broken. Idk
    def find_max_node(self):
        max_node = 0
        for genre in self.genres:
            col = self.get_column(genre, 0)
            if len(col) > 0:
                genre_max = max([int(x[0]) for x in col])
                max_node = max(max_node, genre_max)

        self.max_node = max_node

    # Return a list of all elements in column in file
    def get_column(self, genre, column):
        with open(self.node_file.format(genre), 'r') as reader:
            data = reader.read()
        data = data.split('\n')

        if type(column) == int:
            start = column
            end = start + 1
        elif (type(column) == list or type(column) == tuple) and len(column) == 2:
            start = column[0]
            end = column[1]
        else:
            raise Exception("Invalid type supplied for column. Pass in int or [x, y]")

        try:
            column = [x.split('\t')[start:end] for x in data if (len(x) > 0 and x[0] != '#')]
        except ValueError:  # Just creating the file
            column = []

        return column

    def populate_cache(self):
        # Read in from valids files
        self.cache["rock"] = self.get_column("rock", [0, 3])
        self.cache["country"] = self.get_column("country", [0, 3])
        self.cache["metal"] = self.get_column("metal", [0, 3])

        # Populate the (in)valid URLs caches
        self.valid_urls = []
        for genre in self.genres:
            self.valid_urls += [band[2] for band in self.cache[genre]]
        self.valid_urls = set([url for url in self.valid_urls])
        self.valid_lowers = set([url.lower() for url in self.valid_urls])
        self.read_invalid_urls()  # For invalid URLs

        # Mark cache as being populated
        self.cache_populated = True

    # Read in all invalid URLs
    # WARNING: This should only be called by the populate_cache function
    def read_invalid_urls(self):
        with open(self.invalid_urls_file, 'r') as reader:
            data = reader.read()

        data = data.split('\n')
        data = [x.lower() for x in data]
        self.invalid_urls = set(data)


def main():
    file_manager = DataFiles()
    # file_manager.write_invalid_url("/wiki/List_of_heavy_metal_bands")
    # file_manager.write_invalid_url("https://en.wikipedia.org/wiki/Tupac_Shakur")
    print(file_manager.test_valid_url("/wiki/List_of_heavy_metal_bands"))

    for i in range(15000):
        file_manager = DataFiles()
        file_manager.test_valid_url("/wiki/John_Lemon")


if __name__ in "__main__":
    main()


