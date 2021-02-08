
s.boot;

(
m = OSCFunc( { | msg, time, addr, port | 
    var stationString, grain_main_dur;

    stationString = msg[1];
    grain_main_dur = msg[2];
    ( "stationString is " + stationString ).postln;

    protect {

        try {  b= Buffer.readChannel(s, "app/SuperCollider/out.wav", channels:[0]); }  { "readBufferError".postln;};

    
        
        y = SynthDef(\grain_resonance, { |grain_pos=1,trig=60, bufnum=0, room=0.9, damp = 0.9, amp=0.3|
            var sig, env;
            sig = GrainBuf.ar(
                2,
                Impulse.ar({ExpRand(trig,60.5)}!12),
                LFNoise1.kr(1!12).exprange(0.0002,0.1),
                b,
                -72.midiratio,
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
            env = Line.kr(1, 0, 30, doneAction: 2); // fade in the effect
            sig = sig* amp * env;
            Out.ar(0, sig);
        }).play(s, [\bufnum, b], addAction:\addToTail);
            

        x = SynthDef("grain_main", { |grain_dur=0.2, bufnum=0, amp=0.3|
            var sig, env;
            sig = GrainBuf.ar(
                2,
                Impulse.ar(grain_main_dur),
                grain_dur,
                b,
                1,
                LFNoise1.ar(0.1).range(0,1),
                2,
                0,
                -1,
                512);
            5.do({ sig = AllpassN.ar(sig, 0.7, [0.1.rand, 0.5.rand], 2); });
            env = Line.kr(1, 0, 30, doneAction: 2); // fade in the effect
            Out.ar(0, sig*amp*env);
        }).play(s, [\bufnum, b], addAction:\addToTail);

        
        z = SynthDef("grain_rhythm", { |grain_dur=0.2, bufnum=0, amp=0.3|
            var sig, env;
            sig = GrainBuf.ar(
                2,
            Dust.ar(1),
                LFNoise1.ar(0.1).range(0.5,1),
                b,//LFNoise1.ar(0.1).range(0.2,0.3),
                1,
                LFNoise1.ar(1).range(0.3,1),
                2,
                0,
                -1,
                512);
        // env = Env.adsr(0.001, 0.4, 0.5, 0.1);
        env = Line.kr(0.5, 0, 30, doneAction: 2); // fade in the effect
        sig = LPF.ar(sig, LFNoise1.ar(0.1).range(1000,2000));
            Out.ar(0, sig*amp*env);
        }).play(s, [\bufnum, b], addAction:\addToTail);
    } {
        b.close; 
    };
}, "/start" );

o = OSCFunc( { | msg, time, addr, port |
    var stationString;

    stationString = msg[1];

    protect {
    ( "I am " + stationString ).postln;

    } {
        ( "There is an error " + stationString ).postln;
    };



}, "/stop" );

)
