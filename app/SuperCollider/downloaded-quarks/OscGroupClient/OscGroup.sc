OscGroupClient {
	var serveraddress, username, password, groupname, grouppassword, serverport, localtoremoteport,
		localtxport, localrxport, responders, peerCheckers, <peers, <pid, <netAddr;
	classvar <>program;

	*new {arg serveraddress, username, password, groupname, grouppassword, serverport = 22242,
			localtoremoteport = 22243, localtxport = 22244, localrxport;
		^super.newCopyArgs(serveraddress, username, password, groupname, grouppassword, serverport,
			localtoremoteport, localtxport, localrxport).init;
		}

	*initClass {
		program = "./OscGroupClient"
		}

	init {
		responders = IdentityDictionary.new;
		localrxport.isNil.if({
			localrxport = NetAddr.langPort;
			});
		peers = Set();
		peerCheckers = IdentityDictionary.new;
		}

	join {
		var command;

		(program.pathExists == false).if({
			("'" ++ program ++ "' not found, maybe you forgot to set OscGroupClient.program to the OscGroupClient binary?").postln;
			^false;
		});

		command = [program, serveraddress, serverport, localtoremoteport, localtxport, localrxport,
			username, password, groupname, grouppassword].collect({|i|  i.asString });

		pid = command.unixCmd;

		netAddr = NetAddr("localhost", localtxport);

		// Sets up a responder for ping messages and keeps track of all peers
		// using 10 seconds timeout
		this.addResp('/groupclient/ping', {arg msg, time, addr, recvPort;
			var peerName = msg[1];
			peers.add(peerName);
			peerCheckers[peerName].isNil.if({
				peerCheckers.add(peerName -> Task({
					// timeout of 10 seconds to check for peer's ping
					10.wait;
					peerCheckers[peerName] = nil;
					peers.remove(peerName);
				});
			)});
			peerCheckers[peerName].stop;
			peerCheckers[peerName].play(doReset: true);
		});

		ShutDown.add({("kill" + pid).systemCmd});
		}

	close {
		var keys;
		("kill" + pid).systemCmd;
		pid = nil;
		keys = responders.keys;
		keys.do({arg id; this.removeResp(id)});
		responders = IdentityDictionary.new;
		}

	sendMsg { arg ... msg;
		msg[0] = this.formatSymbol(msg[0]);
		netAddr.sendMsg(*msg);
	}

	sendMsgArray {arg symbol, array;
		symbol = this.formatSymbol(symbol);
		netAddr.sendMsg(symbol, *array)
		}

	addResp { arg id, function;
		pid.notNil.if({
			// there are two ways to pass in the symbol id... fix it here
			id = this.formatSymbol(id);
			responders[id].notNil.if({this.removeResp(id)});
			responders.add(id -> OSCFunc(function, id, recvPort: localrxport));
			}, {
			"You must register your client on an OscGroupServer before you add a responder".warn
			})
		}

	removeResp {arg id;
		id = this.formatSymbol(id);
		responders[id].free;
		responders[id] = nil;
		}

	formatSymbol {arg symbol;
		var str;
		str = symbol.asString;
		(str[0] == $/).if({
			^str.asSymbol;
			}, {
			^("/"++str).asSymbol
			})
		}

}
