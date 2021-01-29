- changed sc port to udp to listen to python
- libdev-jack no sound; changed to libjack-jackd2-dev
- quarks are instaled duting docker compose
- needed to give static ip to sc container due to pyOSC3; create docker network create --subnet 10.5.0.0/24 local_network_dev first

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
    var pyFreq;

    pyFreq = msg[1];
    ( "freq is " + pyFreq ).postln;
    // Synth( \sin, [ \amp, 0.4 ] ).set( \freq, pyFreq );
   	p =  pyFreq;
	// b = Buffer.read(s, p);

	// x = SynthDef(\help_Buffer, { arg out = 0, bufnum;
	//    Out.ar( out,
	//        FreeVerb.ar(PlayBuf.ar(2, bufnum, BufRateScale.kr(bufnum)* (-7.midiratio), doneAction:2), 0.7,0.4, 0.9) ! 2
	//    )
	// }).play(s,[\bufnum, b]);


	SynthDef("help_mp3_01", { |bufnum = 0, amp = 1, dur=0.09, room=0.9, damp=0.5|
	    var stream, sig;
	    stream = DiskIn.ar(2, bufnum);
		stream = GrainIn.ar(1,
			Impulse.kr(10), dur, stream,0
		);
		sig = Pan2.ar(stream, 0, amp);
		sig = FreeVerb.ar(sig,room,damp)!2;
		sig = Splay.ar(sig);
	    Out.ar(0, sig);
	}).load(s);

	~stream = MP3.new("http://edge-bauermz-01-cr.sharp-stream.com/magic1548.mp3", \readurl);
	~stream.start;
	b = Buffer.cueSoundFile(s, ~stream.fifo, 0, 2);
	x = Synth("help_mp3_01", [\bufnum, b.bufnum], addAction:\addToTail);

	//x = SynthDef(\help_Buffer, { arg out = 0, bufnum;
	//    Out.ar( out,
	//        FreeVerb.ar(PlayBuf.ar(2, bufnum, BufRateScale.kr(bufnum)* (-15.midiratio), doneAction:2), 0.7,0.9, 0.9) ! 2
	//    )
	//}).play(s,[\bufnum, b]);

    s.record(path: "/home/sclang/.local/share/SuperCollider/out.wav", duration: 5);

}, "/print" );




)
