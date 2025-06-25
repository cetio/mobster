module mobster.providers;

public import mobster.providers.yts;
public import mobster.providers.apibay;

/// Represents a single torrent entry
struct Torrent
{
    string quality;
    string size;
    string hash;
}

/// Represents a single movie entry with its torrents
struct Movie
{
    long id;
    string title;
    Torrent[] torrents;
}

interface IProvider
{
    enum string API = "invalid";

    Movie[] getMovies(string query);
    Movie getMovie(long id);
}
