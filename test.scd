
// Quarks.install( "OscGroupClient", checkoutIfNeeded: false);
// Quarks.install( "ProcessTools", checkoutIfNeeded: false);
// Quarks.install( "SafetyNet", checkoutIfNeeded: false);
// Quarks.install( "MP3", checkoutIfNeeded: false);
// Quarks.install("Ctk", checkoutIfNeeded: false);
// "Hello world".postln;
// "/supercollider/install/test2.scd".load

// thisProcess.recompile();

(
    OSCdef.new(
        \test,
        {
            arg msg, time, addr, port;

            var stationString;

            stationString = msg[1];
            ( "stationString is " + stationString ).postln;
            // Reading into a buffer is possible, but you *must* specify the number of (uncompressed) frames to read.

            // m = MP3(stationString, \readurl);
            // m.start;
            // b= Buffer.readChannel(s, m.fifo, 0, 100000, channels:[0]);

            // x = Synth.new(\grain_resonance);

        },
        '/start'
    )

)