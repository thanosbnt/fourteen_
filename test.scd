
Quarks.install( "OscGroupClient", checkoutIfNeeded: false);
Quarks.install( "ProcessTools", checkoutIfNeeded: false);
Quarks.install( "SafetyNet", checkoutIfNeeded: false);
Quarks.install( "MP3", checkoutIfNeeded: false);
Quarks.install("Ctk", checkoutIfNeeded: false);
"Hello world".postln;
"/supercollider/install/test2.scd".load

thisProcess.recompile();

