
s.boot;

(
SynthDef( \sin, { | amp = 0.01, freq = 333, trig = 1 |
    var env, sig;
    env = EnvGen.kr( Env.asr( 0.001, 0.9, 0.001 ), trig, doneAction: 0 );
    sig = LFTri.ar( [ freq, freq * 0.999 ], 0.0, amp ) * env;
    Out.ar( [ 0 ], sig * 0.6 );
}).add;


h = Synth( \sin, [ \amp, 0.4 ] );





x = OSCFunc( { | msg, time, addr, port |
    var stationString;

    stationString = msg[1];
    ( "stationString is " + stationString ).postln;
    p =  stationString;
    // b = Buffer.read(s, p);

    // x = SynthDef(\help_Buffer, { arg out = 0, bufnum;
    //     Out.ar( out,
    //         FreeVerb.ar(PlayBuf.ar(2, bufnum, BufRateScale.kr(bufnum)* (-7.midiratio), doneAction:2), 0.7,0.4, 0.9) ! 2
    //     )
    // }).play(s,[\bufnum, b]);

    // x = SynthDef(\help_Buffer, { arg out = 0, bufnum;
    //     Out.ar( out,
    //         FreeVerb.ar(PlayBuf.ar(2, bufnum, BufRateScale.kr(bufnum)* (-15.midiratio), doneAction:2), 0.7,0.9, 0.9) ! 2
    //     )
    // }).play(s,[\bufnum, b]);

    ~stream = MP3.new(p, \readurl);
    ~stream.start;
    b = Buffer.cueSoundFile(s, ~stream.fifo, 0, 2);

    x = SynthDef(\help_mp3, { |bufnum = 0, amp = 1, dur=0.09, room=0.9, damp=0.5|
        var stream, sig;


        stream = DiskIn.ar(2, bufnum);
        stream = GrainIn.ar(1,
            Impulse.kr(10), dur, stream,0
        );
        sig = Pan2.ar(stream, 0, amp);
        sig = FreeVerb.ar(sig,room,damp)!2;
        sig = Splay.ar(sig);
        Out.ar(0, sig);
    }).play(s,[\bufnum, b.bufnum], addAction:\addToTail);




    // x = Synth("help_mp3_01", [\bufnum, b.bufnum], addAction:\addToTail);


    // s.record(path: "/home/sclang/.local/share/SuperCollider/out.wav", duration: 5);

}, "/print" );

)
