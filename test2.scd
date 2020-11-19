
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

        
    // y = SynthDef("grain_resonance", { |grain_pos=1, bufnum=0, room=0.9, damp = 0.9|
    //     var sig;
    //     sig = GrainBuf.ar(
    //         2,
    //         Impulse.ar({ExpRand(60,60.5)}!12),
    //         LFNoise1.kr(1!12).exprange(0.0002,0.5),
    //         b,
    //         1,
    //         grain_pos,
    //         2,
    //         0,
    //         -1,
    //         512
    //     );
    //     sig = LPF.ar(sig, SinOsc.kr(LFNoise1.ar(0.1).range(0.1,1)).range(20, 10000)); 
    //     sig = Splay.ar(sig);
    //     sig = FreeVerb.ar(sig,room,damp)!12;
    //     sig = sig* 0.4;
    //     Out.ar(0, sig);
    // }).play(s, [\bufnum, b], addAction:\addToTail);
    
    y = SynthDef("grain_resonance", { |grain_pos=1,trig=60, bufnum=0, room=0.9, damp = 0.9, amp=1|
        var sig;
        sig = GrainBuf.ar(
            2,
            Impulse.ar({ExpRand(trig,60.5)}!12),
            LFNoise1.kr(1!12).exprange(0.0002,0.1),
            b,
            1,
            LFNoise1.ar(0.004).range(0.01,1),
            2,
            0,
            -1,
            512
        );
        sig = LPF.ar(sig, SinOsc.kr(LFNoise1.ar(1).range(0.01,0.05)).range(20, 10000));
        sig = Splay.ar(sig);
        // sig = FreeVerb.ar(sig,room,damp)!12;
        5.do({ sig = AllpassN.ar(sig, 0.3, [0.1.rand, 0.5.rand], 2); });
        // sig = JPverb.ar(sig,room,damp);

        sig = sig* amp;
        Out.ar(0, sig);
    }).play(s, [\bufnum, b], addAction:\addToTail);
    


    
    x = SynthDef("grain_main", { |grain_dur=0.2, bufnum=0, amp=1|
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
        5.do({ sig = AllpassN.ar(sig, 0.7, [0.1.rand, 0.5.rand], 2); });
        Out.ar(0, sig*amp);
    }).play(s, [\bufnum, b], addAction:\addToTail);
    


}, "/start" );

z = OSCFunc( { | msg, time, addr, port |
    var stationString;

    stationString = msg[1];
    (
    fork {
        var n;
        n=1;
        100.do {
            x.set(\amp, n);
            y.set(\amp, n);
            n=n-0.01;
            n.postln;
            0.1.wait;
        };
        "This is it.".postln;
        x.free();
    }
    );

    ( "I am " + stationString ).postln;

    b.play;
    // b.close; 
    // b.free;
    // m.finish;


}, "/stop" );

)
