


var WebSocketServer = require('ws').Server;
var groupMember, joinCode;

function sendLatLng(loc1, loc2) {
  
  const { exec } = require('child_process');
  exec('python geo.py '+loc1+' '+loc2,function(error,stdout,stderr){if(stdout.length >1){
    
    console.log('Contain in the circle or not： ',stdout);

    }else{

    console.log('you don\'t offer args');

    }if(error) {

    console.info('stderr :'+stderr);

    }
    });
}
var getLatLng = new WebSocketServer({
  port: 5003,
  handleProtocols: getLatLng
});
getLatLng.on('connection', function (wsGetLatLng) {

  wsGetLatLng.on('message', function (message) {
   
    let str = new String(message);
    
    let lat = str.split(',', 1);
    
    str = str.replace(lat + ",", "");
    let lng = str;
    sendLatLng(lat,lng);
  })
});


var createGroup = new WebSocketServer({
  port: 5001,
  handleProtocols: createGroup
});
createGroup.on('connection', function (wsCreateGroup) {
  console.log("New Group Create");
  joinCode = getRandomInt(100000);
  wsCreateGroup.send(joinCode);
});



var joinGroup = new WebSocketServer({
  port: 5002,
  handleProtocols: joinGroup
});
joinGroup.on('connection', function (wsJoinGroup) {
  wsJoinGroup.on('message', function (message) {
    console.log('Join Code:' + message);
    if (message == joinCode) {
      wsJoinGroup.send("Join Success");

    }
  })
});
function getRandomInt(max) {
  return Math.floor(Math.random() * max);
}
