
s.boot;

(
x = OSCFunc( { | msg, time, addr, port |
    var stationString;

    stationString = msg[1];
    ( "stationString is " + stationString ).postln;
    // Reading into a buffer is possible, but you *must* specify the number of (uncompressed) frames to read.
    m = MP3(stationString, \readurl);
    m.start;
    b= Buffer.readChannel(s, m.fifo, 0, 100000, channels:[0]);

        
    y = SynthDef("grain_resonance", { |grain_pos=1, bufnum=0, room=0.9, damp = 0.9|
        var sig;
        sig = GrainBuf.ar(
            2,
            Impulse.ar({ExpRand(60,60.5)}!12),
            LFNoise1.kr(1!12).exprange(0.0002,0.5),
            b,
            1,
            grain_pos,
            2,
            0,
            -1,
            512
        );
        sig = LPF.ar(sig, SinOsc.kr(LFNoise1.ar(0.1).range(0.1,1)).range(20, 10000)); 
        sig = Splay.ar(sig);
        sig = FreeVerb.ar(sig,room,damp)!12;
        sig = sig* 0.4;
        Out.ar(0, sig);
    }).play(s, [\bufnum, b], addAction:\addToTail);
    

    
    x = SynthDef("grain_main", { |grain_dur=0.2, bufnum=0|
        var sig;
        sig = GrainBuf.ar(
            2,
            Impulse.ar(10),
            grain_dur,
            bufnum,
            1,
            LFNoise1.ar(0.1).range(0,1),
            2,
            0,
            -1,
            512);
        Out.ar(0, sig);
    }).play(s, [\bufnum, b], addAction:\addToTail);

}, "/start" );

z = OSCFunc( { | msg, time, addr, port |
    var stationString;

    stationString = msg[1];
    ( "I am " + stationString ).postln;
    b.close; 
    b.free;
    m.finish;


}, "/stop" );

)
