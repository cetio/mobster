module mobster.providers.apibay;

import mobster.providers;
import std.net.curl : get;
import std.json : parseJSON, JSONValue, JSONType;
import std.conv : to;
import tern.algorithm;

class ApiBay : IProvider
{
    /// Base URL for the Pirate Bay JSON API
    enum string API = "https://apibay.org";

    /// Searches for torrents matching `query`. Each result becomes its own Movie.
    Movie[] getMovies(string query)
    {
        Movie[] movies;
        // q.php returns an array of objects with string fields
        string url = API~"/q.php?q="~query;
        JSONValue root = parseJSON(get(url));

        if (root.type != JSONType.array)
            return movies;

        foreach (entry; root.array)
        {
            // parse the string-typed id into a long
            long id = entry["id"].str.to!long;
            // TODO: ../../.dub/packages/tern/0.2.27/tern/source/tern/algorithm/mutation.d(98,12): Error: undefined identifier `ret`, did you mean template `get(K, V)(inout(V[K]) aa, K key, lazy inout(V) defaultValue)`?
            //    return ret.value;
            //           ^
            Movie m = Movie(
                id,
                // TODO: Make more human readable, especially stripping file names.
                entry["name"].str
            );

            m.torrents = [Torrent(
                // TODO: This is incredibly terrible and should not only be modularized but also improved.
                m.title.contains("480p") ? "480p" :
                m.title.contains("720p") ? "720p" :
                m.title.contains("1080p") ? "1080p" :
                m.title.contains("1440p") ? "1440p" :
                m.title.contains("2K") ? "2K" :
                m.title.contains("4K") ? "4K" : "Unknown",
                // TODO: Convert to human readable units.
                entry["size"].str,
                entry["info_hash"].str
            )];

            movies ~= m;
        }
        return movies;
    }

    /// Fetches a single torrent by its ID.
    Movie getMovie(long id)
    {
        Movie movie;
        // use the single­torrent endpoint t.php
        string url = API ~ "/t.php?id=" ~ id.to!string;
        JSONValue root = parseJSON(get(url));

        // t.php returns a single JSON object
        if (root.type != JSONType.object)
            return movie;

        movie = Movie(
            id,
            root["name"].str
        );

        movie.torrents = [Torrent(
            "Unknown",
            root["size"].str,
            root["info_hash"].str
        )];

        return movie;
    }
}
