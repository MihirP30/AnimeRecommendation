import csv
import heapq
from typing import Any


class _Vertex:
    """A vertex in a graph."""
    item: Any
    neighbours: dict["_Vertex", int]  # Stores neighbors with weights

    def __init__(self, item: Any) -> None:
        """Initialize a new vertex with the given item."""
        self.item = item
        self.neighbours = {}


class Graph:
    """A graph data structure."""
    _vertices: dict[Any, _Vertex]
    popularity: dict[Any, int]  # Store popularity of each anime

    def __init__(self) -> None:
        """Initialize an empty graph."""
        self._vertices = {}
        self.popularity = {}

    def add_vertex(self, item: Any, popularity: int) -> None:
        """Add a vertex with the given item and store its popularity."""
        if item not in self._vertices:
            self._vertices[item] = _Vertex(item)
            self.popularity[item] = popularity  # Store popularity

    def add_edge(self, item1: Any, item2: Any, weight: int) -> None:
        """Add a weighted edge between two vertices."""
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]
            v1.neighbours[v2] = weight
            v2.neighbours[v1] = weight

    def find_closest_anime(self, start: Any) -> Any:
        """Find the closest anime recommendation using Dijkstra's algorithm with popularity as a tiebreaker."""
        if start not in self._vertices:
            print("Anime not found in the dataset.")
            return None

        pq = [(0, start)]  # Priority queue with (distance, anime_id)
        distances = {vertex: float('inf') for vertex in self._vertices}
        distances[start] = 0
        visited = set()

        while pq:
            current_distance, current_anime = heapq.heappop(pq)

            if current_anime in visited:
                continue

            visited.add(current_anime)

            for neighbour, weight in self._vertices[current_anime].neighbours.items():
                if neighbour.item not in visited:
                    new_distance = current_distance + weight
                    if new_distance < distances[neighbour.item]:
                        distances[neighbour.item] = new_distance
                        heapq.heappush(pq, (new_distance, neighbour.item))

        # Find the closest anime with the shortest weighted distance
        closest_anime_candidates = []
        min_distance = float('inf')

        for anime, distance in distances.items():
            if anime != start and distance < min_distance:
                min_distance = distance
                closest_anime_candidates = [anime]
            elif anime != start and distance == min_distance:
                closest_anime_candidates.append(anime)

        # If multiple anime have the same closeness, return the most popular one (excluding popularity = 0)
        if closest_anime_candidates:
            return min(
                closest_anime_candidates,
                key=lambda anime: self.popularity.get(anime, float('inf')) if self.popularity.get(anime, 0) != 0 else float('inf')
            )

        return None


def build_anime_graph(csv_filename: str) -> tuple[Graph, dict[str, str]]:
    """Read AnimeList.csv and build a graph with weighted edges."""
    anime_graph = Graph()
    anime_data = {}
    genre_to_anime = {}
    studio_to_anime = {}
    title_to_id = {}

    with open(csv_filename, encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            anime_id = row["anime_id"]
            title = row["title"]
            genres = row["genre"].split(", ") if row["genre"] else []
            studio = row["studio"]
            related = row["related"].split(", ") if row["related"] else []
            popularity = int(row["popularity"]) if row["popularity"].isdigit() else float('inf')

            anime_graph.add_vertex(anime_id, popularity)
            anime_data[anime_id] = (title, genres, studio, related)
            title_to_id[title.lower()] = anime_id

            for genre in genres:
                if genre not in genre_to_anime:
                    genre_to_anime[genre] = set()
                genre_to_anime[genre].add(anime_id)

            if studio:
                if studio not in studio_to_anime:
                    studio_to_anime[studio] = set()
                studio_to_anime[studio].add(anime_id)

        for anime_list in genre_to_anime.values():
            anime_list = list(anime_list)
            for i in range(len(anime_list)):
                for j in range(i + 1, len(anime_list)):
                    anime_graph.add_edge(anime_list[i], anime_list[j], 2)

        for anime_list in studio_to_anime.values():
            anime_list = list(anime_list)
            for i in range(len(anime_list)):
                for j in range(i + 1, len(anime_list)):
                    anime_graph.add_edge(anime_list[i], anime_list[j], 3)

        for anime_id, (_, _, _, related) in anime_data.items():
            for related_anime in related:
                if related_anime in anime_data:
                    anime_graph.add_edge(anime_id, related_anime, 1)

    return anime_graph, title_to_id


if __name__ == "__main__":
    csv_file = "AnimeList.csv"  # Update with actual path
    anime_graph, title_to_id = build_anime_graph(csv_file)

    anime_name = input("Enter an anime name for recommendations: ").strip().lower()
    if anime_name in title_to_id:
        closest_anime_id = anime_graph.find_closest_anime(title_to_id[anime_name])
        if closest_anime_id:
            print(f"Recommended Anime: {closest_anime_id}")
        else:
            print("No recommendations found.")
    else:
        print("Anime not found in the dataset.")

    exit()
