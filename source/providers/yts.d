module mobster.providers.yts;

import mobster.providers;
import std.net.curl;
import std.json;
import std.uri : encode;
import std.conv;

class YTS : IProvider
{
    /// Base URL for the YTS API
    enum string API = "https://yts.mx/api/v2";

    /// Searches YTS for movies matching `query`
    /// Returns an array of MovieInfo
    Movie[] getMovies(string query)
    {
        Movie[] movies;
        string url = API~"/list_movies.json?query_term="~query.encode;
        JSONValue root = parseJSON(get(url));

        if (root["status"].str != "ok")
            return movies;

        JSONValue data = root["data"]["movies"];
        if (data.type != JSONType.array)
            return movies;

        foreach (u; data.array)
        {
            movies ~= Movie(
                u["id"].integer,
                u["title_long"].str
            );

            JSONValue tors = u["torrents"];
            if (tors.type == JSONType.array)
            {
                foreach (v; tors.array)
                {
                    movies[$-1].torrents ~= Torrent(
                        v["quality"].str,
                        v["size"].str,
                        v["hash"].str
                    );
                }
            }
        }

        return movies;
    }

    /// Fetches a single movie by its YTS ID
    Movie getMovie(long id)
    {
        Movie movie;
        string url = API~"/movie_details.json?movie_id="~id.to!string;
        JSONValue root = parseJSON(get(url));

        if (root["status"].str != "ok")
            return movie;

        JSONValue u = root["data"]["movie"];
        if (u.type == JSONType.null_)
            return movie;

        movie = Movie(
            u["id"].integer,
            u["title_long"].str
        );

        JSONValue tors = u["torrents"];
        if (tors.type == JSONType.array)
        {
            foreach (v; tors.array)
            {
                movie.torrents ~= Torrent(
                    v["quality"].str,
                    v["size"].str,
                    v["hash"].str
                );
            }
        }

        return movie;
    }
}
