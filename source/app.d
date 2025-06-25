module mobster.main;

import std.stdio;
import mobster.providers;
import std.string;
import std.conv;
import std.array;
// TODO: Add empty to filter so you can keep it lazy.
// TODO: Eventually commit my changes to public.
import tern.algorithm;
import std.getopt;
import std.ascii;

static IProvider[] providers = [];
static Movie[] movies;

void populateMovies(string query)
{
    movies = [];
    foreach (provider; providers)
        movies ~= provider.getMovies(query);
}

Movie findMovie(long id)
{
    if (movies.filter!(x => x.id == id).length > 0)
        return movies.filter!(x => x.id == id)[0];

    foreach (provider; providers)
    {
        Movie ret = provider.getMovie(id);
        if (ret.id == id)
            return ret;
    }

    return Movie.init;
}

void main(string[] args)
{
    // TODO: this obviously does not take arguments yet
    if (providers == [])
        providers ~= new YTS();

    writeln("Enter search term(s): ");
    string query = stdin.readln().strip;
    if (query.empty)
    {
        writeln("No query entered, exiting.");
        return;
    }

    writeln("Searching for: ", query);
    populateMovies(query);

    if (movies.length == 0)
    {
        writeln("No movies found.");
        return;
    }

    writeln("\nFound ", movies.length, " movies:\n");
    foreach (i, m; movies)
    {
        writeln(" [", i, "] ", m.title, " (ID: ", m.id, ")");
    }

    writeln("\nSelect a movie index: ");
    auto input = stdin.readln().strip;
    auto idx = input.to!long;
    if (idx >= movies.length)
    {
        writeln("Invalid selection, exiting.");
        return;
    }

    auto selected = movies[idx];
    writeln("\nFetching details for: ", selected.title);
    auto details = findMovie(selected.id);

    writeln("\nAvailable torrents:");
    foreach (t; details.torrents)
    {
        writeln(" • Quality: ", t.quality,
            ", Size: ", t.size,
            ", Hash: ", t.hash);
    }
}
