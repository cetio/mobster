# Mobster

> [!WARNING]
> This is an educational tool, and I assume no legal liability in the event that it is misused.
>
> By using Mobster you implicitly agree that, in the event a federal or local authority were to question you, you are to be hanged in the gallows.

A tool for easily accessing and watching movies, shows, and more from various different providers modularly from the commandline.

Mobster was initially intended to be a script, but due to logistical constraints (Python being impossible to use at scale,) it has transitioned to D.
The original script will remain available until the new version is superior.

## Features

- Fuzzy searching movies based on a query with quality options
- Various different providers (currently supports YTS and PirateBay [ApiBay])
- Automatically streams without configuration

### Why Mobster?

Mobster is intended to be significantly more reliable than alternatives, such as Lobster, and provide seamless supports
for various different providers without any hitches.

Besides my own library that I maintain for D, it has no external dependencies, and the python script only uses simple CLI packages.

## Roadmap

- [ ] Tor relay for privacy/"ethical" reasons
- [ ] Continue and track watched movies based on progress
- [ ] Render coverart and movie details (metadata)
- [ ] Godzilla mode
- [ ] Allow for using arguments to find and play or retrieve data
- [ ] Rofi integration

## License

Mobster is licensed under the [AGPL-3.0 License](LICENSE.txt)
