# fourteen\_

... is a mutated global web radio streamer. It is an experiment exploring decomposition, both spatial and sonic.

It's core setup is:

- [SuperCollider](https://supercollider.github.io/)

  - Used as a streamer service, processing the incoming webradio buffers.

- [Flask](https://flask.palletsprojects.com/en/1.1.x/)

  - Is the backend API, managing the interaction between SuperCollider and the frontend.

- [d3.js](https://d3js.org/)

  - Handles the frontend graphics.

## Installing

Requires [docker](https://www.docker.com/). Due to pyOSC3 requiring a static ip to communicate with the SuperCollider server, a docker network needs to be created first. E.g.

```
docker network create --subnet 10.5.0.0/24 local_network_dev
```

Then, navigate to `docker` folder and run

```
docker-compose up
```

### SuperCollider

The sound module uses granular synthesis on the incoming web radio streams. It consists of three `SynthDef`'s. One uses the stream to generate a synth like drone pitch shifted using `midiratio`. The main synth uses a fixed grain duration of 0.2 seconds with a randomly shifting grain position. The final synth acts as 'rhythm' using `Dust` to generate random impulses for grain duration.

The container running SuperCollider is running an audio streaming server using icecast and darkice. It was adapted from [here](https://hub.docker.com/r/rukano/supercollider).

### Flask

The backend API is build using Flask-python. It handles web radio queue requests and manages interactions with the postgres database storing user requests and manages adding random stations for streaming. It uses web radio data from ... To be able to deploy the project as a quick demo on platforms such as ngrok (free tier) all routing (including the streaming server and the fronted page) is handled through the flask app.

### D3.js

The frontend webpage uses d3 to load a world geojson map and handle user requests to the backend.
