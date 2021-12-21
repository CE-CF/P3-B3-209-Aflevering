#include <Arduino.h>
//#include <cstdio>
//#include <string.h>
#include <Ticker.h>


// ----------------------
// Global DHT variables
#include <stdbool.h>
#include <DHTesp.h>
#define DHTPIN 25
DHTesp sensor;
TempAndHumidity sensData;
bool newTemp = false;
Ticker tempTicker;
TaskHandle_t tempTaskHandle = NULL;
bool         tasksEnabled = false;

void initSensors(void);
void triggerGetTemp(void);
void tempTask(void *param_ptr);

// ----------------------
// Motion sensor
#define PIRPIN 33
bool newMotion = false;
TaskHandle_t pirTaskHandle = NULL;

void triggerGetPir(void);
void pirTask(void *param_ptr);



// ----------------------
// Networking related
#include <WiFi.h>
#include <http.h>

#define SSID "DetSmarteHus"
#define PASS "greatput"
int status = WL_IDLE_STATUS;

// HTTP api 
#define HOST "control-unit.local"
#define API_PATH "/api/sensor/"
#define SENSID "Kitchen"
#define ENDPOINT API_PATH SENSID

//#define __TEST
#ifdef __TEST
IPAddress server(192, 168, 63, 165);
#else
IPAddress server;
#endif
int port = 8000;

WiFiClient client;

byte mac[6];
void sendPostReq(char *data);
void sendData(void);


void setup() {
  Serial.begin(9600);
  while(!Serial){}

  delay(1500);
  initSensors();

  // while (status != WL_CONNECTED){
  //   Serial.println("Connecting to " SSID);
  //   status = WiFi.begin(SSID, PASS);
  //   delay(5000);
  // }
  char mac_str[60];
  sprintf(mac_str, "%2.2x:%2.2x:%2.2x:%2.2x:%2.2x:%2.2x", mac[0],mac[1],mac[2],mac[3],mac[4],mac[5]);
  WiFi.macAddress(mac);
#ifndef __TEST
  server = WiFi.gatewayIP();
#endif
  // Print debug network info
  Serial.println("-- Connected --");
  Serial.print("MAC Addr: "); Serial.println(mac_str);
  Serial.print("IP Addr: "); Serial.println(WiFi.localIP());
  Serial.print("Gateway: "); Serial.println(WiFi.gatewayIP());
  Serial.print("Target Server: "); Serial.println(server);


}

void loop() {
  sendData();

  // Serial.print("Motion state: "); Serial.println(newMotion);
}


void triggerGetTemp() {
  if (tempTaskHandle != NULL){
    xTaskResumeFromISR(tempTaskHandle);
  }
}

void tempTask(void *param_ptr){
  while(1){
    if (tasksEnabled && !newTemp){
      sensData = sensor.getTempAndHumidity();
      newTemp = true;
    }
    vTaskSuspend(NULL);
  }
}

void initSensors(void){
  sensor.setup(DHTPIN, DHTesp::DHT11); // Temp and humidity module
  pinMode(PIRPIN, INPUT); // Pir sensor

  xTaskCreatePinnedToCore(tempTask,"temptask ",4000,NULL,5,&tempTaskHandle,1);
  //xTaskCreatePinnedToCore(pirTask,"pirtask ",4000,NULL,5,&pirTaskHandle,1);

  if(tempTaskHandle == NULL){
    Serial.println("[error] failed to create temp task");
  }
  else{
    tempTicker.attach(3, triggerGetTemp);
  }

  tasksEnabled = true;
}

void sendPostReq(char *data){
  // char endpoint[60];
  // sprintf(endpoint,
  //         API_PATH "%2.2x:%2.2x:%2.2x:%2.2x:%2.2x:%2.2x",
  //         mac[0],mac[1],mac[2],mac[3],mac[4],mac[5]);

  Request *req = createRequest("POST", ENDPOINT, data);
  
  ADD_HEADER(req, "Content-type", "application/x-www-form-urlencoded")
  ADD_HEADER(req, "Connection", "close")
  ADD_HEADER(req, "Host", HOST)

    // Serial.println(req->headers->head->name)
    // Serial.println(req->headers->head->value);
    // Serial.println(req->headers->head->nxt_ptr->name);
    // Serial.println(req->headers->head->nxt_ptr->value);
    
  char str[255];
  reqtostr(req, str);

  if (client.connect(server, port)){
    char _str[255];
    sprintf(_str, "Connected to %s");
    Serial.println("Sending request:");
    client.println(str);
  }
  Serial.println(str);
  
  delRequest(req);
}

void sendData(void){
  int pirState = digitalRead(PIRPIN);
  if (newTemp || (pirState && newTemp)){
    char data[38];
    sprintf(data, "temp=%2.1f&hum=%2.1f&mot=%d",sensData.temperature, sensData.humidity, pirState);
    
    sendPostReq(data);
    
    newTemp = false;
  }
}
