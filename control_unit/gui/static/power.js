let bathroomDOM = document.getElementById("bathroom");
let bedroomDOM = document.getElementById("bedroom");
let garageDOM = document.getElementById("garage");
let kitchenDOM = document.getElementById("kitchen");
let living_roomDOM = document.getElementById("living room");
const ON = "ON";
const OFF = "OFF";
function loop(){
    let res = fetch("http://localhost:8000/api/gui/power")
                    .then(response => response.text())
                    .then(json => {console.log(json)})
                    .catch(error => {console.log('error ' + error)});

    // console.log(JSON.parse(JSON.stringify(res)));
    // var jsFormat = res.replaceAll("'", '"')
    // let test = JSON.parse(jsFormat);

    // console.log(res);
    // res2 = JSON.stringify(res);
    // res3 = JSON.parse(JSON.stringify(res));
    // res4 = JSON.parse(res);

    // console.log('keys')
    // console.log(res.keys());

    // console.log('res')
    // console.log(res);
    //
    // for (const [key, value] of Object.entries(res)) {
    //   console.log(`${key}: ${value}`);
    // }
    //
    // console.log('res2');
    // console.log(res2[0]);
    // console.log(res2['0']);
    //
    // for (const [key, value] of Object.entries(res2)) {
    //   console.log(`${key}: ${value}`);
    // }
    //
    // console.log('res3')
    //
    // for (const [key, value] of Object.entries(res3)) {
    //   console.log(`${key}: ${value}`);
    // }

    // console.log('keys4')
    // console.log(res4.keys());
    // console.log(test);
    console.log('res.status: ' + res["status"])
    console.log('res.message: ' + res.message)
    console.log('res.powerstate: ' + res.powerstate)
    if (res.ok){
        let json = res.json();
        console.log('json: ' + json);
        for (let key in json){
            if(json[key]){
                switch(key){
                case 'room1':
                    bathroomDOM.value = "Bathroom(ON)";
                    break;
                case 'room2':
                    bedroomDOM.value = "Bedroom(ON)";
                    break;
                case 'room3':
                    garageDOM.value = "Garage(ON)";
                    break;
                case 'room4':
                    kitchenDOM.value = "Kitchen(ON)";
                    break;
                case 'room5':
                    living_roomDOM.value = "Living room(ON)";
                    break;
                }
            } else {
                switch(key){
                case 'room1':
                    bathroomDOM.value = "Bathroom(OFF)";
                    break;
                case 'room2':
                    bedroomDOM.value = "Bedroom(OFF)";
                    break;
                case 'room3':
                    garageDOM.value = "Garage(OFF)";
                    break;
                case 'room4':
                    kitchenDOM.value = "Kitchen(OFF)";
                    break;
                case 'room5':
                    living_roomDOM.value = "Living room(OFF)";
                    break;
                }
            }
        }
    }
    setTimeout(loop, 5000);
}
setTimeout(loop,0);
